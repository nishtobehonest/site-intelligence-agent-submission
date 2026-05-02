# Plan: Multi-Page Streamlit Portfolio Dashboard

## Context

The existing `app.py` is a single-page Streamlit app covering only the HVAC domain with no pipeline trace, no multi-page nav, and no employer-facing explainers. This plan converts it into a multi-page, presentable dashboard that serves as both a working product demo and an interactive portfolio showcase — one page per major feature/agent, each with a live trace panel and "Why this matters" explainer for employers.

---

## Files to Create / Modify

| Action | Path |
|--------|------|
| Create | `.streamlit/config.toml` |
| Create | `pages/shared.py` |
| Modify | `app.py` → becomes Home/landing page |
| Create | `pages/1_HVAC_Agent.py` |
| Create | `pages/2_Drone_Agent.py` |
| Create | `pages/3_Eval_Dashboard.py` |
| Modify | `requirements.txt` → bump `streamlit>=1.29.0` |

---

## Step 1: `.streamlit/config.toml`

Dark theme, custom accent, no usage stats.

```toml
[theme]
base = "dark"
primaryColor = "#00B4D8"
backgroundColor = "#0F1117"
secondaryBackgroundColor = "#1A1D24"
textColor = "#E8EAF0"
font = "sans serif"

[browser]
gatherUsageStats = false
```

---

## Step 2: `pages/shared.py` — Registry + UI Helpers

Single source of truth for all portfolio content and shared rendering. All pages import from here.

**Contents:**
- `AGENTS` dict — one entry per feature: `name`, `domain`, `phase`, `tagline`, `why_it_matters`, `metrics`
- `BADGE_COLORS` — `{"HIGH": ("#28a745", "white"), "PARTIAL": (...), "LOW": (...)}`
- `confidence_badge_html(level, top_score) -> str` — colored HTML badge
- `render_escalation_warning(route_type)` — `st.error`/`st.warning` banner
- `render_source_expander(sources, route_type)` — collapsed sources block

---

## Step 3: `app.py` — Landing / Home Page

Strip all query logic. Replace with:
- Hero section (2-col): project abstract left, ASCII pipeline diagram right as `st.code()`
- Navigation cards (3-col): one per feature page, using `st.page_link()` + tagline from `AGENTS`
- Metrics row: 4 `st.metric()` widgets — 85 eval cases, 80% overall pass, 94% coverage, <2% hallucination rate

Remove all imports of `FieldServiceAssistant`, preset buttons, spinners, result rendering.

---

## Step 4: `pages/1_HVAC_Agent.py` — HVAC Agent

Migrates and extends the existing `app.py` query UI.

**Layout:** two columns — left (input), right (output + trace)

**Sidebar:** Confidence thresholds (read from env via `os.getenv`) — read-only display showing current `.env` values.

**Pipeline trace:** `FieldServiceAssistant.ask()` doesn't emit intermediate state. Reconstruct via `build_hvac_trace(result: dict) -> dict` using the output dict:
- `top_score` + `confidence_level` combination tells you which scoring branch fired
- If `top_score >= 0.75` but `confidence_level == "PARTIAL"` → conflict was detected (not score)
- `confidence_level == "LOW"` → LLM was skipped
- Read thresholds from `os.getenv("CONFIDENCE_HIGH_THRESHOLD", 0.75)` so trace is always accurate

Render trace in `st.status(..., expanded=True)` (available since Streamlit 1.28).

**Preset queries:** reuse the 3 existing presets from `app.py` (HIGH/PARTIAL/LOW).

**"Why this matters" expander:** collapsed by default, content from `AGENTS["hvac"]["why_it_matters"]`.

**Reuse from existing `app.py`:**
- `load_assistant()` with `@st.cache_resource`
- Preset button → `st.session_state["query"]` pattern
- Badge color logic (move to `shared.py`)

---

## Step 5: `pages/2_Drone_Agent.py` — Drone Site Intelligence Agent

