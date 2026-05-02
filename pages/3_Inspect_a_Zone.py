"""
pages/3_Inspect_a_Zone.py
-------------------------
Step 3: Drone agent investigation. Zone C pre-loaded from site map.
Session memory in expander. Pipeline trace in expander.
"""

import streamlit as st
from src.assistant import SiteIntelligenceAgent
from src.session_memory import SessionMemory
from src.ui.shared import (
    confidence_badge_html,
    render_escalation_warning,
    render_next_step,
    render_source_expander,
    render_walkthrough_banner,
    render_walkthrough_progress,
)

st.set_page_config(page_title="Inspect a Zone", page_icon="🚁", layout="wide")

ACCENT = "#0086A8"
TEXT   = "#1A1A2E"
MUTED  = "#6B7280"

QUERY_TYPE_META = {
    "ANOMALY_QUERY": {
        "emoji": "🔴",
        "label": "Anomaly Query",
        "desc": "Searching for problems in a specific zone",
        "bg": "#fef2f2", "border": "#fca5a5", "text": "#b91c1c",
    },
    "COMPLIANCE_LOOKUP": {
        "emoji": "📋",
        "label": "Compliance Lookup",
        "desc": "Looking up a safety rule or procedure",
        "bg": "#eff6ff", "border": "#93c5fd", "text": "#1d4ed8",
    },
    "HISTORICAL_LOOKUP": {
        "emoji": "📅",
        "label": "Historical Lookup",
        "desc": "Checking past inspection records",
        "bg": "#f5f3ff", "border": "#c4b5fd", "text": "#7c3aed",
    },
    "OUT_OF_SCOPE": {
        "emoji": "🚫",
        "label": "Out of Scope",
        "desc": "Not in the corpus — will escalate instead of guessing",
        "bg": "#F9FAFB", "border": "#E5E7EB", "text": "#6B7280",
    },
}


