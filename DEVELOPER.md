# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Project Is

A RAG-based Site Intelligence Agent. Technicians ask natural-language questions; the system retrieves from three Chroma document collections, scores confidence, and either answers with citations (HIGH), flags conflicting sources (PARTIAL), or escalates without calling the LLM (LOW). The graceful degradation layer is the core differentiator.

**Phase 1 (HVAC) is complete and submitted.** Phase 2 (drone inspection domain) is in progress — classifier, session memory, drone data layer, dual-domain `SiteIntelligenceAgent`, and multi-page Streamlit app are written; drone eval suite is next.

---

## Commands

```bash
# Install
pip install -r requirements.txt
cp .env.example .env   # then add ANTHROPIC_API_KEY

# Ingest HVAC collections (Phase 1)
python src/ingest.py

# Ingest drone inspection collections (Phase 2)
python src/ingest.py --domain drone

# Ingest both domains
python src/ingest.py --domain all

# Run interactive demo or three preset demo queries
python demo/demo.py

# Generate synthetic HVAC job history (50 records via Claude API)
python src/generate_synthetic.py

# Generate synthetic drone inspection data
python src/generate_drone_data.py

# Run full evaluation suite → prints metrics table + saves eval_results.csv
python eval/run_eval.py

# Run unit tests
pytest tests/
```

**Tuning confidence thresholds without code changes:**
```bash
CONFIDENCE_HIGH_THRESHOLD=0.80 CONFIDENCE_PARTIAL_THRESHOLD=0.55 python demo/demo.py
```
Or set these in `.env`. Raising `HIGH_THRESHOLD` reduces hallucination risk; raising `PARTIAL_THRESHOLD` increases escalation rate.

**Current tuned values (`.env`):** `CONFIDENCE_HIGH_THRESHOLD=0.79`, `CONFIDENCE_PARTIAL_THRESHOLD=0.50`.

---

## Architecture

Two classes in `src/assistant.py` share the same pipeline shape:
- `FieldServiceAssistant` — Phase 1, HVAC-only, no classifier or session memory
- `SiteIntelligenceAgent` — Phase 2, dual-domain, active entry point for the Streamlit app

`SiteIntelligenceAgent.ask()` runs five steps in sequence:

```
query
  → classify()           # classifier.py: query type + entity extraction → which collections + retrieval strategy
  → retrieve()           # retriever.py: embed query, search Chroma collections, apply spatial filter, return top-k
  → score_confidence()   # confidence.py: score based on cosine similarity + conflict detection
  → llm.generate()       # llm.py: called ONLY if confidence is HIGH or PARTIAL
  → route()              # degradation.py: format final response based on route type
```

The classifier step is domain-aware and runs two paths: rule-based keyword matching (~70% of queries, ~5ms, no LLM call) or LLM structured output for ambiguous queries (`classifier.py`).

**Six Chroma collections across two domains** — never merge within or across domains:
- HVAC (Phase 1): `osha`, `manuals`, `job_history`
- Drone (Phase 2): `inspection_records`, `historical_baselines`, `compliance_docs`

**Domain selection** is determined at runtime by the classifier and/or explicit `domain=` parameter in `load_collections()`. `retriever.py` defines `HVAC_COLLECTIONS` and `DRONE_COLLECTIONS` constants.

Collections are kept separate intentionally — merging them would break conflict detection, which relies on identifying that the same query returns high-scoring results from multiple collections with similar scores (`retriever.py:detect_conflicts`).

**Conflict detection heuristic** (`retriever.py:detect_conflicts`): Two heuristics run in sequence:
1. **Cross-collection** (top 3): results from different collections with scores within 0.15 → PARTIAL. Catches OSHA vs manual disagreements.
2. **Within-collection version conflict** (top 6): multiple source *files* from the same collection with best-scores within 0.15 → PARTIAL. Added in Phase 2 to catch Carrier 48LC 2017 vs 2023 conflicts. Guard: only fires if the top source score ≥ 0.50 (prevents noise-level matches from triggering false conflicts).

