"""
Home.py
-------
Opening scenario for the Site Intelligence Agent walkthrough.
Single column. Cinematic. One CTA.
"""

try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import streamlit as st

st.set_page_config(
    page_title="Site Intelligence Agent",
    page_icon="🛰️",
    layout="wide",
)

ACCENT       = "#0086A8"
TEXT         = "#1A1A2E"
MUTED        = "#6B7280"
SECONDARY    = "#F0F2F6"
BORDER       = "#E2E8F0"
GREEN        = "#15803d"
GREEN_BG     = "#f0fdf4"
GREEN_BORDER = "#86efac"
AMBER        = "#b45309"
AMBER_BG     = "#fffbeb"
AMBER_BORDER = "#fcd34d"
RED          = "#b91c1c"
RED_BG       = "#fef2f2"
RED_BORDER   = "#fca5a5"

st.markdown(
    """
    <style>
    @keyframes riseIn {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .scenario-line {
      opacity: 0;
      animation: riseIn 0.52s ease forwards;
      font-size: 1.42rem;
      line-height: 1.55;
      font-weight: 600;
      margin: 0 0 0.45rem 0;
      color: #1A1A2E;
    }
    .delay-1 { animation-delay: 0.05s; }
    .delay-2 { animation-delay: 0.32s; }
    .delay-3 { animation-delay: 0.59s; }
    .delay-4 { animation-delay: 0.86s; color: #6B7280; font-style: italic; font-weight: 500; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Constrain content to a readable width
content, _pad = st.columns([1.65, 1])

with content:
    # Label
    st.markdown(
        f"""
        <p style="color:{ACCENT};font-size:0.77rem;font-weight:800;letter-spacing:0.14em;
                  text-transform:uppercase;margin:1.75rem 0 0.65rem 0;">
          Site Intelligence Agent &nbsp;·&nbsp; Cornell MEM Capstone &nbsp;·&nbsp; April 2026
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Headline
    st.markdown(
        f"""
        <h1 style="font-size:3.55rem;line-height:1.05;color:{TEXT};font-weight:860;
                   margin:0 0 1.7rem 0;letter-spacing:-0.015em;">
          AI that knows<br>what it doesn't know.
        </h1>
        """,
        unsafe_allow_html=True,
    )

    # Scenario — staggered fade-in
    st.markdown(
        f"""
        <div style="border-left:4px solid {ACCENT};padding:0.1rem 0 0.1rem 1.2rem;
                    margin:0 0 1.8rem 0;">
          <p class="scenario-line delay-1">It's 2pm. You're on your fourth job today.</p>
          <p class="scenario-line delay-2">A rooftop unit you've never seen. A model you don't recognize.</p>
          <p class="scenario-line delay-3">The manual is 400 pages in your truck.</p>
          <p class="scenario-line delay-4">OSHA says this gap causes 50,000 preventable injuries a year.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hook
    st.markdown(
        f"""
        <p style="font-size:1.28rem;color:{TEXT};font-weight:700;margin:0 0 0.45rem 0;">
          We built an AI that knows what it doesn't know.
        </p>
        <p style="font-size:0.98rem;color:{MUTED};line-height:1.68;margin:0 0 1.5rem 0;
                  max-width:560px;">
          Before calling the language model, it scores its own retrieval confidence
          and routes every query to one of three paths:
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Routing pills — compact horizontal row
    st.markdown(
        f"""
        <div style="display:flex;gap:0.65rem;margin:0 0 2rem 0;flex-wrap:wrap;align-items:center;">
          <div style="background:{GREEN_BG};border:1.5px solid {GREEN_BORDER};border-radius:8px;
                      padding:0.42rem 0.9rem;display:flex;align-items:center;gap:0.4rem;">
            <strong style="color:{GREEN};font-size:0.85rem;">HIGH</strong>
            <span style="color:{MUTED};font-size:0.82rem;">&mdash; Answer. Strong evidence.</span>
          </div>
          <div style="background:{AMBER_BG};border:1.5px solid {AMBER_BORDER};border-radius:8px;
                      padding:0.42rem 0.9rem;display:flex;align-items:center;gap:0.4rem;">
            <strong style="color:{AMBER};font-size:0.85rem;">PARTIAL</strong>
            <span style="color:{MUTED};font-size:0.82rem;">&mdash; Conflict. Verify before acting.</span>
          </div>
          <div style="background:{RED_BG};border:1.5px solid {RED_BORDER};border-radius:8px;
                      padding:0.42rem 0.9rem;display:flex;align-items:center;gap:0.4rem;">
            <strong style="color:{RED};font-size:0.85rem;">LOW</strong>
            <span style="color:{MUTED};font-size:0.82rem;">&mdash; Silence. LLM skipped entirely.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CTA — primary styled button
    cta_col, _ = st.columns([1, 2])
    with cta_col:
        if st.button("Begin Walkthrough →", type="primary", use_container_width=True):
            if hasattr(st, "switch_page"):
                st.switch_page("pages/1_Ask_the_Agent.py")
            else:
                st.info("👈 Click **Ask the Agent** in the sidebar to begin.")

    # Footer
    st.markdown(
        f"""
        <p style="color:{MUTED};font-size:0.8rem;margin:1.4rem 0 0 0;line-height:1.65;">
          Built for safety-critical field work where a confident wrong answer is more dangerous
          than no answer at all. HVAC field service (Phase 1) &nbsp;+&nbsp;
          drone site inspection (Phase 2).
          &nbsp;·&nbsp;
          <a href="https://github.com/nishtobehonest/site-intelligence-agent"
             style="color:{ACCENT};text-decoration:none;">GitHub ↗</a>
        </p>
        """,
        unsafe_allow_html=True,
    )
