"""
pages/6_Connect_the_Dots.py
---------------------------
Step 6: Memory graph walkthrough finale.
Four memory-type cards with real examples. Polished end summary card.
"""

import streamlit as st
from src.ui.shared import clear_walkthrough_state, render_walkthrough_banner, render_walkthrough_progress

st.set_page_config(page_title="Connect the Dots", page_icon="🕸️", layout="wide")

ACCENT    = "#0086A8"
TEXT      = "#1A1A2E"
MUTED     = "#6B7280"
BORDER    = "#E2E8F0"
SECONDARY = "#F0F2F6"
GREEN     = "#15803d"
GREEN_BG  = "#f0fdf4"
GREEN_BORDER = "#86efac"
AMBER     = "#b45309"
AMBER_BG  = "#fffbeb"
AMBER_BORDER = "#fcd34d"
RED       = "#b91c1c"
RED_BG    = "#fef2f2"
RED_BORDER   = "#fca5a5"
PURPLE    = "#7c3aed"
PURPLE_BG = "#f5f3ff"
PURPLE_BORDER = "#c4b5fd"
BLUE      = "#1d4ed8"
BLUE_BG   = "#eff6ff"
BLUE_BORDER  = "#93c5fd"

# ---------------------------------------------------------------------------
# Sidebar + header
# ---------------------------------------------------------------------------

render_walkthrough_progress(6)

st.title("🕸️ Connect the Dots")
st.caption("Step 6 · How the system links inspections across time, zone, cause, and responsibility")

render_walkthrough_banner(
    6,
    "🔗 Now you can see the full picture.",
    "Every inspection connects to a zone, a site, a time, and a pattern. Most systems treat records in isolation — this one shows you how they link together.",
)

# ---------------------------------------------------------------------------
# Causal edge example — the concrete hook
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div style="background:{BLUE_BG};border:1.5px solid {BLUE_BORDER};
                border-left:5px solid {BLUE};border-radius:0 10px 10px 0;
                padding:0.85rem 1.1rem;margin-bottom:1.25rem;">
      <p style="margin:0 0 0.2rem 0;color:{BLUE};font-size:0.7rem;font-weight:800;
                text-transform:uppercase;letter-spacing:0.1em;">👉 Start here</p>
      <p style="margin:0;color:{TEXT};font-size:0.92rem;line-height:1.55;">
        The Zone C corrosion finding in August <strong>triggered a follow-up inspection in Zone B</strong>
        three weeks later. That link is called a <strong>causal edge</strong> — the system
        traced the cause forward in time, instead of treating each record in isolation.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style="border:1px solid {BORDER};border-radius:14px;padding:1.3rem 1.5rem;
                background:white;margin:0 0 1.5rem 0;">
      <div style="display:grid;grid-template-columns:1fr 0.35fr 1fr 0.35fr 1fr;
                  gap:0.65rem;align-items:center;text-align:center;">
        <div style="background:{RED_BG};border:1.5px solid {RED_BORDER};border-radius:10px;
                    padding:0.85rem 0.75rem;">
          <p style="margin:0 0 0.2rem 0;color:{RED};font-weight:800;font-size:0.9rem;">Zone C · Corrosion</p>
          <p style="margin:0;color:{MUTED};font-size:0.8rem;">August inspection</p>
        </div>
        <div style="text-align:center;">
          <p style="margin:0;color:{RED};font-weight:800;font-size:0.95rem;">caused</p>
          <p style="margin:0;color:{MUTED};font-size:0.75rem;">causal edge</p>
        </div>
        <div style="background:{AMBER_BG};border:1.5px solid {AMBER_BORDER};border-radius:10px;
                    padding:0.85rem 0.75rem;">
          <p style="margin:0 0 0.2rem 0;color:{AMBER};font-weight:800;font-size:0.9rem;">Follow-up inspection</p>
          <p style="margin:0;color:{MUTED};font-size:0.8rem;">Three weeks later</p>
        </div>
        <div style="text-align:center;">
          <p style="margin:0;color:{ACCENT};font-weight:800;font-size:0.95rem;">compared to</p>
          <p style="margin:0;color:{MUTED};font-size:0.75rem;">entity edge</p>
        </div>
        <div style="background:{GREEN_BG};border:1.5px solid {GREEN_BORDER};border-radius:10px;
                    padding:0.85rem 0.75rem;">
          <p style="margin:0 0 0.2rem 0;color:{GREEN};font-weight:800;font-size:0.9rem;">Zone B · Baseline</p>
          <p style="margin:0;color:{MUTED};font-size:0.8rem;">Normal comparison</p>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Four memory types — cards with real examples
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <h3 style="color:{TEXT};margin:0 0 0.1rem 0;">Four types of memory link</h3>
    <p style="color:{MUTED};font-size:0.92rem;margin:0 0 1.1rem 0;">
      Each answers a different question a technician or manager would ask.
    </p>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4, gap="medium")