**Layout:** three columns — left (input), middle (classification panel), right (answer + badge)

**Session memory:** store `SessionMemory` in `st.session_state.drone_memory`. Initialize once per session. Pass to `SiteIntelligenceAgent.ask(query, session_memory=memory)`. Sidebar shows `memory.summary()` with per-field breakdown + "Reset Session" button.

**Pipeline trace:** `SiteIntelligenceAgent.ask()` already returns `pipeline_trace` dict — use it directly. Render in a collapsed `st.expander("Full Pipeline Trace")` showing all 5 steps: classify → filter → retrieve → score → route.

**Classification panel (middle col):** `st.metric()` widgets for query_type, confidence, zone, equipment, time_ref. Caption shows `"Rule-based (fast path)"` vs `"LLM path"` based on `via_llm`.

**Preset queries (4):**
1. `"What anomalies were found in Zone-C during the last inspection?"` — ANOMALY_QUERY
2. `"What are the OSHA lockout tagout requirements for drone maintenance?"` — COMPLIANCE_LOOKUP
3. `"Has Zone-B had recurring drainage issues over the past 3 months?"` — HISTORICAL_LOOKUP
4. `"What about last month?"` — ambiguous, shows session memory resolving zone from prior turn

**"Why this matters" expander:** content from `AGENTS["drone"]["why_it_matters"]`.

**Agent loading:** `@st.cache_resource` on `SiteIntelligenceAgent()` constructor.

---

## Step 6: `pages/3_Eval_Dashboard.py` — Eval Metrics

Static — loads `eval_results.csv` at repo root. No re-running evals.

**Path resolution (from `pages/` subdir):**
```python
from pathlib import Path
CSV_PATH = Path(__file__).parent.parent / "eval_results.csv"
```

**Layout:**
- Metrics row (4 columns): overall pass rate, ground truth %, adversarial %, contradictions %
- Per-set breakdown (3 columns): pass/total counts + confidence distribution bar chart per set (`st.bar_chart(conf_counts)`)
- Filterable full table: `st.multiselect` for eval set + pass/fail toggle; `st.dataframe()` with styled confidence column (use `styler.map()` not deprecated `applymap`)

**"Why this matters" expander:** explains why ground truth / adversarial / contradictions are measured separately, not as a single accuracy number.

---

## Order of Implementation

1. `.streamlit/config.toml` — instant visual feedback, validates theme before writing pages
2. `pages/shared.py` — all pages depend on this
3. `app.py` → landing page — validates multi-page nav appears in sidebar
4. `pages/1_HVAC_Agent.py` — migrates existing logic; test with 3 presets
5. `pages/3_Eval_Dashboard.py` — purely static, fast to verify
6. `pages/2_Drone_Agent.py` — most complex; test session memory accumulation across turns
7. `requirements.txt` — bump streamlit pin to `>=1.29.0`

---

## Verification

```bash
streamlit run app.py
```

**Home page:** Sidebar shows 4 entries. Navigation cards link correctly via `st.page_link()`. Metrics row shows correct values (85 cases, 80%, 94%, <2%).

**HVAC Agent:**
- Preset HIGH → green badge, score ~0.93, trace shows "LLM Called"
- Preset PARTIAL → yellow badge, score ~0.52, trace shows partial range or conflict
- Preset LOW → red badge, escalation error, trace shows "LLM Skipped"
- Sidebar shows correct threshold values matching `.env`

**Drone Agent:**
- Preset 1 (Zone-C Anomaly) → middle col shows `ANOMALY_QUERY`, `Zone-C` extracted
- Preset 4 (follow-up "What about last month?") after Preset 1 → sidebar shows Zone-C persisted, classification trace shows `via_llm` path resolving with context
- "Reset Session" button → sidebar clears, `turn_count` returns to 0

**Eval Dashboard:**
- Metrics row: 80.0% overall, 94.0% GT, 45.0% adversarial, 80.0% contradictions
- Filter by set works; table shows 85 rows total
- Bar charts render for each set's confidence distribution
