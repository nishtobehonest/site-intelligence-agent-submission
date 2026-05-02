# Evaluation Strategy — Phase 2
**Drone Domain + Classifier Eval**

---

## Eval Sets to Build

| File | Size | What It Tests | Target |
|------|------|--------------|--------|
| `eval/drone_ground_truth.json` | 30 pairs | Routing correct for answerable drone queries | > 80% correct |
| `eval/drone_adversarial.json` | 15 queries | Escalate (LOW) for out-of-corpus queries | > 70% correct |
| `eval/drone_classifier_eval.json` | 20 queries | Classifier assigns correct query_type | > 90% correct |

Phase 1 HVAC evals (`ground_truth.json`, `adversarial.json`, `contradictions.json`) must still pass as regression check.

---

## drone_ground_truth.json Schema

```json
[
  {
    "query": "What anomalies were flagged in Zone C during August 2025?",
    "expected_route": "HIGH",
    "expected_source_collection": "inspection_records",
    "notes": "Zone C has 12 synthetic records; August 2025 should return clear match"
  },
  ...
]
```

**Query distribution (30 total):**
- 12 × ANOMALY_QUERY (specific zone + time)
- 8 × HISTORICAL_LOOKUP (trend, baseline comparison)
- 7 × COMPLIANCE_LOOKUP (OSHA questions)
- 3 × contradiction queries (should route PARTIAL — two sources disagree)

**Correct behavior:** HIGH or PARTIAL (not LOW). Same definition as Phase 1 ground truth.

---

## drone_adversarial.json Schema

```json
[
  {
    "query": "What anomalies were found in Zone X last week?",
    "expected_route": "LOW",
    "failure_mode": "zone_does_not_exist",
    "notes": "Zone X is not in the corpus. Should escalate, not hallucinate."
  },
  ...
]
```

**Adversarial categories (15 total):**
- 6 × Non-existent zones (Zone X, Zone Z, Building 7)
- 4 × Timeframes with no data (pre-2024 dates, future dates)
- 3 × Out-of-domain (weather, stock prices, unrelated topics)
- 2 × Near-miss equipment not in corpus (DJI Phantom, Parrot Anafi — generic drone brands vs specific equipment types in corpus)

**Correct behavior:** LOW route — escalate without hallucinating.

---

## drone_classifier_eval.json Schema

```json
[
  {
    "query": "What does OSHA 1926 Subpart Q say about fall protection on scaffolding?",
    "expected_query_type": "COMPLIANCE_LOOKUP",
    "expected_zone": null,
    "expected_time_ref": null,
    "path": "rule_based"
  },
  {
    "query": "What anomalies were found in Zone B during the last inspection?",
    "expected_query_type": "ANOMALY_QUERY",
    "expected_zone": "Zone-B",
    "expected_time_ref": "last inspection",
    "path": "rule_based"
  },
  ...
]
```

**20 queries covering:**
- 5 clear COMPLIANCE queries (rule-based path)
- 5 clear ANOMALY queries with zone + time entity extraction
- 4 HISTORICAL queries (trend, baseline, recurring)
- 3 OUT_OF_SCOPE queries
- 3 ambiguous queries (require LLM classification path)

**Metrics to track:**
- `query_type_accuracy`: % where predicted type == expected type
- `zone_extraction_accuracy`: % where extracted_zone == expected_zone (among queries where expected_zone is not null)
- `time_ref_detection`: % where extracted_time_ref is non-null when expected_time_ref is non-null

---

## run_eval.py Changes

Add `--domain` flag:

```bash
python eval/run_eval.py --domain hvac    # Phase 1 evals (existing behavior)
python eval/run_eval.py --domain drone   # Phase 2 evals
python eval/run_eval.py --domain all     # Both (regression check)
```

Add `run_classifier_eval()` function:

```python
def run_classifier_eval(records: list) -> dict:
    """
    Tests classifier independently of the full pipeline.
    Faster than running the full agent for each query.
    Returns: {
        "query_type_accuracy": float,
        "zone_extraction_accuracy": float,
        "time_ref_detection_rate": float,
        "total": int,
        "passed": int
    }
    """
    from src.classifier import classify
    ...
```

---

## Eval Output Format

Same CSV format as Phase 1 + new columns:

```
query, domain, expected_route, actual_route, correct, query_type, classifier_confidence,
spatial_filter_applied, top_score, collection, source_file
```

Summary table printed to stdout:

```
Phase 2 Evaluation Results
══════════════════════════════════════════════════════════
                        Total    Correct    Accuracy
Drone Ground Truth        30        24        80.0%
Drone Adversarial         15        11        73.3%
Classifier Eval           20        18        90.0%
──────────────────────────────────────────────────────────
Phase 2 Overall           65        53        81.5%
══════════════════════════════════════════════════════════
Regression (HVAC)         85        68        80.0%   ✓
══════════════════════════════════════════════════════════
```

---

## Metric Targets Rationale

**Ground truth > 80%:** Same as Phase 1. The drone domain has cleaner data (purpose-built synthetic) so should be achievable.

**Adversarial > 70%:** Lower than Phase 1 HVAC adversarial (45%) because the drone near-miss problem is smaller — fewer near-miss equipment models that are semantically similar to in-corpus ones.

**Classifier > 90%:** This is the new bar. The classifier is the first agentic layer; if it mis-routes consistently, everything downstream degrades. 90% is achievable with a good rule-based fast-path + LLM fallback.

---

## What to Do When Targets Aren't Hit

| Metric | Below Target | Likely Cause | Fix |
|--------|-------------|-------------|-----|
| Ground truth | < 80% | Threshold mismatch | Tune `CONFIDENCE_HIGH_THRESHOLD` in `.env` |
| Adversarial | < 70% | Synthetic data too similar to corpus | Add more distinct out-of-corpus zones/equipment in eval set |
| Classifier | < 90% | LLM mis-classifying ambiguous queries | Expand rule-based keyword set; improve LLM prompt |

Do not tune thresholds before running the eval. Set defaults, run the eval, then tune based on data.
