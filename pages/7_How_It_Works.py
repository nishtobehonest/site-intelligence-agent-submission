"""
pages/7_How_It_Works.py
-----------------------
Interactive confidence scoring and architecture explainer.
Educational reference for demos and interviews.
"""

import os

import streamlit as st
from src.ui.shared import (
    ACCENT, BORDER, MUTED, SECONDARY, TEXT,
    render_walkthrough_progress,
)

st.set_page_config(page_title="How It Works", page_icon="🔍", layout="wide")

# ── Semantic color sets (same pattern as Connect the Dots) ───────────────────
GREEN         = "#15803d"
GREEN_BG      = "#f0fdf4"
GREEN_BORDER  = "#86efac"
AMBER         = "#b45309"
AMBER_BG      = "#fffbeb"
AMBER_BORDER  = "#fcd34d"
RED           = "#b91c1c"
RED_BG        = "#fef2f2"
RED_BORDER    = "#fca5a5"

HIGH_T    = float(os.getenv("CONFIDENCE_HIGH_THRESHOLD", 0.79))
PARTIAL_T = float(os.getenv("CONFIDENCE_PARTIAL_THRESHOLD", 0.50))

ROUTE_META = {
    "HIGH": {
        "color": GREEN, "bg": GREEN_BG, "border": GREEN_BORDER,
        "label": "HIGH CONFIDENCE", "emoji": "✅",
        "llm": "✅ LLM called — answer generated",
        "action": "A cited answer is returned. The technician can act on it.",
    },
    "PARTIAL": {
        "color": AMBER, "bg": AMBER_BG, "border": AMBER_BORDER,
        "label": "PARTIAL CONFIDENCE", "emoji": "⚠️",
        "llm": "⚠️ LLM called — answer flagged",
        "action": "Answer generated but marked uncertain. Verify before acting.",
    },
    "LOW": {
        "color": RED, "bg": RED_BG, "border": RED_BORDER,
        "label": "LOW CONFIDENCE", "emoji": "🚫",
        "llm": "🚫 LLM NOT called — zero hallucination risk",
        "action": "Escalation message sent. No answer generated. Contact a supervisor.",
    },
}


def _route(score: float, conflict: bool) -> str:
    if score < PARTIAL_T:
        return "LOW"
    if conflict or score < HIGH_T:
        return "PARTIAL"
    return "HIGH"


def _decision_line(score: float, conflict: bool, route: str) -> str:
    if score < PARTIAL_T:
        return f"score {score:.2f} < {PARTIAL_T} → LOW"
    if conflict:
        return f"score {score:.2f} ≥ {PARTIAL_T} but conflict detected → PARTIAL"
    if score < HIGH_T:
        return f"score {score:.2f} in [{PARTIAL_T}, {HIGH_T}) → PARTIAL"
    return f"score {score:.2f} ≥ {HIGH_T}, no conflict → HIGH"


def _score_bar(score: float, route: str) -> str:
    pct        = score * 100
    partial_pct = PARTIAL_T * 100
    high_pct    = HIGH_T * 100
    marker_color = {"HIGH": GREEN, "PARTIAL": AMBER, "LOW": RED}[route]

    low_w     = partial_pct
    partial_w = high_pct - partial_pct
    high_w    = 100 - high_pct

    low_label_x     = low_w / 2
    partial_label_x = partial_pct + partial_w / 2
    high_label_x    = high_pct + high_w / 2

    # Clamp score label so it doesn't overflow the bar edges
    score_label_x = max(2, min(pct, 97))

    return f"""
<div style="position:relative;height:40px;border-radius:8px;overflow:hidden;
            border:1px solid {BORDER};margin:0.6rem 0 0 0;">
  <div style="position:absolute;left:0;top:0;width:{low_w}%;height:100%;background:{RED_BG};"></div>
  <div style="position:absolute;left:{partial_pct}%;top:0;width:{partial_w}%;height:100%;background:{AMBER_BG};"></div>
  <div style="position:absolute;left:{high_pct}%;top:0;width:{high_w}%;height:100%;background:{GREEN_BG};"></div>
  <div style="position:absolute;left:{low_label_x}%;top:50%;transform:translate(-50%,-50%);
              font-size:0.7rem;font-weight:800;color:{RED};letter-spacing:0.05em;">LOW</div>
  <div style="position:absolute;left:{partial_label_x}%;top:50%;transform:translate(-50%,-50%);
              font-size:0.7rem;font-weight:800;color:{AMBER};letter-spacing:0.05em;">PARTIAL</div>
  <div style="position:absolute;left:{high_label_x}%;top:50%;transform:translate(-50%,-50%);
              font-size:0.7rem;font-weight:800;color:{GREEN};letter-spacing:0.05em;">HIGH</div>
  <div style="position:absolute;left:{partial_pct}%;top:0;width:2px;height:100%;background:#9CA3AF;opacity:0.6;"></div>
  <div style="position:absolute;left:{high_pct}%;top:0;width:2px;height:100%;background:#9CA3AF;opacity:0.6;"></div>
  <div style="position:absolute;left:{pct}%;top:0;width:4px;height:100%;
              background:{marker_color};transform:translateX(-50%);
              box-shadow:0 0 6px rgba(0,0,0,0.22);border-radius:2px;z-index:2;"></div>
</div>
<div style="position:relative;height:18px;margin-bottom:0.3rem;">
  <div style="position:absolute;left:{score_label_x}%;transform:translateX(-50%);
              font-size:0.72rem;font-weight:800;color:{marker_color};">▲ {score:.2f}</div>
  <div style="position:absolute;left:{partial_pct}%;transform:translateX(-50%);
              font-size:0.67rem;color:#9CA3AF;top:3px;">{PARTIAL_T}</div>
  <div style="position:absolute;left:{high_pct}%;transform:translateX(-50%);
              font-size:0.67rem;color:#9CA3AF;top:3px;">{HIGH_T}</div>
</div>
"""


