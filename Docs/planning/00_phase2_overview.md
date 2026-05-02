# Phase 2 Overview — Site Intelligence Agent
**May – June 2026 · Portfolio Extension**

---

## What This Phase Is

Phase 1 proved the pipeline architecture (RAG + graceful degradation) works in the HVAC field service domain. Phase 2 pivots to drone site inspection — a real use case at DroneDeploy and Infravision — and adds the multi-agent layer that makes this genuinely interesting as a portfolio artifact.

The pipeline shape does not change. What changes is the domain, the data, and the addition of a classifier agent that runs *before* retrieval and decides how to retrieve.

---

## Features Being Added

| Feature | File(s) | What It Teaches |
|---------|---------|----------------|
| Drone inspection data layer | `src/generate_drone_data.py`, `src/ingest.py` | Domain-agnostic architecture |
| Spatial metadata filtering | `src/retriever.py` | Metadata-aware vector retrieval |
| Classifier agent | `src/classifier.py` | Multi-agent handoff design |
| Pipeline wiring | `src/assistant.py` | Agent orchestration |
| Session memory | `src/session_memory.py` | Stateful vs stateless agent design |
| App UI updates | `app.py` | Multi-domain demo UX |
| Drone eval suite | `eval/` | Evaluating agentic systems |
| Power grid domain (stretch) | data + ingest only | Architecture generalization proof |

---

## Build Order

Each step produces something testable. Do not start the next until the current exit criterion is met.

```
[1] Data layer + ingest (drone collections in Chroma)
 ↓
[2] Spatial metadata threading (where_filter in retriever)
 ↓
[3] Classifier agent (query type + entity extraction)
 ↓
[4] Pipeline wiring (SiteIntelligenceAgent class)
 ↓
[5] Session memory (stateful entity resolution)
 ↓
[6] App UI (domain switcher, session panel, streaming)
 ↓
[7] Eval suite (drone ground truth + classifier eval)
 ↓
[8] Second domain — stretch (power grid)
```

---

## Exit Criteria for Phase 2 Complete

- [ ] Classifier routes > 90% of queries by correct type (classifier eval)
- [ ] Spatial filter applies: Zone-C query returns only Zone-C inspection records
- [ ] Session memory resolves "what about last month?" from prior turn context
- [ ] Both HVAC (Phase 1) and Drone domains demoable from same Streamlit app
- [ ] Streaming output working in app.py
- [ ] Drone eval: ground truth > 80%, adversarial > 70%
- [ ] Phase 1 HVAC evals still pass (regression check)

---

## Three Demo Queries (Drone Domain)

Like Phase 1, define three preset queries that exercise all three routing paths:

- **HIGH**: "What anomalies were flagged in Zone C during the August 2025 inspection?"
  → inspection_records returns high-score match, no conflicts
- **PARTIAL**: "Is the corrosion on the Zone B structural panel above baseline levels?"
  → inspection_records and historical_baselines both return results, conflict detected
- **LOW**: "What is the status of Zone X inspection?"
  → Zone X does not exist in corpus, escalate without hallucinating

---

## Company Positioning

| Company | Why This Phase Matters to Them |
|---------|-------------------------------|
| DroneDeploy | Longitudinal anomaly intelligence — query past inspections, surface trends |
| Infravision | Safety-critical infrastructure inspection — graceful degradation prevents confident wrong answers |
| Wherobots | Spatial intelligence layer — zone-level filtering shows spatially-aware retrieval |
