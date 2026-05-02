"""
pages/5_Find_the_Gaps.py
------------------------
Step 5: The Honesty Report.
Styled HTML heatmap — green = covered, red = gap.
Click any red cell to see the escalation message that would fire.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from textwrap import dedent

import streamlit as st
import streamlit.components.v1 as components
from src.ui.shared import render_next_step, render_walkthrough_banner, render_walkthrough_progress

st.set_page_config(page_title="Find the Gaps", page_icon="🧭", layout="wide")

DATA_PATH = Path(__file__).parent.parent / "data" / "raw" / "drone" / "inspection_records.json"

ZONES = ["Zone-A", "Zone-B", "Zone-C", "Zone-D", "Zone-E"]

PROBLEM_TYPES = [
    "thermal-hotspot",
    "corrosion",
    "blockage",
    "overheating",
    "panel-hotspot",
    "refrigerant-leak",
    "exposed-wiring",
    "pipe-separation",
]


@st.cache_data
def load_records() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open() as f:
        return json.load(f)


def build_heatmap_html(
    zones: list[str],
    problem_types: list[str],
    coverage: dict[str, set[str]],
    selected_zone: str | None,
) -> str:
    # Table header
    header_cells = (
        '<th style="text-align:left;padding:0.45rem 0.8rem;color:#6B7280;font-size:0.7rem;'
        'font-weight:800;text-transform:uppercase;letter-spacing:0.06em;'
        'background:#F0F2F6;border-radius:6px 0 0 6px;white-space:nowrap;">'
        "Inspection Zone</th>"
    )
    for p in problem_types:
        header_cells += (
            f'<th style="text-align:center;padding:0.45rem 0.4rem;color:#6B7280;'
            f'font-size:0.68rem;font-weight:800;text-transform:uppercase;'
            f'letter-spacing:0.04em;background:#F0F2F6;">'
            f"{p.replace('-', ' ')}</th>"
        )

    # Table rows
    rows = ""
    for zone in zones:
        is_selected = zone == selected_zone
        left_border = "border-left:4px solid #0086A8;" if is_selected else "border-left:4px solid transparent;"
        zone_weight = "font-weight:700;" if is_selected else "font-weight:500;"
        annotation  = (
            ' <span style="color:#0086A8;font-size:0.72rem;font-weight:600;">← you asked</span>'
            if is_selected else ""
        )

        rows += f'<tr style="{left_border}transition:background 0.1s;">'
        rows += (
            f'<td style="padding:0.5rem 0.8rem;white-space:nowrap;{zone_weight}">'
            f"{zone}{annotation}</td>"
        )

        for problem in problem_types:
            has_data = problem in coverage.get(zone, set())
            safe_zone    = zone.replace("'", "\\'")
            safe_problem = problem.replace("-", " ").replace("'", "\\'")

            if has_data:
                rows += (
                    '<td style="padding:0.3rem 0.25rem;">'
                    '<div style="background:#f0fdf4;border:1.5px solid #86efac;border-radius:6px;'
                    'padding:0.28rem 0;text-align:center;color:#15803d;font-size:0.78rem;'
                    'font-weight:600;user-select:none;">Covered</div></td>'
                )
            else:
                rows += (
                    f'<td style="padding:0.3rem 0.25rem;">'
                    f'<div class="gap-cell" '
                    f"onclick=\"showGap('{safe_zone}', '{safe_problem}', this)\" "
                    f'style="background:#fef2f2;border:1.5px solid #fca5a5;border-radius:6px;'
                    f'padding:0.28rem 0;text-align:center;color:#b91c1c;font-size:0.78rem;'
                    f'font-weight:600;cursor:pointer;" '
                    f'title="Click to see what a technician would get">Gap</div></td>'
                )

        rows += "</tr>"

    return dedent(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      * {{ box-sizing: border-box; }}
      body {{
        font-family: "Source Sans Pro", -apple-system, BlinkMacSystemFont, sans-serif;
        margin: 0; padding: 0; background: white;
      }}
      table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 3px;
      }}
      .gap-cell:hover {{
        background: #fee2e2 !important;
        border-color: #f87171 !important;
        transform: scale(1.04);
        transition: transform 0.1s, background 0.1s;
      }}
      .gap-cell.active {{
        outline: 2.5px solid #dc2626;
        outline-offset: 1px;
      }}
      #detail {{
        display: none;
        margin-top: 1rem;
        background: #fef2f2;
        border: 1.5px solid #fca5a5;
        border-left: 5px solid #b91c1c;
        border-radius: 0 10px 10px 0;
        padding: 0.85rem 1.1rem;
        font-size: 0.9rem;
        line-height: 1.6;
        color: #1A1A2E;
        animation: fadeIn 0.18s ease;
      }}
      @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(4px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
      }}
      #detail.visible {{ display: block; }}
      .detail-badge {{
        display: inline-block;
        background: #b91c1c;
        color: white;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 0.15rem 0.55rem;
        border-radius: 4px;
        letter-spacing: 0.05em;
        margin-bottom: 0.45rem;
      }}
      .detail-note {{
        color: #6B7280;
        font-size: 0.82rem;
        margin-top: 0.4rem;
      }}
    </style>
    </head>
    <body>
    <table>
      <thead><tr>{header_cells}</tr></thead>
      <tbody>{rows}</tbody>
    </table>

    <div id="detail">
      <div class="detail-badge">LOW CONFIDENCE — ESCALATE</div><br>
      <span id="detail-text"></span>
      <div class="detail-note" id="detail-note"></div>
    </div>

    <script>
    var activeCell = null;
    function showGap(zone, problem, el) {{
      if (activeCell) activeCell.classList.remove('active');
      el.classList.add('active');
      activeCell = el;
      var detail = document.getElementById('detail');
      detail.classList.add('visible');
      document.getElementById('detail-text').innerHTML =
        'No records for <strong>' + problem + '</strong> in <strong>' + zone + '</strong>. ' +
        'A technician asking about this would receive:<br>' +
        '<em style="color:#b91c1c;">"Insufficient documentation — contact supervisor before proceeding."</em>';
      document.getElementById('detail-note').textContent =
        'The LLM is not called on this path. Zero hallucination risk.';
    }}
    </script>
    </body>
    </html>
    """)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

