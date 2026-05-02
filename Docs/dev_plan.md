# Site Intelligence Agent — Phased Development Plan

**Nishchay Vishwanath | April 2026**

---

## Current State (Phase 0 — Complete)

The RAG pipeline skeleton is fully written. No data has been ingested yet.

| Component | Status |
|-----------|--------|
| `src/ingest.py` | Written, untested (no data) |
| `src/retriever.py` | Written |
| `src/confidence.py` | Written |
| `src/degradation.py` | Written |
| `src/assistant.py` | Written |
| `src/llm.py` | Written |
| `demo/demo.py` | Written |
| `eval/run_eval.py` | Written |
| `data/raw/osha/` | Empty (README.txt only) |
| `data/raw/manuals/` | Empty (README.txt only) |
| `data/raw/job_history/` | Empty (README.txt only) |
| `eval/ground_truth.json` | Stub (2 pairs) |
| `eval/adversarial.json` | Stub (2 queries) |
| `eval/contradictions.json` | Stub |
| `app.py` | Does not exist |
| `tests/test_degradation.py` | Does not exist |

---

## Phase 1: Data Foundation

**Goal:** Get real documents into Chroma so retrieval actually works end-to-end.

**Owner:** Nishchay

### Steps

1. **OSHA documents** → `data/raw/osha/`
   - Download: 29 CFR 1910.147 (Lockout/Tagout)
   - Download: 29 CFR 1910.303 (Electrical general requirements)
   - Download: OSHA Field Operations Manual (CPL-02-00-164)
   - All are U.S. government public domain — no license issues

2. **Equipment manuals** → `data/raw/manuals/`
   - Target: 3–5 PDFs covering different equipment types
   - Good sources: Carrier HVAC, Trane, Lennox (all publish public technical docs)
   - Include at least two versions of the same manual if possible (enables contradiction testing)

3. **Synthetic job history** → `data/raw/job_history/`
   - Run: `python src/generate_synthetic.py`
   - Target: 50 records across 5 equipment types and 3 job types
   - Output schema: job_id, date, equipment_id, job_type, site_id, technician_notes, anomalies_flagged, resolution, compliance_notes

4. **Ingest into Chroma**
   - Run: `python src/ingest.py`
   - Verify all 3 collections build without errors
   - Check chunk counts logged to stdout

5. **Smoke test**
   - Run: `python demo/demo.py`
   - Use the three preset queries from CLAUDE.md (LOTO, refrigerant charge, missing equipment ID)

**Exit criterion:** All three routing paths (HIGH / PARTIAL / LOW) fire at least once with real data.

---

## Phase 2: Eval Set Build

**Goal:** Replace stubs with real evaluation data so metrics are meaningful.

**Owner:** Nishchay

### Steps

1. **Ground truth set** — expand `eval/ground_truth.json` from 2 → 50 pairs
   - Derive correct answers directly from ingested OSHA docs and manuals
   - Query distribution: 40% procedural, 30% equipment spec, 20% compliance, 10% job history lookup
   - Each entry: `{ "query": "...", "expected_answer": "...", "source": "..." }`

2. **Adversarial set** — expand `eval/adversarial.json` from 2 → 20 queries
   - Two failure mode categories: out-of-corpus equipment IDs, nonexistent job records
   - Correct system behavior: LOW confidence escalation (not a hallucinated answer)

3. **Contradictions set** — expand `eval/contradictions.json` from stub → 15 scenarios
   - Three conflict types:
     - Version conflicts within the same manual (2019 vs 2023 specs)
     - Spec disagreements across manufacturers
     - Procedure discrepancies between OSHA and manufacturer guidance
   - Correct system behavior: PARTIAL route, both sources surfaced

4. **Run eval**
   - Run: `python eval/run_eval.py --collection all --output eval_results.csv`
   - Record baseline metrics: hallucination rate, coverage rate, escalation rate

**Exit criterion:** Eval runner completes on all 85 cases. Baseline metrics recorded to `eval_results.csv`.

---

## Phase 3: Threshold Tuning & Unit Tests

**Goal:** Hit target metrics and lock down the degradation logic with tests.

**Owner:** Nishchay

### Steps

1. **Tune confidence thresholds** (adjust env vars, no code changes needed)
   - `HIGH_THRESHOLD` (default 0.75): raise → fewer wrong answers, higher escalation rate
   - `PARTIAL_THRESHOLD` (default 0.50): raise → more LOW routes; lower → more PARTIAL routes
   - Re-run eval after each change. Track hallucination rate and coverage rate.
   - Target: hallucination < 2% AND coverage > 80%. If they conflict, hallucination wins.

2. **Write unit tests** — `tests/test_degradation.py`
   - Test HIGH path: mock results with top_score > 0.75, assert route_type == "HIGH"
   - Test PARTIAL path: mock conflicting results, assert route_type == "PARTIAL" and conflict flag present
   - Test LOW path: mock empty results, assert escalate == True and no LLM call made

3. **Consistency test**
   - Run same 5 representative queries (one per equipment type) × 3 sessions each
   - Measure semantic similarity between runs
   - Target: < 15% variance on factual queries

**Exit criterion:** Eval targets met. `pytest tests/` passes.

---

## Phase 4: Streamlit Interface

**Goal:** Browser-based demo for live presentation.

**Owner:** Nishchay

### Steps

1. Create `app.py` in repo root — wraps `FieldServiceAssistant.ask()`

2. UI elements:
   - Text input for technician query
   - Three preset query buttons (one per routing path)
   - Color-coded confidence badge: green (HIGH) / yellow (PARTIAL) / red (LOW)
   - Response text area
   - Source citation block (document name, collection, relevance score)
   - Escalation warning panel shown only on LOW routes

3. Test locally: `streamlit run app.py` → `localhost:8501`

4. Walk through all three preset queries to verify demo flow

**Exit criterion:** All three routing paths demonstrable in browser in under 8 seconds per query.

---

## Phase 5: Submission Polish

**Goal:** Final metrics, clean repo, presentation-ready artifacts.

**Owner:** Nishchay

### Steps

1. Run full eval suite — produce final `eval_results.csv`
2. Verify final metrics meet targets (hallucination < 2%, coverage > 80%, escalation 10–25%)
3. Update `README.md` with setup instructions
4. Confirm `requirements.txt` covers all imports (including `streamlit`)
5. Record short video walkthrough: HIGH → PARTIAL → LOW in sequence

**Exit criterion:** April 8 submission package complete.

---

## Metric Targets (from dev plan)

| Metric | Target |
|--------|--------|
| Hallucination rate | < 2% |
| Coverage rate | > 80% |
| Escalation rate | 10–25% |
| Time to answer | < 8 seconds |
| Precision (cited source supports answer) | > 90% |
| Factual accuracy on ground truth | > 85% |

---

## Key Design Constraints

- Confidence thresholds are **product decisions** — tune conservatively. False positives (wrong confident answer) are more dangerous than false negatives (unnecessary escalation) in a safety-critical field context.
- Three separate Chroma collections (`osha`, `manuals`, `job_history`) — never merge into one. Source-aware retrieval enables conflict detection.
- Every response must include a source citation. No exceptions.
- For LOW confidence routes: the LLM is **not called**. Escalation message is generated programmatically in `degradation.py`.
