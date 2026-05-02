"""
why_it_matters_content.py
-------------------------
Rendering logic for the "Why It Matters" visual explainer.
Moved out of `pages/` so Streamlit does not expose it as a standalone page.
Called from 1_Ask_the_Agent.py as a tab.
"""

import streamlit as st

BG        = "#FFFFFF"
SECONDARY = "#F0F2F6"
ACCENT    = "#0086A8"
TEXT      = "#1A1A2E"
MUTED     = "#6B7280"
GREEN     = "#15803d"
GREEN_BG  = "#f0fdf4"
GREEN_BORDER = "#86efac"
AMBER     = "#b45309"
AMBER_BG  = "#fffbeb"
AMBER_BORDER = "#d97706"
RED       = "#b91c1c"
RED_BG    = "#fef2f2"
RED_BORDER = "#fca5a5"
BORDER    = "#E2E8F0"


def render() -> None:
    """Render the full Why It Matters visual explainer."""

    # -----------------------------------------------------------------------
    # Section 1 — Hero: The Problem
    # -----------------------------------------------------------------------

    st.markdown(
        f"""
        <div style="padding:2rem 0 1rem 0;">
          <p style="color:{ACCENT};font-size:0.85rem;font-weight:600;letter-spacing:0.12em;
                    text-transform:uppercase;margin-bottom:0.4rem;">
            HVAC Site Intelligence Agent · Phase 1
          </p>
          <h1 style="font-size:2.4rem;font-weight:800;color:{TEXT};
                     line-height:1.15;margin:0 0 0.8rem 0;">
            Field technicians shouldn't<br>have to guess.
          </h1>
          <p style="font-size:1rem;color:{MUTED};max-width:620px;line-height:1.65;margin:0;">
            In HVAC maintenance, a wrong answer isn't just inconvenient — it's a compliance
            violation or a safety incident. Technicians today resolve questions from memory,
            PDF manuals, and phone calls to supervisors. This agent changes that.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_before, col_after = st.columns(2, gap="large")

    with col_before:
        st.markdown(
            f"""
            <div style="background:{RED_BG};border:1px solid {RED};border-radius:10px;
                        padding:1.4rem;height:100%;">
              <p style="color:{RED};font-size:0.75rem;font-weight:700;
                        letter-spacing:0.1em;text-transform:uppercase;margin:0 0 1rem 0;">
                ✗ &nbsp;Status quo
              </p>
              <div style="display:flex;flex-direction:column;gap:0.65rem;">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <span style="background:rgba(185,28,28,0.1);border-radius:50%;width:2rem;height:2rem;
                               display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">👷</span>
                  <span style="color:{TEXT};font-size:0.92rem;">Technician has a question on-site</span>
                </div>
                <div style="padding-left:1.25rem;color:{MUTED};font-size:0.8rem;">↓</div>
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <span style="background:rgba(185,28,28,0.1);border-radius:50%;width:2rem;height:2rem;
                               display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">📄</span>
                  <span style="color:{TEXT};font-size:0.92rem;">Searches paper manuals, Google, or calls supervisor</span>
                </div>
                <div style="padding-left:1.25rem;color:{MUTED};font-size:0.8rem;">↓</div>
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <span style="background:rgba(185,28,28,0.1);border-radius:50%;width:2rem;height:2rem;
                               display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">❓</span>
                  <span style="color:{TEXT};font-size:0.92rem;">Gets an uncertain or uncited answer</span>
                </div>
                <div style="padding-left:1.25rem;color:{MUTED};font-size:0.8rem;">↓</div>
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <span style="background:rgba(185,28,28,0.1);border-radius:50%;width:2rem;height:2rem;
                               display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">⚠️</span>
                  <span style="color:{TEXT};font-size:0.92rem;">Proceeds anyway — OSHA risk, rework, injury</span>
                </div>
              </div>
              <p style="color:{RED};font-size:0.78rem;margin:1rem 0 0 0;font-style:italic;">
                OSHA estimates $1B+ in preventable workplace injuries annually
                in industrial maintenance settings.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_after:
        st.markdown(
            f"""
            <div style="background:{GREEN_BG};border:1px solid {GREEN};border-radius:10px;
                        padding:1.4rem;height:100%;">
              <p style="color:{GREEN};font-size:0.75rem;font-weight:700;
                        letter-spacing:0.1em;text-transform:uppercase;margin:0 0 1rem 0;">
                ✓ &nbsp;With this agent
              </p>
              <div style="display:flex;flex-direction:column;gap:0.65rem;">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <span style="background:rgba(21,128,61,0.1);border-radius:50%;width:2rem;height:2rem;
                               display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">👷</span>
                  <span style="color:{TEXT};font-size:0.92rem;">Technician asks a natural-language question</span>
                </div>
                <div style="padding-left:1.25rem;color:{MUTED};font-size:0.8rem;">↓</div>
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <span style="background:rgba(21,128,61,0.1);border-radius:50%;width:2rem;height:2rem;
                               display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">🔍</span>
                  <span style="color:{TEXT};font-size:0.92rem;">Agent retrieves from OSHA docs, manuals, job history</span>
                </div>
                <div style="padding-left:1.25rem;color:{MUTED};font-size:0.8rem;">↓</div>
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <span style="background:rgba(21,128,61,0.1);border-radius:50%;width:2rem;height:2rem;
                               display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">📊</span>
                  <span style="color:{TEXT};font-size:0.92rem;">Scores confidence — HIGH, PARTIAL, or LOW</span>
                </div>
                <div style="padding-left:1.25rem;color:{MUTED};font-size:0.8rem;">↓</div>
                <div style="display:flex;align-items:center;gap:0.75rem;">
                  <span style="background:rgba(21,128,61,0.1);border-radius:50%;width:2rem;height:2rem;
                               display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">✅</span>
                  <span style="color:{TEXT};font-size:0.92rem;">Cited answer, flagged conflict, or clean escalation</span>
                </div>
              </div>
              <p style="color:{GREEN};font-size:0.78rem;margin:1rem 0 0 0;font-style:italic;">
                Every response tells you exactly what it knows, what it doesn't,
                and who to call when it isn't sure.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # -----------------------------------------------------------------------
    # Section 2 — Trust Layer: Three Paths
    # -----------------------------------------------------------------------

    st.markdown(
        f"""
        <div style="margin:1.5rem 0 0.25rem 0;">
          <p style="color:{ACCENT};font-size:0.8rem;font-weight:600;
                    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.3rem;">
            The trust layer
          </p>
          <h2 style="font-size:1.8rem;font-weight:700;color:{TEXT};margin:0 0 0.4rem 0;">
            Every answer is one of three things.
          </h2>
          <p style="color:{MUTED};font-size:0.92rem;max-width:580px;margin:0 0 1.5rem 0;">
            The routing decision is made before the LLM is called — not after.
            That's what makes this different from a standard chatbot.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_high, c_partial, c_low = st.columns(3, gap="medium")

    with c_high:
        st.markdown(
            f"""
            <div style="background:{GREEN_BG};border:1px solid {GREEN};
                        border-radius:10px;padding:1.4rem;height:100%;">
              <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="background:{GREEN};color:white;font-size:0.7rem;font-weight:700;
                             padding:3px 10px;border-radius:4px;letter-spacing:0.05em;">HIGH</span>
                <span style="color:{GREEN};font-size:1.1rem;">✅</span>
              </div>
              <p style="color:{TEXT};font-weight:700;font-size:1rem;margin:0 0 0.5rem 0;">
                Confident. Cited. Act on it.
              </p>
              <p style="color:{MUTED};font-size:0.85rem;line-height:1.55;margin:0 0 1rem 0;">
                Score ≥ 0.75, no source conflicts. LLM generates a grounded answer
                with explicit citations from the indexed documents.
              </p>
              <div style="background:rgba(40,167,69,0.08);border-left:3px solid {GREEN};
                          padding:0.6rem 0.75rem;border-radius:0 6px 6px 0;">
                <p style="color:{MUTED};font-size:0.72rem;margin:0 0 0.2rem 0;font-weight:600;">EXAMPLE</p>
                <p style="color:{TEXT};font-size:0.8rem;margin:0;font-style:italic;">
                  "Steps for lockout/tagout energy control?"
                </p>
                <p style="color:{GREEN};font-size:0.78rem;margin:0.3rem 0 0 0;">
                  Score 0.93 · 29 CFR 1910.147 cited
                </p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_partial:
        st.markdown(
            f"""
            <div style="background:{AMBER_BG};border:1px solid {AMBER};
                        border-radius:10px;padding:1.4rem;height:100%;">
              <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="background:{AMBER};color:#1a1a1a;font-size:0.7rem;font-weight:700;
                             padding:3px 10px;border-radius:4px;letter-spacing:0.05em;">PARTIAL</span>
                <span style="color:{AMBER};font-size:1.1rem;">⚠️</span>
              </div>
              <p style="color:{TEXT};font-weight:700;font-size:1rem;margin:0 0 0.5rem 0;">
                Conflicting sources. Verify first.
              </p>
              <p style="color:{MUTED};font-size:0.85rem;line-height:1.55;margin:0 0 1rem 0;">
                Sources disagree or score is borderline. LLM answers but the
                conflict is surfaced explicitly — technician reviews before acting.
              </p>
              <div style="background:rgba(230,168,23,0.08);border-left:3px solid {AMBER};
                          padding:0.6rem 0.75rem;border-radius:0 6px 6px 0;">
                <p style="color:{MUTED};font-size:0.72rem;margin:0 0 0.2rem 0;font-weight:600;">EXAMPLE</p>
                <p style="color:{TEXT};font-size:0.8rem;margin:0;font-style:italic;">
                  "Refrigerant charge for a Carrier rooftop unit?"
                </p>
                <p style="color:{AMBER};font-size:0.78rem;margin:0.3rem 0 0 0;">
                  Score 0.52 · 2017 vs 2023 manual conflict
                </p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_low:
        st.markdown(
            f"""
            <div style="background:{RED_BG};border:1px solid {RED};
                        border-radius:10px;padding:1.4rem;height:100%;">
              <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.75rem;">
                <span style="background:{RED};color:white;font-size:0.7rem;font-weight:700;
                             padding:3px 10px;border-radius:4px;letter-spacing:0.05em;">LOW</span>
                <span style="color:{RED};font-size:1.1rem;">🚫</span>
              </div>
              <p style="color:{TEXT};font-weight:700;font-size:1rem;margin:0 0 0.5rem 0;">
                Unknown. Escalate. LLM never called.
              </p>
              <p style="color:{MUTED};font-size:0.85rem;line-height:1.55;margin:0 0 1rem 0;">
                Below retrieval threshold — no reliable docs found.
                The LLM is <strong style="color:{RED};">skipped entirely</strong>.
                Zero hallucination risk by design.
              </p>
              <div style="background:rgba(220,53,69,0.08);border-left:3px solid {RED};
                          padding:0.6rem 0.75rem;border-radius:0 6px 6px 0;">
                <p style="color:{MUTED};font-size:0.72rem;margin:0 0 0.2rem 0;font-weight:600;">EXAMPLE</p>
                <p style="color:{TEXT};font-size:0.8rem;margin:0;font-style:italic;">
                  "Repair procedures for a Daikin VRV DX300?"
                </p>
                <p style="color:{RED};font-size:0.78rem;margin:0.3rem 0 0 0;">
                  Score 0.31 · Daikin not in corpus → escalate
                </p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background:{SECONDARY};border:1px solid {ACCENT};border-radius:8px;
                    padding:1.1rem 1.4rem;display:flex;align-items:flex-start;gap:0.75rem;">
          <span style="color:{ACCENT};font-size:1.3rem;flex-shrink:0;margin-top:0.1rem;">💡</span>
          <div>
            <p style="color:{TEXT};font-size:0.92rem;font-weight:600;margin:0 0 0.2rem 0;">
              The trust layer is not a disclaimer. It's a design constraint.
            </p>
            <p style="color:{MUTED};font-size:0.85rem;margin:0;line-height:1.55;">
              The system physically cannot hallucinate on LOW-confidence queries because
              the LLM is never invoked. Every LOW response is built deterministically
              from <code style="color:{ACCENT};">degradation.py</code> — no model, no generation, no risk.
              In safety-critical environments, a clean escalation is the correct answer.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # -----------------------------------------------------------------------
    # Section 3 — Architecture Diagram
    # -----------------------------------------------------------------------

    st.markdown(
        f"""
        <div style="margin:1.5rem 0 1.2rem 0;">
          <p style="color:{ACCENT};font-size:0.8rem;font-weight:600;
                    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.3rem;">
            Under the hood
          </p>
          <h2 style="font-size:1.8rem;font-weight:700;color:{TEXT};margin:0 0 0.4rem 0;">
            Five steps. One decision.
          </h2>
          <p style="color:{MUTED};font-size:0.92rem;max-width:560px;margin:0;">
            Confidence is scored before the LLM is ever called — routing each query
            to the right outcome, not just the most likely-sounding one.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def _step(n, label, desc, bg, border, fg):
        return (
            f'<div style="flex:1;background:{bg};border:1px solid {border};border-radius:8px;'
            f'padding:1rem 0.85rem;min-width:0;">'
            f'<p style="color:{fg};font-size:0.65rem;font-weight:700;letter-spacing:0.1em;'
            f'text-transform:uppercase;margin:0 0 0.3rem 0;">Step {n}</p>'
            f'<p style="color:{TEXT};font-weight:700;font-size:0.9rem;margin:0 0 0.3rem 0;">{label}</p>'
            f'<p style="color:{MUTED};font-size:0.75rem;margin:0;line-height:1.4;">{desc}</p>'
            f'</div>'
        )

    arrow = (
        f'<div style="display:flex;align-items:center;padding:0 0.4rem;'
        f'color:{MUTED};font-size:1.2rem;flex-shrink:0;">&rarr;</div>'
    )

    top_row = (
        f'<div style="display:flex;align-items:stretch;gap:0;margin-bottom:1.5rem;min-width:700px;">'
        + _step(1, "Query",    "Natural-language question from technician",                          "#eff6ff", "#bfdbfe", "#1d4ed8")
        + arrow
        + _step(2, "Classify", "Intent + entities &rarr; which collections to search",               "#f5f3ff", "#c4b5fd", "#7c3aed")
        + arrow
        + _step(3, "Retrieve", "Embed query &rarr; search Chroma collections &rarr; rank by cosine", "#ecfeff", "#a5f3fc", "#0e7490")
        + arrow
        + _step(4, "Score",    "Similarity + conflict detection &rarr; HIGH / PARTIAL / LOW",         AMBER_BG,  AMBER_BORDER, AMBER)
        + arrow
        + _step(5, "Route",    "Format final response based on confidence path",                      "#eef2ff", "#a5b4fc", "#4338ca")
        + "</div>"
    )

    divider_row = (
        f'<div style="display:flex;justify-content:flex-end;padding-right:3.5rem;'
        f'color:{MUTED};font-size:0.9rem;margin-bottom:0.75rem;min-width:700px;">'
        f'&darr; routes to</div>'
    )

    output_row = (
        f'<div style="display:flex;gap:0.75rem;min-width:700px;">'
        # HIGH
        f'<div style="flex:1;background:{GREEN_BG};border:1px solid {GREEN};border-radius:8px;padding:1rem;">'
        f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">'
        f'<span style="background:{GREEN};color:white;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:3px;">HIGH</span>'
        f'<span style="color:{MUTED};font-size:0.8rem;">score &ge; 0.75</span></div>'
        f'<p style="color:{TEXT};font-size:0.82rem;margin:0;line-height:1.45;">LLM called &rarr; grounded answer with source citations</p>'
        f'<p style="color:{GREEN};font-size:0.75rem;margin:0.4rem 0 0 0;font-style:italic;">"29 CFR 1910.147 &sect;(d)(4): before maintenance begins, all energy sources must be isolated..."</p>'
        f'</div>'
        # PARTIAL
        f'<div style="flex:1;background:{AMBER_BG};border:1px solid {AMBER};border-radius:8px;padding:1rem;">'
        f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">'
        f'<span style="background:{AMBER};color:white;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:3px;">PARTIAL</span>'
        f'<span style="color:{MUTED};font-size:0.8rem;">score 0.50&ndash;0.75 or conflict</span></div>'
        f'<p style="color:{TEXT};font-size:0.82rem;margin:0;line-height:1.45;">LLM called &rarr; answer + &#9888; conflict flag + both sources shown</p>'
        f'<p style="color:{AMBER};font-size:0.75rem;margin:0.4rem 0 0 0;font-style:italic;">"Carrier 2017: 350&ndash;410 PSI; 2023 manual: 395&ndash;450 PSI. Verify before acting."</p>'
        f'</div>'
        # LOW
        f'<div style="flex:1;background:{RED_BG};border:1px solid {RED};border-radius:8px;padding:1rem;">'
        f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">'
        f'<span style="background:{RED};color:white;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:3px;">LOW</span>'
        f'<span style="color:{MUTED};font-size:0.8rem;">score &lt; 0.50</span></div>'
        f'<p style="color:{TEXT};font-size:0.82rem;margin:0;line-height:1.45;"><strong style="color:{RED};">LLM skipped.</strong> Deterministic escalation from <code style="color:{RED};font-size:0.78rem;">degradation.py</code></p>'
        f'<p style="color:{RED};font-size:0.75rem;margin:0.4rem 0 0 0;font-style:italic;">"No documentation found for Daikin VRV DX300. Contact your supervisor."</p>'
        f'</div>'
        f'</div>'
    )

    st.markdown(
        f'<div style="background:{SECONDARY};border-radius:12px;padding:2rem 1.5rem;overflow-x:auto;">'
        + top_row + divider_row + output_row
        + '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p style="color:{MUTED};font-size:0.78rem;margin:0.6rem 0 0 0;font-style:italic;">'
        f'Collections are kept separate intentionally — conflict detection depends on knowing '
        f'<em>which</em> collection each result came from.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # -----------------------------------------------------------------------
    # Section 4 — Proof: By the Numbers
    # -----------------------------------------------------------------------

    st.markdown(
        f"""
        <div style="margin:1.5rem 0 1.2rem 0;">
          <p style="color:{ACCENT};font-size:0.8rem;font-weight:600;
                    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.3rem;">
            Measured, not claimed
          </p>
          <h2 style="font-size:1.8rem;font-weight:700;color:{TEXT};margin:0 0 0.4rem 0;">
            The numbers back it up.
          </h2>
          <p style="color:{MUTED};font-size:0.92rem;max-width:560px;margin:0;">
            85 evaluation cases across three categories: ground truth coverage,
            adversarial robustness, and conflict surfacing.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Eval cases", "85", help="Ground truth (50) + adversarial (20) + contradictions (15)")
    m2.metric("Overall pass rate", "80.0%", help="Weighted across all three eval categories")
    m3.metric("Coverage (GT)", "94.0%", help="Known equipment queries answered correctly")
    m4.metric("Hallucination rate", "<2%", help="LOW path skips LLM — fabrication is structurally prevented")

    st.markdown("<br>", unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    with e1:
        st.markdown(
            f"""
            <div style="background:{SECONDARY};border-radius:8px;padding:1.1rem;">
              <p style="color:{GREEN};font-size:0.72rem;font-weight:700;letter-spacing:0.1em;
                        text-transform:uppercase;margin:0 0 0.4rem 0;">Ground Truth · 94%</p>
              <p style="color:{TEXT};font-size:0.85rem;line-height:1.55;margin:0;">
                47 of 50 queries about known HVAC equipment correctly routed HIGH or PARTIAL.
                3 failures are near-miss model numbers (XR13 ≈ XR15) — a known semantic
                search limitation, documented and accepted.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e2:
        st.markdown(
            f"""
            <div style="background:{SECONDARY};border-radius:8px;padding:1.1rem;">
              <p style="color:{AMBER};font-size:0.72rem;font-weight:700;letter-spacing:0.1em;
                        text-transform:uppercase;margin:0 0 0.4rem 0;">Conflicts · 80%</p>
              <p style="color:{TEXT};font-size:0.85rem;line-height:1.55;margin:0;">
                12 of 15 contradiction scenarios correctly surfaced as PARTIAL.
                Two heuristics: cross-collection disagreement and within-collection
                version mismatch (Carrier 2017 vs 2023).
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with e3:
        st.markdown(
            f"""
            <div style="background:{SECONDARY};border-radius:8px;padding:1.1rem;">
              <p style="color:{RED};font-size:0.72rem;font-weight:700;letter-spacing:0.1em;
                        text-transform:uppercase;margin:0 0 0.4rem 0;">Adversarial · 45%</p>
              <p style="color:{TEXT};font-size:0.85rem;line-height:1.55;margin:0;">
                9 of 20 out-of-corpus queries correctly escalated. The 45% is an
                accepted limitation — dense vectors can't distinguish model numbers.
                Documented, not hidden.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background:{AMBER_BG};border:1px solid {AMBER};border-radius:8px;
                    padding:1rem 1.3rem;display:flex;align-items:flex-start;gap:0.75rem;">
          <span style="color:{AMBER};font-size:1.1rem;flex-shrink:0;margin-top:0.1rem;">⚠</span>
          <div>
            <p style="color:{AMBER};font-size:0.85rem;font-weight:600;margin:0 0 0.2rem 0;">
              Known limitation — adversarial pass rate is 45%, and that's intentional.
            </p>
            <p style="color:{MUTED};font-size:0.8rem;margin:0;line-height:1.5;">
              Semantic similarity cannot distinguish Trane XR13 from XR15 — vectors are
              too similar. Raising thresholds sacrifices ground-truth coverage faster than
              it gains adversarial precision. The right fix is hybrid retrieval (BM25 + dense),
              not threshold tuning. This tradeoff is measured, documented, and accepted.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Section 5 — Site Map
    # -----------------------------------------------------------------------

    st.markdown(
        f"""
        <div style="margin:1.5rem 0 1.2rem 0;">
          <p style="color:{ACCENT};font-size:0.8rem;font-weight:600;
                    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.3rem;">
            Spatial view
          </p>
          <h2 style="font-size:1.8rem;font-weight:700;color:{TEXT};margin:0 0 0.4rem 0;">
            Site map: where the system knows what is happening.
          </h2>
          <p style="color:{MUTED};font-size:0.92rem;max-width:620px;margin:0;">
            The drone workflow is not just semantic retrieval. It is zone-aware retrieval.
            Queries about Zone-C should resolve against Zone-C inspection records, not the full corpus.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="background:{SECONDARY};border:1px solid {BORDER};border-radius:12px;padding:1.25rem;">
          <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:1rem;align-items:stretch;">
            <div style="background:{BG};border:1px solid {BORDER};border-radius:10px;padding:1rem;">
              <p style="color:{TEXT};font-size:0.82rem;font-weight:700;margin:0 0 0.75rem 0;">Facility layout</p>
              <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:0.55rem;">
                <div style="background:#ecfeff;border:1px solid #67e8f9;border-radius:8px;padding:0.8rem;min-height:90px;">
                  <p style="color:{TEXT};font-size:0.75rem;font-weight:700;margin:0 0 0.25rem 0;">Zone-A</p>
                  <p style="color:{MUTED};font-size:0.72rem;line-height:1.45;margin:0;">Roof edge<br>Routine baseline</p>
                </div>
                <div style="background:{AMBER_BG};border:1px solid {AMBER_BORDER};border-radius:8px;padding:0.8rem;min-height:90px;">
                  <p style="color:{TEXT};font-size:0.75rem;font-weight:700;margin:0 0 0.25rem 0;">Zone-B</p>
                  <p style="color:{MUTED};font-size:0.72rem;line-height:1.45;margin:0;">Drainage watch<br>Recurring moisture</p>
                </div>
                <div style="background:{RED_BG};border:1px solid {RED_BORDER};border-radius:8px;padding:0.8rem;min-height:90px;">
                  <p style="color:{TEXT};font-size:0.75rem;font-weight:700;margin:0 0 0.25rem 0;">Zone-C</p>
                  <p style="color:{MUTED};font-size:0.72rem;line-height:1.45;margin:0;">Hotspot cluster<br>Active anomaly area</p>
                </div>
                <div style="background:#eff6ff;border:1px solid #93c5fd;border-radius:8px;padding:0.8rem;min-height:90px;">
                  <p style="color:{TEXT};font-size:0.75rem;font-weight:700;margin:0 0 0.25rem 0;">Zone-D</p>
                  <p style="color:{MUTED};font-size:0.72rem;line-height:1.45;margin:0;">Mechanical access<br>Intermittent inspection data</p>
                </div>
                <div style="background:#f5f3ff;border:1px solid #c4b5fd;border-radius:8px;padding:0.8rem;min-height:90px;">
                  <p style="color:{TEXT};font-size:0.75rem;font-weight:700;margin:0 0 0.25rem 0;">Zone-E</p>
                  <p style="color:{MUTED};font-size:0.72rem;line-height:1.45;margin:0;">Compliance zone<br>Reference-heavy queries</p>
                </div>
                <div style="background:{BG};border:1px dashed {BORDER};border-radius:8px;padding:0.8rem;min-height:90px;">
                  <p style="color:{TEXT};font-size:0.75rem;font-weight:700;margin:0 0 0.25rem 0;">Query flow</p>
                  <p style="color:{MUTED};font-size:0.72rem;line-height:1.45;margin:0;">Classifier extracts zone<br>Spatial filter narrows retrieval</p>
                </div>
              </div>
            </div>
            <div style="background:{BG};border:1px solid {BORDER};border-radius:10px;padding:1rem;">
              <p style="color:{TEXT};font-size:0.82rem;font-weight:700;margin:0 0 0.75rem 0;">Why this matters</p>
              <div style="display:flex;flex-direction:column;gap:0.75rem;">
                <div style="border-left:3px solid {ACCENT};padding-left:0.75rem;">
                  <p style="color:{TEXT};font-size:0.78rem;font-weight:700;margin:0 0 0.15rem 0;">Spatial filtering</p>
                  <p style="color:{MUTED};font-size:0.75rem;line-height:1.5;margin:0;">
                    A Zone-C question should not retrieve Zone-A records just because the anomaly wording looks similar.
                  </p>
                </div>
                <div style="border-left:3px solid {AMBER};padding-left:0.75rem;">
                  <p style="color:{TEXT};font-size:0.78rem;font-weight:700;margin:0 0 0.15rem 0;">Operational context</p>
                  <p style="color:{MUTED};font-size:0.75rem;line-height:1.5;margin:0;">
                    The map turns inspection logs into something an operator can reason about by location, not just text chunks.
                  </p>
                </div>
                <div style="border-left:3px solid {GREEN};padding-left:0.75rem;">
                  <p style="color:{TEXT};font-size:0.78rem;font-weight:700;margin:0 0 0.15rem 0;">Demo narrative</p>
                  <p style="color:{MUTED};font-size:0.75rem;line-height:1.5;margin:0;">
                    It makes the Phase 2 story legible: classifier → spatial filter → zone-specific evidence → response.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Section 6 — Knowledge Gap Map
    # -----------------------------------------------------------------------

    st.markdown(
        f"""
        <div style="margin:1.5rem 0 1.2rem 0;">
          <p style="color:{ACCENT};font-size:0.8rem;font-weight:600;
                    letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.3rem;">
            Coverage map
          </p>
          <h2 style="font-size:1.8rem;font-weight:700;color:{TEXT};margin:0 0 0.4rem 0;">
            Knowledge gap map: where the corpus is weak.
          </h2>
          <p style="color:{MUTED};font-size:0.92rem;max-width:620px;margin:0;">
            A good system does not hide uncertainty. It shows where retrieval coverage is strong,
            where conflicts appear, and where the correct answer is to escalate.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="background:{SECONDARY};border:1px solid {BORDER};border-radius:12px;padding:1.25rem;">
          <div style="background:{BG};border:1px solid {BORDER};border-radius:10px;padding:1rem;overflow-x:auto;">
            <table style="width:100%;border-collapse:collapse;font-size:0.8rem;">
              <thead>
                <tr>
                  <th style="text-align:left;padding:0.65rem;border-bottom:1px solid {BORDER};color:{TEXT};">Knowledge area</th>
                  <th style="text-align:left;padding:0.65rem;border-bottom:1px solid {BORDER};color:{TEXT};">Coverage</th>
                  <th style="text-align:left;padding:0.65rem;border-bottom:1px solid {BORDER};color:{TEXT};">Observed behavior</th>
                  <th style="text-align:left;padding:0.65rem;border-bottom:1px solid {BORDER};color:{TEXT};">Implication</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{TEXT};">OSHA / compliance procedures</td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};"><span style="background:{GREEN};color:white;padding:3px 8px;border-radius:999px;font-size:0.72rem;font-weight:700;">Strong</span></td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{MUTED};">Usually routes HIGH with clear citations</td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{MUTED};">Safe demo path for trust and correctness</td>
                </tr>
                <tr>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{TEXT};">Versioned equipment manuals</td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};"><span style="background:{AMBER};color:white;padding:3px 8px;border-radius:999px;font-size:0.72rem;font-weight:700;">Mixed</span></td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{MUTED};">Can route PARTIAL when manuals disagree</td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{MUTED};">Conflict surfacing is a feature, not a bug</td>
                </tr>
                <tr>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{TEXT};">Out-of-corpus model numbers</td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};"><span style="background:{RED};color:white;padding:3px 8px;border-radius:999px;font-size:0.72rem;font-weight:700;">Weak</span></td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{MUTED};">Should route LOW and skip the LLM</td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{MUTED};">This is the main hallucination-control boundary</td>
                </tr>
                <tr>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{TEXT};">Zone-specific drone anomalies</td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};"><span style="background:#0e7490;color:white;padding:3px 8px;border-radius:999px;font-size:0.72rem;font-weight:700;">Emerging</span></td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{MUTED};">Depends on classifier accuracy and spatial metadata quality</td>
                  <td style="padding:0.7rem;border-bottom:1px solid {BORDER};color:{MUTED};">Main Phase 2 leverage point</td>
                </tr>
                <tr>
                  <td style="padding:0.7rem;color:{TEXT};">Follow-up questions with omitted context</td>
                  <td style="padding:0.7rem;"><span style="background:#4338ca;color:white;padding:3px 8px;border-radius:999px;font-size:0.72rem;font-weight:700;">Contextual</span></td>
                  <td style="padding:0.7rem;color:{MUTED};">Resolved by session memory when prior zone/time exists</td>
                  <td style="padding:0.7rem;color:{MUTED};">Good evidence that the system is stateful, not stateless chat</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kg1, kg2, kg3 = st.columns(3)

    with kg1:
        st.markdown(
            f"""
            <div style="background:{GREEN_BG};border:1px solid {GREEN_BORDER};border-radius:10px;padding:1rem;height:100%;">
              <p style="color:{GREEN};font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin:0 0 0.35rem 0;">
                What is covered
              </p>
              <p style="color:{TEXT};font-size:0.84rem;line-height:1.55;margin:0;">
                Known OSHA procedures, common equipment procedures, and indexed inspection records
                should produce grounded answers with traceable provenance.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kg2:
        st.markdown(
            f"""
            <div style="background:{AMBER_BG};border:1px solid {AMBER_BORDER};border-radius:10px;padding:1rem;height:100%;">
              <p style="color:{AMBER};font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin:0 0 0.35rem 0;">
                What is contested
              </p>
              <p style="color:{TEXT};font-size:0.84rem;line-height:1.55;margin:0;">
                Version drift, stale manuals, and cross-collection contradictions should remain visible as PARTIAL,
                not be averaged into false confidence.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kg3:
        st.markdown(
            f"""
            <div style="background:{RED_BG};border:1px solid {RED_BORDER};border-radius:10px;padding:1rem;height:100%;">
              <p style="color:{RED};font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;margin:0 0 0.35rem 0;">
                What is missing
              </p>
              <p style="color:{TEXT};font-size:0.84rem;line-height:1.55;margin:0;">
                Unsupported manufacturers, unseen model numbers, and zones with no history should trigger deterministic escalation.
                Those gaps are product roadmap inputs.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background:{SECONDARY};border:1px solid {BORDER};border-radius:8px;padding:1rem 1.2rem;">
          <p style="color:{TEXT};font-size:0.9rem;font-weight:600;margin:0 0 0.3rem 0;">
            The walkthrough now ends with two operational lenses:
          </p>
          <p style="color:{MUTED};font-size:0.82rem;line-height:1.55;margin:0;">
            <strong>Site map</strong> explains spatial awareness in the drone workflow.
            <strong>Knowledge gap map</strong> explains confidence boundaries in both HVAC and drone retrieval.
            Together they make the demo read like a product system, not just a chatbot screen.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