records  = load_records()
coverage: dict[str, set[str]] = defaultdict(set)
for record in records:
    coverage[record["zone_id"]].add(record["anomaly_type"])

# ---------------------------------------------------------------------------
# Header + banner
# ---------------------------------------------------------------------------

render_walkthrough_progress(5)

st.title("🧭 Find the Gaps")
st.caption("Step 5 · The Honesty Report")

render_walkthrough_banner(
    5,
    "🚫 These are the questions the system refuses to answer.",
    "Every red cell is a trap. A standard AI would make something up. This one says 'I don't know' — and hands it back to a human.",
)

st.markdown(
    f"""
    <div style="display:flex;gap:0.75rem;align-items:stretch;margin:0.5rem 0 1.2rem 0;flex-wrap:wrap;">
      <div style="background:#f0fdf4;border:1.5px solid #86efac;border-radius:10px;
                  padding:0.7rem 1rem;flex:1;min-width:160px;">
        <p style="margin:0;font-size:0.7rem;font-weight:800;color:#15803d;
                  text-transform:uppercase;letter-spacing:0.08em;">✅ Covered</p>
        <p style="margin:0.2rem 0 0;font-size:0.85rem;color:#374151;line-height:1.4;">
          Records exist. The system can answer.
        </p>
      </div>
      <div style="background:#fef2f2;border:1.5px solid #fca5a5;border-radius:10px;
                  padding:0.7rem 1rem;flex:1;min-width:160px;">
        <p style="margin:0;font-size:0.7rem;font-weight:800;color:#b91c1c;
                  text-transform:uppercase;letter-spacing:0.08em;">🚫 Gap → click me</p>
        <p style="margin:0.2rem 0 0;font-size:0.85rem;color:#374151;line-height:1.4;">
          No records. LLM skipped. Escalated to supervisor.
        </p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Zone C annotation (if arriving from Inspect a Zone)
# ---------------------------------------------------------------------------

selected_zone = st.session_state.get("walkthrough_zone")
if selected_zone == "Zone-C":
    st.info("You just asked about Zone C. Its row is highlighted below.")

# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------

if not records:
    st.warning(
        "Drone inspection records not found. "
        "Add `data/raw/drone/inspection_records.json` to populate this page."
    )
else:
    # Dynamic height: header row + one row per zone + detail panel space
    table_height = 60 + len(ZONES) * 52 + 140
    heatmap_html = build_heatmap_html(ZONES, PROBLEM_TYPES, coverage, selected_zone)
    components.html(heatmap_html, height=table_height, scrolling=False)

# ---------------------------------------------------------------------------
# Next step
# ---------------------------------------------------------------------------

render_next_step(
    "pages/6_Connect_the_Dots.py",
    "Next: Connect the Dots →",
    "Now see how the system links every inspection across time, zone, cause, and responsibility.",
)