# ── Sidebar ──────────────────────────────────────────────────────────────────
render_walkthrough_progress(7)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("🔍 How the System Works")
st.caption("Interactive reference — confidence scoring, routing, and architecture explained from scratch")

# ─────────────────────────────────────────────────────────────────────────────
# 1. Pipeline overview
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("The Pipeline — 5 Steps")
st.markdown(
    "Every query goes through the same five steps, in order. "
    "**The LLM is step 5, not step 1** — it only runs if the system is confident enough."
)

pipeline_steps = [
    ("1", "Classify",  "What kind of query? Which collections to search?", "classifier.py",  "#F8FAFC"),
    ("2", "Retrieve",  "Embed the query, search Chroma, return top-k chunks.", "retriever.py", "#F8FAFC"),
    ("3", "Score",     "How similar is the best match? Do sources conflict?", "confidence.py", "#EFF6FF"),
    ("4", "Gate",      "Score < 0.50 → skip LLM entirely. Otherwise proceed.", "assistant.py", GREEN_BG),
    ("5", "Route",     "Format the final response: answer, warn, or escalate.", "degradation.py", AMBER_BG),
]

arrow = (
    '<div style="display:flex;align-items:center;padding-top:1.6rem;'
    f'color:#CBD5E1;font-size:1.5rem;flex-shrink:0;padding-left:4px;padding-right:4px;">→</div>'
)

boxes = []
for n, title, desc, fname, bg in pipeline_steps:
    boxes.append(f"""
    <div style="flex:1;min-width:130px;background:{bg};border:1.5px solid {BORDER};
                border-radius:10px;padding:0.9rem 1rem;">
      <div style="font-size:1.4rem;font-weight:900;color:#CBD5E1;line-height:1;">{n}</div>
      <div style="font-size:0.95rem;font-weight:800;color:{TEXT};margin:0.25rem 0 0.3rem 0;">{title}</div>
      <div style="font-size:0.79rem;color:{MUTED};line-height:1.4;margin-bottom:0.5rem;">{desc}</div>
      <div style="font-size:0.68rem;color:#9CA3AF;font-family:monospace;">{fname}</div>
    </div>
    """)