**LOW path skips the LLM entirely** (`assistant.py`). The escalation message is built programmatically in `degradation.py`. Do not change this — calling the LLM on LOW-confidence context is exactly the hallucination scenario the system is designed to prevent.

**LLM provider is swappable** via `LLM_PROVIDER` env var (`anthropic` / `openai` / `gemini`). Currently configured for Gemini. Working model: `gemini-2.5-flash` (gemini-1.5-pro and gemini-2.0-flash are deprecated and return 404).

**Chroma similarity scores**: Chroma returns L2 distance for unit-normalized sentence-transformer vectors. Correct conversion formula is `1.0 - (L2_distance² / 2)` — this gives true cosine similarity. Do NOT use `1.0 - score` (that formula was wrong and caused HIGH-confidence matches to score ~0.36 instead of ~0.80).

---

## Current Data State

Chroma DB lives at `./data/chroma_db/`. Re-run `python src/ingest.py --domain all` after adding documents.

**HVAC domain (Phase 1 — complete):**

| Collection | Files | Chunks |
|---|---|---|
| `osha` | 29 CFR 1910.147 (Lockout/Tagout), 29 CFR 1910.303 (Electrical Safety) | 283 |
| `manuals` | Carrier 48LC 2017, Carrier 48LC 2023, Lennox SL280, Trane XR15 | 1,372 |
| `job_history` | synthetic_jobs.json (50 records) | 181 |

> ✅ **Duplicate chunks resolved.** Earlier runs had 2× counts (ingest run twice). Chroma DB was dropped and re-ingested cleanly.

**Drone domain (Phase 2 — in progress):**

| Collection | Files | Chunks |
|---|---|---|
| `inspection_records` | inspection_records.json | 202 |
| `historical_baselines` | historical_baselines.json | 160 |
| `compliance_docs` | OSHA 1926.452 (scaffold safety) | 158 |

**LangChain imports:** `src/ingest.py` and `src/retriever.py` use `langchain_chroma` and `langchain_huggingface` (not `langchain_community`). Both packages are in `requirements.txt`.

**HVAC demo queries:**
- Demo 1 (HIGH): "What are the steps for the lockout tagout energy control procedure?" — score 0.93
- Demo 2 (PARTIAL): "What is the recommended refrigerant charge pressure for a Carrier rooftop unit?" — score 0.52
- Demo 3 (LOW): "What are the repair procedures for a Daikin VRV system model DX300?" — score 0.31

**Drone demo queries (Phase 2 targets):**
- Demo 1 (HIGH): "What anomalies were flagged in Zone C during the August 2025 inspection?"
- Demo 2 (PARTIAL): "Is the corrosion on the Zone B structural panel above baseline levels?"
- Demo 3 (LOW): "What is the status of Zone X inspection?" — Zone X not in corpus, escalate

---

## Known Issues

1. ~~**`detect_conflicts` only fires across collection names**~~ — **FIXED.** Within-collection version conflict detection added to `retriever.py:detect_conflicts`. Carrier 2017 vs 2023 conflicts correctly surface as PARTIAL.

2. ~~**Duplicate chunks in Chroma**~~ — **FIXED.** Chroma DB dropped and re-ingested cleanly.

3. **Semantic search cannot distinguish model numbers** — queries about near-miss equipment (Trane XR13, Carrier 50XC, Lennox XC25) score high against in-corpus counterparts (XR15, 48LC, SL280) and route PARTIAL instead of LOW. Architectural limitation of dense vector retrieval. Accepted. Production fix: hybrid retrieval (BM25 + dense) or metadata filtering.

4. **Carrier 48LC airflow query retrieves Lennox content** — "airflow and static pressure settings for Carrier 48LC" returns Lennox SL280 results at top of ranking (score 0.78) because both manuals have similar airflow table content. No conflict fires. Chunking issue; deferred to Phase 3.

