"""
src/ui/shared.py
----------------
UI helpers shared across all walkthrough pages.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Agent registry
# ---------------------------------------------------------------------------

AGENTS = {
    "hvac": {
        "name": "HVAC Site Intelligence Agent",
        "domain": "HVAC",
        "phase": "Phase 1",
        "tagline": "RAG pipeline with graceful degradation for field technicians",
        "why_it_matters": (
            "Most RAG systems answer every query — even when they shouldn't. "
            "This agent scores its own confidence before calling the LLM. "
            "LOW-confidence queries skip the model entirely: no hallucination, "
            "just a clean escalation. In a safety-critical environment, "
            "a wrong answer is worse than no answer. "
            "\n\n"
            "**For interviewers:** The confidence scoring and routing logic in "
            "`src/confidence.py` and `src/degradation.py` is the differentiator. "
            "The LLM is the last step, not the first."
        ),
        "metrics": {
            "eval_cases": 85,
            "overall_pass": "80.0%",
            "coverage": "94.0%",
            "hallucination": "<2%",
        },
    },
    "drone": {
        "name": "Drone Site Intelligence Agent",
        "domain": "Drone Inspection",
        "phase": "Phase 2",
        "tagline": "Multi-agent pipeline with spatial filters and session memory",
        "why_it_matters": (
            "Phase 2 adds a classifier agent that runs before retrieval — "
            "classifying query intent (ANOMALY_QUERY / COMPLIANCE_LOOKUP / "
            "HISTORICAL_LOOKUP / OUT_OF_SCOPE) and routing to the right "
            "Chroma collections. Spatial metadata filtering means a Zone-C "
            "question only retrieves Zone-C records. "
            "\n\n"
            "Session memory resolves follow-up questions: 'What about last month?' "
            "works because the agent remembers which zone you just asked about. "
            "\n\n"
            "**For interviewers:** This is the multi-agent handoff pattern — "
            "classifier → retrieval agent → confidence scorer → router. "
            "Each boundary is an explicit interface, not a monolith."
        ),
        "metrics": {},
    },
}

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

ACCENT    = "#0086A8"
TEXT      = "#1A1A2E"
MUTED     = "#6B7280"
BORDER    = "#E2E8F0"
SECONDARY = "#F0F2F6"

# ---------------------------------------------------------------------------
# Badge + escalation helpers
# ---------------------------------------------------------------------------

BADGE_COLORS = {
    "HIGH":    ("#15803d", "white"),
    "PARTIAL": ("#b45309", "white"),
    "LOW":     ("#b91c1c", "white"),
}


def confidence_badge_html(level: str, top_score: float) -> str:
    bg, fg = BADGE_COLORS.get(level, ("#888", "white"))
    return (
        f'<span style="background:{bg};color:{fg};padding:5px 16px;'
        f'border-radius:4px;font-weight:bold;font-size:0.95rem">'
        f'{level} CONFIDENCE</span>'
        f'&nbsp;&nbsp;<span style="color:#aaa;font-size:0.9rem">'
        f'similarity score: {top_score:.2f}</span>'
    )


def render_escalation_warning(route_type: str) -> None:
    if route_type == "LOW":
        st.error(
            "No reliable documentation found for this query. "
            "Contact your office or supervisor before proceeding."
        )
    elif route_type == "PARTIAL":
        st.warning("Conflicting sources detected. Verify this answer before acting.")


def render_source_expander(sources: str, route_type: str) -> None:
    if sources and sources.strip() and sources != "None" and route_type != "LOW":
        with st.expander("Sources", expanded=True):
            st.text(sources)


def render_why_it_matters(agent_key: str) -> None:
    agent = AGENTS.get(agent_key, {})
    why = agent.get("why_it_matters", "")
    if why:
        with st.expander("Why this matters (for interviewers)", expanded=False):
            st.markdown(why)


# ---------------------------------------------------------------------------
# Walkthrough components
# ---------------------------------------------------------------------------

WALKTHROUGH_STEPS = [
    (1, "Ask the Agent",   "pages/1_Ask_the_Agent.py"),
    (2, "View the Site",   "pages/2_View_the_Site.py"),
    (3, "Inspect a Zone",  "pages/3_Inspect_a_Zone.py"),
    (4, "See the Proof",   "pages/4_See_the_Proof.py"),
    (5, "Find the Gaps",   "pages/5_Find_the_Gaps.py"),
    (6, "Connect the Dots","pages/6_Connect_the_Dots.py"),
    (7, "How It Works",    "pages/7_How_It_Works.py"),
]


def render_walkthrough_progress(current_step: int) -> None:
    """Sidebar progress tracker — story-arc labels, current step highlighted."""
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            f'<p style="color:{MUTED};font-size:0.72rem;font-weight:800;'
            f'letter-spacing:0.12em;text-transform:uppercase;margin:0.1rem 0 0.6rem 0;">'
            f'Walkthrough</p>',
            unsafe_allow_html=True,
        )
        for step, label, path in WALKTHROUGH_STEPS:
            if step < current_step:
                st.page_link(path, label=f"✓  {label}")
            elif step == current_step:
                st.markdown(
                    f'<div style="padding:0.32rem 0.7rem;border-radius:6px;'
                    f'background:{SECONDARY};border-left:3px solid {ACCENT};'
                    f'font-size:0.88rem;font-weight:700;color:{TEXT};margin:0.12rem 0;">'
                    f'→ {step}. {label}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.page_link(path, label=f"  {step}. {label}")


def render_walkthrough_banner(step: int, persona_line: str, plain_english: str) -> None:
    """Walkthrough banner with progress dots. Dismissible via × button."""
    key = f"banner_dismissed_{step}"
    if st.session_state.get(key):
        return

    dots_html = "".join(
        f'<span style="width:8px;height:8px;border-radius:50%;display:inline-block;'
        f'background:{"#0086A8" if i <= step else "#CBD5E1"};margin-right:3px;'
        f'flex-shrink:0;"></span>'
        for i in range(1, 7)
    )

    banner_col, dismiss_col = st.columns([22, 1], gap="small")
    with banner_col:
        st.markdown(
            f"""
            <div style="background:linear-gradient(135deg,#EFF6FF 0%,#F0F9FF 100%);
                        border-left:5px solid {ACCENT};
                        border-radius:0 12px 12px 0;
                        padding:0.85rem 1.2rem;margin:0 0 1.1rem 0;">
              <div style="display:flex;align-items:center;gap:0.65rem;margin-bottom:0.45rem;flex-wrap:wrap;">
                <span style="background:{ACCENT};color:white;font-size:0.67rem;font-weight:800;
                             padding:0.18rem 0.6rem;border-radius:999px;letter-spacing:0.04em;
                             white-space:nowrap;flex-shrink:0;">
                  Step {step} / 6
                </span>
                <div style="display:flex;align-items:center;">{dots_html}</div>
              </div>
              <p style="margin:0 0 0.25rem 0;color:{TEXT};font-size:1.05rem;font-weight:800;line-height:1.3;">
                {persona_line}
              </p>
              <p style="margin:0;color:#374151;font-size:0.88rem;line-height:1.55;">
                {plain_english}
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with dismiss_col:
        st.markdown("<div style='margin-top:0.55rem'></div>", unsafe_allow_html=True)
        if st.button("✕", key=f"dismiss_{step}", help="Dismiss this banner"):
            st.session_state[key] = True
            st.rerun()


def render_next_step(next_page: str, next_label: str, bridge: str = "") -> None:
    """Narrative bridge + next-page CTA at the bottom of each walkthrough page."""
    st.markdown("---")
    if bridge:
        st.markdown(
            f'<p style="color:{MUTED};font-size:0.95rem;font-style:italic;'
            f'margin:0 0 0.5rem 0;">{bridge}</p>',
            unsafe_allow_html=True,
        )
    st.page_link(next_page, label=next_label)


def clear_walkthrough_state() -> None:
    """Clear all walkthrough session keys. Called by 'Start over'."""
    for key in list(st.session_state.keys()):
        if key.startswith("walkthrough_") or key.startswith("banner_dismissed_"):
            del st.session_state[key]
