"""
pages/4_See_the_Proof.py
------------------------
Static eval metrics dashboard. Loads eval_results.csv when available.
"""

from pathlib import Path

import pandas as pd
import streamlit as st
from src.ui.shared import render_next_step, render_walkthrough_banner, render_walkthrough_progress

st.set_page_config(page_title="See the Proof", page_icon="📊", layout="wide")

CSV_PATH = Path(__file__).parent.parent / "eval_results.csv"

render_walkthrough_progress(4)

st.title("📊 See the Proof")
st.caption("Step 4 · Ground truth / adversarial / contradiction scenarios")
render_walkthrough_banner(
    4,
    "📋 Don't trust a tool you can't test.",
    "Here are 85 real test cases — questions with known right answers. See exactly what the system gets right, what it flags, and what it refuses to touch.",
)

st.markdown(
    """
    <div style="background:#eff6ff;border:1.5px solid #93c5fd;border-left:5px solid #1d4ed8;
                border-radius:0 10px 10px 0;padding:0.85rem 1.1rem;margin-bottom:1rem;">
      <p style="margin:0 0 0.2rem 0;color:#1d4ed8;font-size:0.7rem;font-weight:800;
                text-transform:uppercase;letter-spacing:0.1em;">👉 Start here</p>
      <p style="margin:0;color:#1A1A2E;font-size:0.92rem;line-height:1.55;">
        Filter to <strong>Adversarial → Failed</strong>. These are the near-misses —
        queries the system <em>should</em> refuse rather than guess. A standard LLM would
        answer every one. This system doesn't.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_results() -> pd.DataFrame:
    return pd.read_csv(CSV_PATH)


if not CSV_PATH.exists():
    st.warning("Eval results have not been generated yet.")
    st.markdown(
        """
        In a live deployment, run `python eval/run_eval.py` to populate this view.
        This dashboard normally shows routing accuracy across ground-truth,
        adversarial, and contradiction test cases.
        """
    )
    m_cols = st.columns(4)
    m_cols[0].metric("Expected eval cases", "85")
    m_cols[1].metric("Ground truth", "Coverage")
    m_cols[2].metric("Adversarial", "Escalation")
    m_cols[3].metric("Contradictions", "Conflict flags")
else:
    df = load_results()

    total = len(df)
    passed = df["passed"].sum()
    overall_pct = passed / total * 100 if total else 0

    sets = {
        "ground_truth": "Ground Truth",
        "adversarial": "Adversarial",
        "contradictions": "Contradictions",
    }

    m_cols = st.columns(4)
    m_cols[0].metric("Overall pass rate", f"{overall_pct:.1f}%", f"{int(passed)}/{total} cases")

    for i, (set_key, set_label) in enumerate(sets.items(), start=1):
        subset = df[df["set"] == set_key]
        if len(subset):
            pct = subset["passed"].sum() / len(subset) * 100
            m_cols[i].metric(set_label, f"{pct:.1f}%", f"{int(subset['passed'].sum())}/{len(subset)}")
        else:
            m_cols[i].metric(set_label, "—")

    st.markdown("---")

    set_cols = st.columns(3)
    for col, (set_key, set_label) in zip(set_cols, sets.items()):
        subset = df[df["set"] == set_key]
        with col:
            st.subheader(set_label)
            if len(subset) == 0:
                st.info("No data for this set.")
                continue
            passed_n = int(subset["passed"].sum())
            st.markdown(f"**{passed_n} / {len(subset)} passed**")
            conf_counts = subset["actual_confidence"].value_counts()
            st.bar_chart(conf_counts)

    st.markdown("---")
    st.subheader("All results")

    filter_cols = st.columns([2, 1])
    with filter_cols[0]:
        selected_sets = st.multiselect(
            "Filter by eval set",
            options=list(sets.keys()),
            default=list(sets.keys()),
            format_func=lambda k: sets.get(k, k),
        )
    with filter_cols[1]:
        pass_filter = st.selectbox("Filter by result", ["All", "Passed", "Failed"])

    filtered = df[df["set"].isin(selected_sets)] if selected_sets else df

    if pass_filter == "Passed":
        filtered = filtered[filtered["passed"] == True]
    elif pass_filter == "Failed":
        filtered = filtered[filtered["passed"] == False]

    def style_confidence(val):
        colors = {"HIGH": "#28a745", "PARTIAL": "#e6a817", "LOW": "#dc3545"}
        color = colors.get(str(val), "#888")
        return f"color: {color}; font-weight: bold"

    styled = filtered.style.map(style_confidence, subset=["actual_confidence"])
    st.dataframe(styled, use_container_width=True, height=400)

    with st.expander("Why measure these three categories separately?", expanded=False):
        st.markdown(
            "A single accuracy number hides the system's failure modes. "
            "**Ground truth** measures coverage, **adversarial** measures hallucination risk, "
            "and **contradictions** measures conflict surfacing."
        )

render_next_step(
    "pages/5_Find_the_Gaps.py",
    "Next: Find the Gaps →",
    "The proof tells you how it performed. The next page shows where it refuses to guess.",
)