pipeline_html = (
    '<div style="display:flex;gap:0;align-items:flex-start;overflow-x:auto;padding:0.5rem 0;">'
    + arrow.join(boxes)
    + "</div>"
)
st.markdown(pipeline_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Interactive score simulator
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🎛️ Confidence Score Simulator")
st.markdown(
    "Drag the slider to any similarity score, toggle conflict, and watch the routing "
    "decision update live — using the exact same thresholds as the production system."
)

sim_left, sim_right = st.columns([1, 1], gap="large")

with sim_left:
    score    = st.slider(
        "Similarity score  (0 = no match · 1 = perfect match)",
        min_value=0.0, max_value=1.0, value=0.82, step=0.01, key="how_sim_score",
    )
    conflict = st.toggle("Two sources disagree (conflict detected)", key="how_sim_conflict")

    route = _route(score, conflict)
    st.markdown(_score_bar(score, route), unsafe_allow_html=True)

    marker_color = {"HIGH": GREEN, "PARTIAL": AMBER, "LOW": RED}[route]
    st.markdown(
        f"""
        <table style="width:100%;font-size:0.82rem;border-collapse:collapse;margin-top:0.2rem;">
          <tr>
            <td style="padding:0.28rem 0;color:{MUTED};width:40%;">Score</td>
            <td style="padding:0.28rem 0;font-weight:700;color:{TEXT};">{score:.2f}</td>
          </tr>
          <tr>
            <td style="padding:0.28rem 0;color:{MUTED};">Conflict?</td>
            <td style="padding:0.28rem 0;font-weight:700;color:{TEXT};">{"Yes" if conflict else "No"}</td>
          </tr>
          <tr>
            <td style="padding:0.28rem 0;color:{MUTED};">Decision</td>
            <td style="padding:0.28rem 0;font-size:0.78rem;color:{marker_color};font-weight:600;">
              {_decision_line(score, conflict, route)}
            </td>
          </tr>
        </table>
        """,
        unsafe_allow_html=True,
    )

with sim_right:
    meta = ROUTE_META[route]
    st.markdown(
        f"""
        <div style="background:{meta['bg']};border:2px solid {meta['border']};
                    border-radius:14px;padding:1.4rem 1.6rem;">
          <div style="font-size:2.2rem;margin-bottom:0.4rem;">{meta['emoji']}</div>
          <div style="font-size:1.15rem;font-weight:900;color:{meta['color']};
                      margin-bottom:0.5rem;letter-spacing:0.02em;">{meta['label']}</div>
          <div style="font-size:0.88rem;font-weight:700;color:{meta['color']};
                      margin-bottom:1rem;">{meta['llm']}</div>
          <div style="font-size:0.88rem;color:{TEXT};line-height:1.6;">
            {meta['action']}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")
st.markdown("**Try a real scenario:**")

scenarios = [
    ("✅ LOTO procedure — score 0.93",         0.93, False),
    ("⚠️ Carrier refrigerant — score 0.52",    0.52, False),
    ("⚠️ Carrier 2017 vs 2023 — conflict",     0.78, True),
    ("🚫 Daikin VRV (not in corpus) — 0.31",  0.31, False),
]
scen_cols = st.columns(4)
for i, (label, s, c) in enumerate(scenarios):
    if scen_cols[i].button(label, use_container_width=True, key=f"scen_{i}"):
        st.session_state["how_sim_score"]    = s
        st.session_state["how_sim_conflict"] = c
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# 3. What is a similarity score?
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📐 What Is a Similarity Score?")

emb_left, emb_right = st.columns([3, 2], gap="large")

with emb_left:
    st.markdown(
        f"""
        <div style="background:{SECONDARY};border:1px solid {BORDER};border-radius:10px;
                    padding:1.1rem 1.3rem;">
          <p style="color:{ACCENT};font-size:0.7rem;font-weight:800;letter-spacing:0.1em;
                    text-transform:uppercase;margin:0 0 0.6rem 0;">Plain English</p>
          <p style="color:{TEXT};font-size:0.9rem;line-height:1.6;margin:0 0 0.7rem 0;">
            When you type a question, the system converts it into a list of
            <strong>384 numbers</strong> called an <strong>embedding</strong>.
            Every document chunk in the library has already been converted to its own 384-number list.
          </p>
          <p style="color:{TEXT};font-size:0.9rem;line-height:1.6;margin:0 0 0.7rem 0;">
            The system finds chunks whose number-lists are <strong>pointing in the same direction</strong>
            as yours — like arrows in a 384-dimensional space. The closer the angle, the higher the score.
          </p>
          <table style="width:100%;font-size:0.82rem;border-collapse:collapse;">
            <tr style="border-bottom:1px solid {BORDER};">
              <th style="text-align:left;padding:0.3rem 0.5rem;color:{MUTED};">Score</th>
              <th style="text-align:left;padding:0.3rem 0.5rem;color:{MUTED};">Meaning</th>
            </tr>
            <tr><td style="padding:0.28rem 0.5rem;font-weight:700;color:{GREEN};">0.93</td>
                <td style="padding:0.28rem 0.5rem;color:{TEXT};">Nearly the same meaning — strong match</td></tr>
            <tr style="background:{SECONDARY};"><td style="padding:0.28rem 0.5rem;font-weight:700;color:{AMBER};">0.75</td>
                <td style="padding:0.28rem 0.5rem;color:{TEXT};">Related but not exact</td></tr>
            <tr><td style="padding:0.28rem 0.5rem;font-weight:700;color:{AMBER};">0.52</td>
                <td style="padding:0.28rem 0.5rem;color:{TEXT};">Loosely connected — uncertain</td></tr>
            <tr style="background:{SECONDARY};"><td style="padding:0.28rem 0.5rem;font-weight:700;color:{RED};">0.31</td>
                <td style="padding:0.28rem 0.5rem;color:{TEXT};">Probably unrelated — escalate</td></tr>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

with emb_right:
    st.markdown("**Under the hood**")
    st.markdown(
        "Chroma returns L2 (Euclidean) distance, not cosine similarity directly. "
        "The correct conversion for unit-normalized vectors is:"
    )
    st.code("cosine_similarity = 1.0 - (L2_distance² / 2)", language="python")
    st.markdown(
        f"""
        <div style="background:{RED_BG};border:1px solid {RED_BORDER};border-radius:8px;
                    padding:0.75rem 1rem;margin-top:0.5rem;">
          <p style="margin:0 0 0.3rem 0;color:{RED};font-size:0.72rem;font-weight:800;
                    text-transform:uppercase;letter-spacing:0.08em;">⚠️ Common mistake</p>
          <p style="margin:0;font-size:0.83rem;color:{TEXT};">
            Using <code>1.0 - score</code> directly is wrong — it causes HIGH-confidence
            matches to score ~0.36 instead of ~0.80, breaking the routing entirely.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown(
        f'<p style="font-size:0.82rem;color:{MUTED};">'
        f"Model: <code>sentence-transformers/all-MiniLM-L6-v2</code> — produces unit-normalized "
        f"384-dimensional vectors, which is why the conversion formula works.</p>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 4. Conflict detection
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("⚡ Conflict Detection")
st.markdown(
    "A high score alone doesn't mean the answer is safe. "
    "If two different sources both score highly but say different things, the system surfaces the conflict "
    "instead of silently picking one."
)

cc1, cc2, cc3 = st.columns(3, gap="medium")

conflict_card = lambda title, color, bg, border, lines, verdict, verdict_color: f"""
<div style="background:{bg};border:1.5px solid {border};border-radius:10px;
            padding:1rem 1.1rem;height:100%;">
  <p style="color:{color};font-size:0.7rem;font-weight:800;letter-spacing:0.1em;
            text-transform:uppercase;margin:0 0 0.5rem 0;">{title}</p>
  <pre style="background:rgba(0,0,0,0.04);border-radius:6px;padding:0.6rem 0.75rem;
              font-size:0.78rem;line-height:1.6;margin:0 0 0.65rem 0;color:{TEXT};
              white-space:pre-wrap;">{lines}</pre>
  <p style="margin:0;font-size:0.83rem;color:{verdict_color};font-weight:700;">{verdict}</p>
</div>
"""

with cc1:
    st.markdown(
        conflict_card(
            "Cross-collection conflict",
            AMBER, AMBER_BG, AMBER_BORDER,
            "osha     → 0.82\nmanuals  → 0.75\nΔ = 0.07 < 0.15",
            "→ PARTIAL — OSHA and the manual disagree. Both surfaces surfaced.",
            AMBER,
        ),
        unsafe_allow_html=True,
    )

with cc2:
    st.markdown(
        conflict_card(
            "Version conflict (same collection)",
            AMBER, AMBER_BG, AMBER_BORDER,
            "carrier-2017.pdf → 0.81\ncarrier-2023.pdf → 0.74\nΔ = 0.07 < 0.15",
            "→ PARTIAL — Two versions disagree. Most RAG systems would silently pick one.",
            AMBER,
        ),
        unsafe_allow_html=True,
    )

with cc3:
    st.markdown(
        conflict_card(
            "Clean HIGH — no conflict",
            GREEN, GREEN_BG, GREEN_BORDER,
            "osha    → 0.93\nmanuals → 0.44\nΔ = 0.49 > 0.15",
            "→ HIGH — One source dominates. Answer confidently with citations.",
            GREEN,
        ),
        unsafe_allow_html=True,
    )

st.markdown("")
st.info(
    f"**Guard rail:** Conflict detection only fires if the top score ≥ {PARTIAL_T}. "
    f"Below that, the system routes LOW anyway — no need to check for conflicts in noise-level matches."
)

# ─────────────────────────────────────────────────────────────────────────────
# 5. Architecture — six collections
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🗄️ Architecture: Six Collections, Never Merged")
st.markdown(
    "The data lives in six separate Chroma collections — three per domain. "
    "Merging them would destroy conflict detection, which depends on knowing *which collection* each result came from."
)

arch_hvac, arch_drone = st.columns(2, gap="large")

def _collection_card(name: str, desc: str, chunks: str) -> str:
    return f"""
    <div style="background:#F8FAFC;border:1px solid {BORDER};border-radius:8px;
                padding:0.65rem 0.9rem;margin-bottom:0.5rem;display:flex;
                align-items:flex-start;gap:0.75rem;">
      <div style="flex:1;min-width:0;">
        <span style="font-family:monospace;font-weight:700;color:{ACCENT};font-size:0.9rem;">{name}</span>
        <div style="font-size:0.79rem;color:{MUTED};margin-top:0.18rem;line-height:1.4;">{desc}</div>
      </div>
      <span style="font-size:0.72rem;color:{MUTED};white-space:nowrap;margin-top:2px;">{chunks}</span>
    </div>
    """

with arch_hvac:
    st.markdown(
        f'<p style="font-size:0.7rem;font-weight:800;color:{MUTED};letter-spacing:0.1em;'
        f'text-transform:uppercase;margin:0 0 0.5rem 0;">HVAC — Phase 1</p>',
        unsafe_allow_html=True,
    )
    for name, desc, chunks in [
        ("osha",        "29 CFR 1910.147 (LOTO) · 29 CFR 1910.303 (Electrical)",      "283 chunks"),
        ("manuals",     "Carrier 48LC 2017/2023 · Lennox SL280 · Trane XR15",         "1,372 chunks"),
        ("job_history", "50 synthetic field service records",                           "181 chunks"),
    ]:
        st.markdown(_collection_card(name, desc, chunks), unsafe_allow_html=True)

with arch_drone:
    st.markdown(
        f'<p style="font-size:0.7rem;font-weight:800;color:{MUTED};letter-spacing:0.1em;'
        f'text-transform:uppercase;margin:0 0 0.5rem 0;">Drone Inspection — Phase 2</p>',
        unsafe_allow_html=True,
    )
    for name, desc, chunks in [
        ("inspection_records",  "Per-flight anomaly records by zone and date",          "202 chunks"),
        ("historical_baselines","Pre-construction baselines for deviation comparison",  "160 chunks"),
        ("compliance_docs",     "OSHA 1926.452 scaffold safety requirements",           "158 chunks"),
    ]:
        st.markdown(_collection_card(name, desc, chunks), unsafe_allow_html=True)

st.markdown(
    f"""
    <div style="background:{SECONDARY};border:1px solid {BORDER};border-radius:8px;
                padding:0.8rem 1.1rem;margin-top:0.5rem;">
      <strong style="color:{TEXT};">Why keep them separate?</strong>
      <span style="color:{MUTED};font-size:0.87rem;"> — Conflict detection works by noticing when
      the same query returns high-scoring results from <em>different</em> collections.
      Merging them erases source identity, making it impossible to detect that two sources disagree.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# 6. Phase 2 additions
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🚁 Phase 2 Additions")
st.markdown("Phase 1 was HVAC-only with no classifier. Phase 2 adds three new capabilities before retrieval.")

tab_cls, tab_spatial, tab_mem = st.tabs(["Classifier Agent", "Spatial Filters", "Session Memory"])

with tab_cls:
    tcl, tcr = st.columns(2, gap="large")
    with tcl:
        st.markdown(
            "The classifier runs **before** retrieval and identifies query intent, "
            "so the system knows which collections to search and how."
        )
        st.markdown(
            f"""
            | Query type | Example | Collections |
            |---|---|---|
            | `ANOMALY_QUERY` | "What cracks were found in Zone C?" | inspection_records |
            | `COMPLIANCE_LOOKUP` | "What OSHA rules cover scaffolding?" | compliance_docs |
            | `HISTORICAL_LOOKUP` | "Has Zone B had drainage issues?" | historical_baselines |
            | `OUT_OF_SCOPE` | "What's the weather tomorrow?" | *none — escalate immediately* |
            """
        )
    with tcr:
        st.markdown("**Two paths:**")
        st.markdown(
            f"""
            <div style="background:{GREEN_BG};border:1px solid {GREEN_BORDER};border-radius:8px;
                        padding:0.7rem 0.9rem;margin-bottom:0.5rem;">
              <strong style="color:{GREEN};">⚡ Rule-based — ~70% of queries, ~5ms</strong><br>
              <span style="font-size:0.83rem;color:{TEXT};">Keyword matching. No API call.</span>
            </div>
            <div style="background:{AMBER_BG};border:1px solid {AMBER_BORDER};border-radius:8px;
                        padding:0.7rem 0.9rem;">
              <strong style="color:{AMBER};">🤖 LLM classifier — ~30% of queries</strong><br>
              <span style="font-size:0.83rem;color:{TEXT};">Ambiguous queries sent to LLM for intent
              parsing and entity extraction (zone, equipment, time reference).</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab_spatial:
    st.markdown(
        "Restricts Chroma searches to a specific zone using metadata filters, "
        "so a Zone-C question only retrieves Zone-C records."
    )
    st.code(
        """# Without spatial filter — searches all 202 inspection records
results = collection.similarity_search(query, k=5)

# With spatial filter — Zone-C records only
results = collection.similarity_search(
    query, k=5,
    filter={"zone_id": {"$eq": "Zone-C"}}
)""",
        language="python",
    )
    st.markdown(
        f"""
        <div style="background:{AMBER_BG};border:1px solid {AMBER_BORDER};border-radius:8px;
                    padding:0.7rem 0.9rem;margin-top:0.5rem;">
          <strong style="color:{AMBER};">Fallback:</strong>
          <span style="font-size:0.83rem;color:{TEXT};"> If the filtered search returns fewer than 2 results,
          the system retries without the filter and flags it in the pipeline trace.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab_mem:
    st.markdown(
        "Tracks zone, equipment, time reference, and query type across turns — "
        "so follow-up questions resolve correctly."
    )
    st.code(
        """Turn 1: "What anomalies were found in Zone C?"
  → memory stores: zone=Zone-C, type=ANOMALY_QUERY

Turn 2: "What about last month?"
  → memory resolves: zone=Zone-C (from Turn 1)
  → adds time filter for previous month
  → retrieves Zone-C records from that period""",
        language="text",
    )
    st.markdown(
        f'<p style="font-size:0.83rem;color:{MUTED};margin-top:0.5rem;">'
        f"Stored in <code>st.session_state[\"drone_memory\"]</code>. "
        f'Reset anytime with the "Reset session" button in the sidebar on the Inspect a Zone page.</p>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# 7. Design principles
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🧱 Three Design Principles")

p1, p2, p3 = st.columns(3, gap="medium")

def _principle_card(title: str, body: str, punchline: str) -> str:
    return f"""
    <div style="background:#F8FAFC;border:1px solid {BORDER};border-radius:10px;
                padding:1.1rem 1.2rem;height:100%;">
      <p style="font-weight:800;color:{TEXT};margin:0 0 0.55rem 0;font-size:0.95rem;">{title}</p>
      <p style="font-size:0.84rem;color:{MUTED};line-height:1.6;margin:0 0 0.8rem 0;">{body}</p>
      <p style="font-size:0.82rem;color:{ACCENT};font-style:italic;margin:0;border-top:1px solid {BORDER};
                padding-top:0.55rem;">"{punchline}"</p>
    </div>
    """

with p1:
    st.markdown(
        _principle_card(
            "LLM is the last step",
            "Most RAG systems send the query straight to the LLM. This system embeds, retrieves, "
            "scores, and only then calls the LLM — and only if confidence is HIGH or PARTIAL.",
            "The LLM can't hallucinate what it never sees.",
        ),
        unsafe_allow_html=True,
    )

with p2:
    st.markdown(
        _principle_card(
            "False negatives beat false positives",
            "An unnecessary escalation is annoying. A confident wrong answer in a safety-critical "
            "setting can injure someone. When in doubt, escalate rather than guess.",
            "Tune thresholds conservatively. Silence is safe.",
        ),
        unsafe_allow_html=True,
    )

with p3:
    st.markdown(
        _principle_card(
            "Thresholds are product decisions",
            f"0.79 and 0.50 are not magic numbers. Set via env vars — no code change or redeploy needed. "
            f"Raising HIGH_THRESHOLD lowers hallucination risk but raises escalation rate.",
            "Engineering builds the dial. Product decides where to set it.",
        ),
        unsafe_allow_html=True,
    )

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.page_link("Home.py", label="← Back to walkthrough home")