5. **Drone eval suite not yet built (Phase 2 in progress)** — `SiteIntelligenceAgent` pipeline, Streamlit walkthrough app (`Home.py`, `pages/1_Ask_the_Agent.py` through `pages/6_Connect_the_Dots.py`), classifier, session memory, and spatial filters are all done. Remaining: drone eval files, regression check on HVAC evals, and verifying streaming output.

---

## Eval Sets

**HVAC eval (Phase 1 — final baseline):**

| File | Size | Correct behavior | Baseline |
|------|------|-----------------|---------|
| `ground_truth.json` | 50 pairs | HIGH or PARTIAL (not LOW) | **94.0%** (47/50) |
| `adversarial.json` | 20 queries | LOW (escalate — no hallucination) | **45.0%** (9/20) |
| `contradictions.json` | 15 scenarios | PARTIAL (conflict surfaced) | **80.0%** (12/15) |
| **Overall** | **85 cases** | | **80.0%** (68/85) |

**Adversarial at 45% is an accepted known limitation** — failures are semantically similar near-miss equipment (XR13 ≈ XR15) unfixable with cosine similarity alone.

**Drone eval (Phase 2 — not yet run):** Targets are ground truth > 80%, adversarial > 70%, classifier > 90% correct type routing. Eval files not yet built.

**HVAC eval has been run** — results saved to `eval_results.csv` at repo root (final baseline metrics above).

Metric targets for submission: hallucination < 2%, coverage > 80%, escalation 10–25%.

---

## Key Constraints

- **Three separate Chroma collections — never merge.** Source-aware retrieval and conflict detection depend on this.
- **Every response must cite a source.** No uncited answers.
- **Confidence thresholds are product decisions, not engineering ones.** In a safety-critical context, false positives (confident wrong answer) are more dangerous than false negatives (unnecessary escalation). Tune conservatively.
- **The system prompt in `assistant.py` enforces grounding.** Do not weaken the "answer only from context" and "always cite" instructions.

---

## Phase 2 Build Status (Drone Domain)

| Component | Status |
|-----------|--------|
| `src/generate_drone_data.py` | ✅ Written |
| Drone data ingested to Chroma | ✅ Done (3 collections, 520 total chunks) |
| `src/classifier.py` | ✅ Written — rule-based + LLM fallback |
| `src/session_memory.py` | ✅ Written — zone/equipment/time entity tracking |
| `src/retriever.py` spatial filter | ✅ Written — `build_spatial_filter()`, domain-aware `load_collections()` |
| `src/assistant.py` dual-domain wiring | ✅ Done — `SiteIntelligenceAgent` class, drone system prompt, `parse_time_ref` complete |
| Streamlit walkthrough app + session panel | ✅ Done — `Home.py`, `pages/1_Ask_the_Agent.py` through `pages/6_Connect_the_Dots.py` |
| `src/ui/shared.py`, `src/ui/why_it_matters_content.py` | ✅ Done — Streamlit UI helper modules |
| Drone eval suite | ⬜ Not started |
| Regression check on HVAC evals | ⬜ Not started |

**Phase 2 exit criteria (from `Docs/planning/00_phase2_overview.md`):**
- [ ] Classifier routes > 90% of queries by correct type
- [ ] Zone-C query returns only Zone-C inspection records (spatial filter)
- [ ] "What about last month?" resolves via session memory
- [x] Both HVAC and Drone demoable from same Streamlit app
- [ ] Streaming output working
- [ ] Drone eval: ground truth > 80%, adversarial > 70%
- [ ] Phase 1 HVAC evals still pass (regression)

---

## Future Domain Extensions (Phase 3+)

The pipeline is domain-agnostic — add a new collection set and a classifier rule branch:
- Power grid construction: `safety_procedures` / `equipment_specs` / `incident_logs`

No changes needed in `confidence.py` or `degradation.py`.
