"""
pages/1_Ask_the_Agent.py
------------------------
Step 1: Teach the three confidence-routing paths.
No tabs — just the agent. Route-specific aha callouts after each result.
"""

import os
import streamlit as st
from src.assistant import FieldServiceAssistant
from src.ui.shared import (
    confidence_badge_html,
    render_escalation_warning,
    render_next_step,
    render_source_expander,
    render_walkthrough_banner,
    render_walkthrough_progress,
)

st.set_page_config(page_title="Ask the Agent", page_icon="🔧", layout="wide")

ACCENT = "#0086A8"
TEXT   = "#1A1A2E"
MUTED  = "#6B7280"

PRESETS = [
    {
        "label": "1. HIGH — Lockout/Tagout",
        "query": "What are the steps for the lockout tagout energy control procedure?",
    },
    {
        "label": "2. PARTIAL — Carrier Refrigerant",
        "query": "What is the recommended refrigerant charge pressure for a Carrier rooftop unit?",
    },
    {
        "label": "3. LOW — Daikin VRV",
        "query": "What are the repair procedures for a Daikin VRV system model DX300?",
    },
]


@st.cache_resource(show_spinner="Loading HVAC knowledge base...")
def load_assistant():
    return FieldServiceAssistant()


def build_hvac_trace(result: dict) -> dict:
    high_threshold    = float(os.getenv("CONFIDENCE_HIGH_THRESHOLD", 0.75))
    partial_threshold = float(os.getenv("CONFIDENCE_PARTIAL_THRESHOLD", 0.50))
    level = result["confidence_level"]
    score = result["top_score"]

    if level == "LOW":
        branch    = f"score {score:.2f} < partial threshold {partial_threshold:.2f}"
        llm_called = False
    elif level == "PARTIAL":
        branch = (
            f"score {score:.2f} ≥ high threshold but conflict detected → PARTIAL"
            if score >= high_threshold
            else f"score {score:.2f} in partial range [{partial_threshold:.2f}, {high_threshold:.2f})"
        )
        llm_called = True
    else:
        branch    = f"score {score:.2f} ≥ high threshold {high_threshold:.2f}, no conflict"
        llm_called = True

    return {
        "retrieve": "Searched osha, manuals, job_history collections",
        "score":    branch,
        "llm":      "Called" if llm_called else "Skipped (LOW path — no hallucination)",
        "route":    result["route_type"],
    }


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

render_walkthrough_progress(1)


# ---------------------------------------------------------------------------
# Header + banner
# ---------------------------------------------------------------------------

st.title("🔧 Ask the Agent")
st.caption("Step 1 · Learn the three confidence-routing paths")

render_walkthrough_banner(
    1,
    "🔧 You just got dispatched to a unit you've never worked on.",
    "Ask the system. Watch it decide — in under a second — whether it's confident enough to answer, or whether it should stay silent.",
)

# ---------------------------------------------------------------------------
# Preset callout + buttons
# ---------------------------------------------------------------------------

st.info("Try these three queries **in order** — each one shows a different routing path.")

st.markdown("**Quick demos:**")

if "hvac_input" not in st.session_state:
    st.session_state["hvac_input"] = st.session_state.get("hvac_query", "")

btn_cols = st.columns(3)
for i, preset in enumerate(PRESETS):
    if btn_cols[i].button(preset["label"], use_container_width=True):
        st.session_state["hvac_query"] = preset["query"]
        st.session_state["hvac_input"] = preset["query"]

st.markdown("")

# ---------------------------------------------------------------------------
# Query input + result
# ---------------------------------------------------------------------------

col_in, col_out = st.columns([2, 3])

with col_in:
    query = st.text_area(
        "Technician question",
        height=120,
        placeholder="Ask about equipment procedures, OSHA requirements, or job history...",
        key="hvac_input",
    )
    submit = st.button("Ask", type="primary", use_container_width=True)

with col_out:
    active_query = query if submit else ""

    if active_query.strip():
        assistant = load_assistant()

        with st.spinner("Retrieving documents and scoring confidence..."):
            result = assistant.ask(active_query)

        level = result["confidence_level"]

        # Confidence badge
        st.markdown(
            confidence_badge_html(level, result["top_score"]),
            unsafe_allow_html=True,
        )
        st.markdown("")

        # Pipeline trace (collapsed by default — keeps the answer front and center)
        trace = build_hvac_trace(result)
        with st.expander("Pipeline trace", expanded=False):
            st.markdown(f"**1. Retrieve:** {trace['retrieve']}")
            st.markdown(f"**2. Score:** {trace['score']}")
            st.markdown(f"**3. LLM:** {trace['llm']}")
            st.markdown(f"**4. Route:** `{trace['route']}`")

        st.markdown("---")

        # Answer
        response_text = result["response"]
        answer_text = (
            response_text.split("\n\nSources:\n", 1)[0]
            if "\n\nSources:\n" in response_text
            else response_text
        )
        st.markdown(answer_text)

        render_source_expander(result["sources"], result["route_type"])
        render_escalation_warning(result["route_type"])

        # Route-specific aha callout
        if level == "HIGH":
            st.success(
                "✅ **Confident answer, cited source.** The system found strong documentation "
                "and called the LLM. Act on this."
            )
        elif level == "PARTIAL":
            st.warning(
                "⚠️ **Two sources disagreed.** The 2017 and 2023 Carrier manuals say different "
                "things about refrigerant pressure. The system surfaced both instead of picking one. "
                "Most RAG systems would return one answer with no warning."
            )
        elif level == "LOW":
            st.error(
                "🚫 **The LLM was not called.** A standard AI would have generated a "
                "confident-sounding answer here — likely wrong. This system chose silence instead."
            )
            st.caption(
                "What a standard LLM would do: generate an answer with no source. "
                "What this system did: escalate to a supervisor."
            )
    else:
        st.markdown(
            f'<p style="color:{MUTED};font-style:italic;margin-top:1rem;">'
            f"Results appear here after you run a query.</p>",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Next step
# ---------------------------------------------------------------------------

render_next_step(
    "pages/2_View_the_Site.py",
    "Next: View the Site →",
    "That was one unit on one rooftop. Here's what your whole site looks like.",
)
