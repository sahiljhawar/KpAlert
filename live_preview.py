"""Live-reloading local preview server for kp_alert_email.html.j2.

Watches kp_alert_email.html.j2 and render_preview.py (the sample data +
render logic) for changes, re-renders automatically, and auto-refreshes
the browser tab. Editing kp_index_monitor.py's alert-building logic is
not picked up, since it isn't invoked here -- update the CTX values in
render_preview.py to mirror any changes you make there.

Usage: python3 live_preview.py [port]   (default port 8935)
"""

import functools
import http.server
import importlib
import socketserver
import sys
import threading
import time
from pathlib import Path

import render_preview

ROOT = Path(__file__).resolve().parent
WATCHED = [ROOT / "kp_alert_email.html.j2", ROOT / "render_preview.py"]
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8935

_lock = threading.Lock()
_version = 0
_html = ""

RELOAD_SNIPPET = """
<script>
(function() {
  let last = null;
  setInterval(async () => {
    try {
      const r = await fetch('/__version');
      const v = await r.text();
      if (last !== null && v !== last) location.reload();
      last = v;
    } catch (e) {}
  }, 500);
})();
</script>
</body>
"""


def _mtimes():
    return tuple(p.stat().st_mtime for p in WATCHED)


def _rerender():
    global _html
    importlib.reload(render_preview)
    _html = render_preview.render()


def _watch_loop():
    global _version
    with _lock:
        _rerender()
    last = _mtimes()
    while True:
        time.sleep(0.5)
        current = _mtimes()
        if current != last:
            last = current
            try:
                with _lock:
                    _rerender()
                    _version += 1
                print("re-rendered")
            except Exception as e:
                print(f"render error: {e}")


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/__version":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            with _lock:
                self.wfile.write(str(_version).encode())
            return
        if self.path in ("/", "/test_render.html"):
            with _lock:
                body = _html.replace("</body>", RELOAD_SNIPPET)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass


def main():
    threading.Thread(target=_watch_loop, daemon=True).start()
    handler = functools.partial(Handler, directory=str(ROOT))
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), handler) as httpd:
        print(f"Live preview: http://localhost:{PORT}/  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