with m1:
    st.markdown(
        f"""
        <div style="background:{RED_BG};border:1.5px solid {RED_BORDER};border-radius:10px;
                    padding:1.1rem;height:100%;">
          <p style="color:{RED};font-size:0.68rem;font-weight:800;letter-spacing:0.1em;
                    text-transform:uppercase;margin:0 0 0.35rem 0;">WHY · Causal</p>
          <p style="color:{TEXT};font-weight:700;font-size:0.95rem;margin:0 0 0.4rem 0;">
            Why did Zone B get inspected again?
          </p>
          <p style="color:{MUTED};font-size:0.83rem;line-height:1.5;margin:0;">
            Zone C corrosion in August created a causal link to the Zone B follow-up.
            The system traces the chain of events instead of treating each record in isolation.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f"""
        <div style="background:{BLUE_BG};border:1.5px solid {BLUE_BORDER};border-radius:10px;
                    padding:1.1rem;height:100%;">
          <p style="color:{BLUE};font-size:0.68rem;font-weight:800;letter-spacing:0.1em;
                    text-transform:uppercase;margin:0 0 0.35rem 0;">WHEN · Temporal</p>
          <p style="color:{TEXT};font-weight:700;font-size:0.95rem;margin:0 0 0.4rem 0;">
            When did this anomaly first appear?
          </p>
          <p style="color:{MUTED};font-size:0.83rem;line-height:1.5;margin:0;">
            Temporal edges order inspections chronologically within each zone.
            "What about last month?" works because the sequence is preserved in memory.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f"""
        <div style="background:{GREEN_BG};border:1.5px solid {GREEN_BORDER};border-radius:10px;
                    padding:1.1rem;height:100%;">
          <p style="color:{GREEN};font-size:0.68rem;font-weight:800;letter-spacing:0.1em;
                    text-transform:uppercase;margin:0 0 0.35rem 0;">WHO · Entity</p>
          <p style="color:{TEXT};font-weight:700;font-size:0.95rem;margin:0 0 0.4rem 0;">
            Who owns this equipment?
          </p>
          <p style="color:{MUTED};font-size:0.83rem;line-height:1.5;margin:0;">
            Entity edges link the same zone or equipment type across time segments —
            so a query about Zone C retrieves all relevant records regardless of date.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f"""
        <div style="background:{PURPLE_BG};border:1.5px solid {PURPLE_BORDER};border-radius:10px;
                    padding:1.1rem;height:100%;">
          <p style="color:{PURPLE};font-size:0.68rem;font-weight:800;letter-spacing:0.1em;
                    text-transform:uppercase;margin:0 0 0.35rem 0;">WHAT · Semantic</p>
          <p style="color:{TEXT};font-weight:700;font-size:0.95rem;margin:0 0 0.4rem 0;">
            What type of problem keeps recurring?
          </p>
          <p style="color:{MUTED};font-size:0.83rem;line-height:1.5;margin:0;">
            Semantic edges cluster the same anomaly type across different zones —
            connecting all corrosion findings site-wide even when zones differ.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f'<p style="color:{MUTED};font-size:0.85rem;line-height:1.6;">'
    f"Inspired by Jiang et al., <em>MAGMA: A Multi-Graph based Agentic Memory Architecture</em>, "
    f"arXiv:2601.03236, January 2026.</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# End summary card
# ---------------------------------------------------------------------------

st.markdown("---")

st.markdown(
    f"""
    <div style="background:{SECONDARY};border:1.5px solid {BORDER};border-radius:16px;
                padding:1.6rem 1.8rem;max-width:700px;">
      <h2 style="color:{TEXT};margin:0 0 0.5rem 0;font-size:1.6rem;">
        You've seen the full system.
      </h2>
      <p style="color:{MUTED};font-size:1rem;line-height:1.75;margin:0 0 1.1rem 0;">
        6 steps &nbsp;·&nbsp; 3 routing paths &nbsp;·&nbsp;
        85 test cases &nbsp;·&nbsp; &lt;2% hallucination rate<br>
        2 domains &nbsp;·&nbsp; 0 guesses on LOW-confidence queries
      </p>
      <p style="color:{TEXT};font-weight:700;margin:0 0 0.25rem 0;">
        Nishchay Vishwanath &nbsp;·&nbsp; Cornell MEM 2026
      </p>
      <p style="margin:0;">
        <a href="https://github.com/nishtobehonest/site-intelligence-agent"
           style="color:{ACCENT};text-decoration:none;font-size:0.9rem;">
          GitHub ↗
        </a>
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("← Start over", type="secondary"):
    clear_walkthrough_state()
    if hasattr(st, "switch_page"):
        st.switch_page("Home.py")
    else:
        st.success("Walkthrough state cleared. Click **Home** in the sidebar to restart.")