def render_classification_card(q_type: str, conf: float, zone: str, equipment: str,
                                time_ref: str, via_llm: bool) -> None:
    meta = QUERY_TYPE_META.get(q_type, {
        "emoji": "❓", "label": q_type or "Unknown",
        "desc": "Query type not recognised",
        "bg": "#F9FAFB", "border": "#E5E7EB", "text": "#6B7280",
    })

    path_chip = (
        '<span style="background:#fffbeb;border:1px solid #fcd34d;border-radius:999px;'
        'padding:0.14rem 0.55rem;font-size:0.76rem;color:#b45309;font-weight:700;">🤖 LLM classifier</span>'
        if via_llm else
        '<span style="background:#f0fdf4;border:1px solid #86efac;border-radius:999px;'
        'padding:0.14rem 0.55rem;font-size:0.76rem;color:#15803d;font-weight:700;">⚡ Instant · Rule-based</span>'
    )

    entity_chips = []
    if zone and zone != "—":
        entity_chips.append(
            f'<span style="background:#F0F2F6;border-radius:999px;padding:0.14rem 0.5rem;'
            f'font-size:0.76rem;color:#374151;font-weight:500;">📍 {zone}</span>'
        )
    if equipment and equipment != "—":
        entity_chips.append(
            f'<span style="background:#F0F2F6;border-radius:999px;padding:0.14rem 0.5rem;'
            f'font-size:0.76rem;color:#374151;font-weight:500;">🔧 {equipment}</span>'
        )
    if time_ref and time_ref != "—":
        entity_chips.append(
            f'<span style="background:#F0F2F6;border-radius:999px;padding:0.14rem 0.5rem;'
            f'font-size:0.76rem;color:#374151;font-weight:500;">🕐 {time_ref}</span>'
        )
    entities_html = (
        '<span style="color:#9CA3AF;font-size:0.76rem;">No entities extracted</span>'
        if not entity_chips else " ".join(entity_chips)
    )

    st.markdown(
        f"""
        <div style="border:1.5px solid {meta['border']};border-radius:12px;
                    overflow:hidden;margin-bottom:0.75rem;">
          <div style="background:{meta['bg']};padding:0.65rem 1rem;
                      display:flex;align-items:center;gap:0.6rem;">
            <span style="font-size:1.05rem;flex-shrink:0;">{meta['emoji']}</span>
            <div style="flex:1;min-width:0;">
              <p style="margin:0;color:{meta['text']};font-size:0.7rem;font-weight:800;
                        letter-spacing:0.1em;text-transform:uppercase;">{meta['label']}</p>
              <p style="margin:0;color:{meta['text']};font-size:0.8rem;opacity:0.85;">
                {meta['desc']}
              </p>
            </div>
            <span style="flex-shrink:0;background:white;color:{meta['text']};font-size:0.72rem;
                         font-weight:800;padding:0.15rem 0.55rem;border-radius:999px;
                         border:1px solid {meta['border']};">
              {conf:.0%}
            </span>
          </div>
          <div style="padding:0.6rem 1rem;background:white;display:flex;
                      flex-direction:column;gap:0.4rem;">
            <div>{path_chip}</div>
            <div style="display:flex;flex-wrap:wrap;gap:0.3rem;">{entities_html}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

PRESETS = [
    {
        "label": "ANOMALY — Zone-C",
        "query": "What anomalies were found in Zone-C during the last inspection?",
    },
    {
        "label": "COMPLIANCE — Lockout/Tagout",
        "query": "What are the OSHA lockout tagout requirements for drone maintenance?",
    },
    {
        "label": "HISTORICAL — Zone-B drainage",
        "query": "Has Zone-B had recurring drainage issues over the past 3 months?",
    },
    {
        "label": "FOLLOW-UP — session memory",
        "query": "What about last month?",
    },
]


def _format_filter(where_filter: dict) -> str:
    if not where_filter:
        return "No spatial filter — searched all collections"
    zone_filter = where_filter.get("zone_id")
    if isinstance(zone_filter, dict) and "$eq" in zone_filter:
        return f"Restricted to {zone_filter['$eq']}"
    return "Spatial filter applied"


def _format_route(route_type: str) -> str:
    if route_type == "HIGH":
        return "HIGH confidence: answer with citations"
    if route_type == "PARTIAL":
        return "PARTIAL confidence: answer with uncertainty warning"
    return "LOW confidence: escalate instead of guessing"


def render_pipeline_trace(trace: dict, route_type: str, top_score: float) -> None:
    classification  = trace.get("classification", {})
    query_type      = classification.get("query_type", "Unknown")
    classifier_conf = classification.get("confidence", 0.0)
    via_llm         = classification.get("via_llm", False)
    route           = trace.get("route")

    if route == "OUT_OF_SCOPE_SHORT_CIRCUIT":
        st.info("Classified as out of scope — retrieval and LLM skipped.")
        st.warning("Routed to LOW confidence escalation.")
        return

    if route == "UNKNOWN_ZONE_LOW":
        zone = classification.get("zone") or "Unknown zone"
        st.info(f"Classified as `{query_type}`, detected `{zone}` — not in corpus.")
        st.warning("Zone unknown — retrieval and LLM skipped.")
        return

    st.markdown(
        f"**1. Classify** — `{query_type}` at {classifier_conf:.0%} confidence "
        f"via {'LLM' if via_llm else 'rule-based fast path'}."
    )
    st.markdown(f"**2. Filter** — {_format_filter(trace.get('filter', {}))}.")

    filtered_count = trace.get("result_count_filtered", 0)
    fallback       = trace.get("fallback")
    fallback_count = trace.get("result_count_fallback")
    if fallback:
        st.markdown(
            f"**3. Retrieve** — filtered search: {filtered_count} results; "
            f"fallback full-corpus: {fallback_count} results."
        )
    else:
        st.markdown(f"**3. Retrieve** — {filtered_count} relevant records found.")

    conflict      = trace.get("conflict", False)
    conflict_text = "conflict detected" if conflict else "no source conflict"
    st.markdown(
        f"**4. Score** — top similarity `{top_score:.2f}`; "
        f"routed `{trace.get('confidence', route_type)}`; {conflict_text}."
    )

    llm_text = (
        "LLM called — generating cited answer"
        if route_type in ("HIGH", "PARTIAL")
        else "LLM skipped — LOW path, zero hallucination risk"
    )
    st.markdown(f"**5. Decide** — {_format_route(route_type)}. {llm_text}.")


@st.cache_resource(show_spinner="Loading drone inspection knowledge base...")
def load_agent():
    return SiteIntelligenceAgent()


# ---------------------------------------------------------------------------
# Session memory init + walkthrough pre-fill
# ---------------------------------------------------------------------------

if "drone_memory" not in st.session_state:
    st.session_state["drone_memory"] = SessionMemory()

if st.session_state.get("walkthrough_arrived_from_zone") and st.session_state.get("walkthrough_zone_query"):
    st.session_state["drone_query"] = st.session_state["walkthrough_zone_query"]
    st.session_state["drone_input"] = st.session_state["walkthrough_zone_query"]
elif st.session_state.get("walkthrough_zone_query") and "drone_query" not in st.session_state:
    st.session_state["drone_query"] = st.session_state["walkthrough_zone_query"]

memory: SessionMemory = st.session_state["drone_memory"]

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

render_walkthrough_progress(3)

with st.sidebar:
    with st.expander("Session memory", expanded=False):
        ctx = memory.get_context()
        st.markdown(f"**Turn:** {ctx['turn_count']}")
        st.markdown(f"**Zone:** {ctx['last_zone'] or '—'}")
        st.markdown(f"**Equipment:** {ctx['last_equipment'] or '—'}")
        st.markdown(f"**Time ref:** {ctx['last_time_ref'] or '—'}")
        st.markdown(f"**Query type:** {ctx['last_query_type'] or '—'}")
        if st.button("Reset session", use_container_width=True):
            memory.reset()
            st.rerun()

# ---------------------------------------------------------------------------
# Header + banner
# ---------------------------------------------------------------------------

st.title("🚁 Inspect a Zone")
st.caption("Step 3 · Classifier agent + spatial filters + session memory")

render_walkthrough_banner(
    3,
    "🚁 You're about to head to Zone C.",
    "Ask the system what you're walking into. It narrows the search to Zone C only — so you get the right records, not all of them.",
)

# Arrival callout — fires once when navigating from the site map
if st.session_state.get("walkthrough_arrived_from_zone"):
    st.success(
        "**The map already knew where you were headed.** "
        "Your query was pre-loaded from the zone you selected — you didn't have to type anything."
    )
    st.session_state["walkthrough_arrived_from_zone"] = False

# ---------------------------------------------------------------------------
# Preset buttons
# ---------------------------------------------------------------------------

st.markdown("**Quick demos:**")

if "drone_input" not in st.session_state:
    st.session_state["drone_input"] = st.session_state.get("drone_query", "")

btn_cols = st.columns(4)
for i, preset in enumerate(PRESETS):
    if btn_cols[i].button(preset["label"], use_container_width=True):
        st.session_state["drone_query"] = preset["query"]
        st.session_state["drone_input"] = preset["query"]

st.markdown("")

# ---------------------------------------------------------------------------
# Query layout: input | classification | answer
# ---------------------------------------------------------------------------

col_in, col_mid, col_out = st.columns([2, 2, 3])

with col_in:
    query = st.text_area(
        "Inspector question",
        height=120,
        placeholder="Ask about anomalies, OSHA compliance, or historical baselines...",
        key="drone_input",
    )
    submit = st.button("Ask", type="primary", use_container_width=True)

active_query = query if submit else ""

if active_query.strip():
    agent = load_agent()

    with st.spinner("Classifying and retrieving..."):
        result = agent.ask(active_query, session_memory=memory)

    trace          = result.get("pipeline_trace", {})
    classification = trace.get("classification", {})
    q_type         = classification.get("query_type", "—")
    conf           = classification.get("confidence", 0.0)
    zone           = classification.get("zone") or "—"
    equipment      = classification.get("equipment") or "—"
    time_ref       = classification.get("time_ref") or "—"
    via_llm        = classification.get("via_llm", False)

    with col_mid:
        st.markdown("### 🧠 What the classifier decided")
        render_classification_card(q_type, conf, zone, equipment, time_ref, via_llm)

        with st.expander("Pipeline decision path", expanded=False):
            render_pipeline_trace(trace, result["route_type"], result["top_score"])

    with col_out:
        st.markdown("### 💬 What the system found")
        st.markdown(
            confidence_badge_html(result["confidence_level"], result["top_score"]),
            unsafe_allow_html=True,
        )
        st.markdown("")

        response_text = result["response"]
        answer_text = (
            response_text.split("\n\nSources:\n", 1)[0]
            if "\n\nSources:\n" in response_text
            else response_text
        )
        st.markdown(answer_text)
        render_source_expander(result["sources"], result["route_type"])
        render_escalation_warning(result["route_type"])

else:
    with col_mid:
        st.markdown("### 🧠 What the classifier decided")
        st.markdown(
            f'<p style="color:{MUTED};font-style:italic;">Classification panel populates after a query.</p>',
            unsafe_allow_html=True,
        )
    with col_out:
        st.markdown("### 💬 What the system found")
        st.markdown(
            f'<p style="color:{MUTED};font-style:italic;">Results appear here after you submit a query.</p>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Next step
# ---------------------------------------------------------------------------

render_next_step(
    "pages/4_See_the_Proof.py",
    "Next: See the Proof →",
    "How do we know this system actually works?",
)
