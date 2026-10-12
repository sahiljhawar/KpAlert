"""Render kp_alert_email.html.j2 with sample data for local preview.

Usage: python3 render_preview.py
Writes test_render.html, viewable directly in a browser.
"""

from pathlib import Path

from jinja2 import Template

TEMPLATE_PATH = Path(__file__).resolve().parent / "kp_alert_email.html.j2"

CTX = {
    "subject": "Alert: STRONG STORM CONDITIONS predicted with probability ≥ 65%.",
    "issued": "08:27 UTC, 16 Sep 2026",
    "level_code": "G5",
    "level_name": "Strong Storm",
    "headline": "Geomagnetic activity may reach Strong Storm conditions (Kp ≥ 7)",
    "lede": (
        "From 12:00 (UTC) 15.09.2026 to 15:00 (UTC) 15.09.2026, Geomagnetic Activity can reach "
        "STRONG STORM CONDITIONS (Kp ≥ 7) with probability of ~65%."
    ),
    "current_conditions": "MODERATE CONDITIONS at 06:00 (UTC) 16.09.2026",
    "forecast_caption": None,
    "storm_rows": [
        {"time": "16.09.2026 08:27", "p67": "40%", "p78": "20%", "p8": "5%"},
        {"time": "16.09.2026 11:27", "p67": "35%", "p78": "25%", "p8": "8%"},
    ],
    "activity_current_code": "G3",
    "aurora": {
        "note": "Kp ≥ 5 indicate potential auroral activity at Berlin latitudes. Time indicated in UTC.",
    },
    "year": 2026,
}


def render() -> str:
    """Render with cid: references swapped for local file paths, for browser preview."""
    out = Template(TEMPLATE_PATH.read_text()).render(**CTX)
    return out.replace("cid:forecast_image", "./assets/kp_swift_ensemble_LAST.png").replace(
        "cid:aurora_image", "./assets/aurora_LAST.png"
    )


if __name__ == "__main__":
    out_path = TEMPLATE_PATH.parent / "test_render.html"
    out_path.write_text(render())
    print(f"wrote {out_path}")
