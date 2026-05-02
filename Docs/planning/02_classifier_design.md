# Classifier Agent Design
**Phase 2 · src/classifier.py**

---

## What the Classifier Does

Runs before retrieval. Takes the raw user query (+ session context) and outputs:
1. **Query type** — what kind of question this is
2. **Target collections** — which Chroma collections to search
3. **Spatial entities** — zone, equipment, time reference extracted from the query
4. **Retrieval strategy** — filtered, full-corpus, compliance-only, or skip

This is the first agent-to-agent handoff in the system. The classifier agent hands off to the retrieval layer with a structured decision, not just the raw query string.

---

## Query Types

| Type | Description | Example |
|------|-------------|---------|
| `COMPLIANCE_LOOKUP` | Regulatory, safety procedure, OSHA standard question | "What does OSHA 1926 say about fall protection on scaffolding?" |
| `HISTORICAL_LOOKUP` | Past inspection records, trends, baselines | "Has Zone D had recurring moisture issues in the past year?" |
| `ANOMALY_QUERY` | Current or recent anomaly status for a zone/equipment | "What anomalies were flagged in Zone C last month?" |
| `OUT_OF_SCOPE` | Outside the corpus — no relevant data can exist | "What is the weather forecast for Austin?" |

---

## Output Interface (ClassificationResult)

```python
@dataclass
class ClassificationResult:
    query_type: Literal["COMPLIANCE_LOOKUP", "HISTORICAL_LOOKUP", "ANOMALY_QUERY", "OUT_OF_SCOPE"]
    confidence: float                  # 0.0-1.0, classifier's own confidence
    extracted_zone: str | None         # e.g. "Zone-C", None if not mentioned
    extracted_equipment: str | None    # e.g. "rooftop-hvac", None if not mentioned
    extracted_time_ref: str | None     # raw string: "last month", "August 2025", etc.
    collections_to_search: list[str]   # which Chroma collections to pass to retrieve()
    retrieval_strategy: str            # "filtered" | "full" | "compliance_only" | "skip"
    reasoning: str                     # one sentence explaining the decision
```

**Collection mapping by query type:**
```
COMPLIANCE_LOOKUP  → ["compliance_docs"]
HISTORICAL_LOOKUP  → ["historical_baselines", "inspection_records"]
ANOMALY_QUERY      → ["inspection_records", "historical_baselines"]
OUT_OF_SCOPE       → []  (retrieval skipped entirely)
```

---

## Two-Path Classification

### Path 1: Rule-Based Fast-Path (no LLM call, ~5ms)

Handles ~70% of queries via keyword matching. Returns `None` if ambiguous.

**Keyword sets:**

```python
COMPLIANCE_KEYWORDS = {"osha", "regulation", "requirement", "procedure", "lockout",
                       "tagout", "safety standard", "cfr", "subpart", "compliance", "hazard"}

HISTORICAL_KEYWORDS = {"last month", "previous", "history", "past", "inspection record",
                       "was flagged", "has been", "prior", "trend", "baseline", "recurring"}

ANOMALY_KEYWORDS    = {"anomaly", "anomalies", "flagged", "zone", "severity", "hotspot",
                       "corrosion", "damage", "what was found", "current status", "found in"}

OUT_OF_SCOPE_SIGNALS = {"weather", "stock", "news", "unrelated domain keyword"}
```

**Decision rule:**
- 2+ COMPLIANCE hits, 0 others → COMPLIANCE_LOOKUP (confidence: 0.90)
- 2+ HISTORICAL hits, 0 others → HISTORICAL_LOOKUP (confidence: 0.85)
- 2+ ANOMALY hits, 0 others → ANOMALY_QUERY (confidence: 0.85)
- Any OUT_OF_SCOPE signal → OUT_OF_SCOPE (confidence: 0.95)
- Anything else → `None` (falls through to LLM path)

### Path 2: LLM Classification (ambiguous queries)

Structured JSON output enforced via Anthropic tool_use (or Gemini response_schema).

**Why structured output over free-text parsing:** Production-grade approach. Eliminates the most common failure mode in agent pipelines (malformed JSON). Shows knowledge of modern API patterns.

**Prompt template:**
```
You are a query classifier for a drone site inspection intelligence system.

The system has three data sources:
- inspection_records: actual drone inspection records with zone IDs, dates, anomaly types, severity
- compliance_docs: OSHA safety standards (1910.147, 1926 Subpart Q)
- historical_baselines: normal operating baselines per zone and equipment type

Session context (what user asked before):
{session_context_summary}

Classify this query:
"{query}"

Rules:
- COMPLIANCE_LOOKUP: regulatory/safety procedure/standard questions
- HISTORICAL_LOOKUP: past records, trends, baselines, recurring patterns
- ANOMALY_QUERY: current or recent anomaly status for a specific zone/equipment
- OUT_OF_SCOPE: no relevant data exists in any collection
```

**Tool definition for structured output (Anthropic tool_use):**
```python
classifier_tool = {
    "name": "classify_query",
    "description": "Classify the inspection query and extract spatial entities",
    "input_schema": {
        "type": "object",
        "properties": {
            "query_type": {"type": "string", "enum": ["COMPLIANCE_LOOKUP", "HISTORICAL_LOOKUP", "ANOMALY_QUERY", "OUT_OF_SCOPE"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "extracted_zone": {"type": ["string", "null"]},
            "extracted_equipment": {"type": ["string", "null"]},
            "extracted_time_ref": {"type": ["string", "null"]},
            "reasoning": {"type": "string"}
        },
        "required": ["query_type", "confidence", "reasoning"]
    }
}
```

---

## Entity Extraction

Runs for all queries regardless of which classification path fired.

**Zone extraction:**
- Pattern: match "Zone [A-E]" (case-insensitive)
- Fallback: use `session_context["last_zone"]` if no explicit mention
- If session has no context either: `extracted_zone = None`

**Equipment extraction:**
- Match against known equipment types list
- Partial match allowed ("hvac" → "rooftop-hvac")
- Fallback: `session_context["last_equipment"]`

**Time reference extraction:**
- Match: "last month", "last week", "last quarter", "in [month] [year]", "past N days/months"
- Store as raw string — conversion to `flight_date_after` happens in `assistant.py`
- Fallback: `session_context["last_time_ref"]`

---

## Handoff Interface to Retrieval

The classifier outputs `ClassificationResult`. The `SiteIntelligenceAgent.ask()` method converts it:

```python
classification = classify(query, session_ctx)

# Build spatial filter from extracted entities
where_filter = build_spatial_filter(
    zone_id=classification.extracted_zone,
    flight_date_after=parse_time_ref(classification.extracted_time_ref),
    severity=None  # don't filter severity by default — return all, let confidence decide
)

# Only search the collections the classifier selected
target_collections = {k: v for k, v in self.collections.items()
                      if k in classification.collections_to_search}

results = retrieve(query, target_collections, where_filter=where_filter)

# Fallback: if filtered retrieval returns nothing, retry without filter
if not results and where_filter:
    results = retrieve(query, self.collections)  # full corpus, no filter
    # log fallback in pipeline_trace
```

---

## OUT_OF_SCOPE Handling

When classifier returns `OUT_OF_SCOPE`:
- Skip retrieval entirely
- Skip LLM call entirely
- Return a programmatic escalation message (same LOW path from Phase 1):
  ```
  "This query is outside the scope of the Site Intelligence Agent.
   The system covers: drone inspection records, OSHA compliance standards,
   and historical baselines for Zones A-E.
   Please consult [appropriate resource] for this type of question."
  ```
- Never hallucinate. This is a safety constraint, not a UX choice.

---

## Failure Modes and Mitigations

| Failure Mode | When It Happens | Mitigation |
|--------------|----------------|-----------|
| Misclassifies ANOMALY_QUERY as HISTORICAL_LOOKUP | Query mentions past tense: "what was found" | Both types search inspection_records — impact is minimal |
| Misclassifies compliance as anomaly | OSHA cited in anomaly context | Confidence < 0.7 → log warning; both collections searched as fallback |
| Entity extraction fails (zone not recognized) | Abbreviations, typos | Fallback to session context; if still None, run full-corpus retrieval |
| LLM classifier times out | API outage | Catch exception, fall back to rule-based only; log degradation |

---

## Testing the Classifier

Unit tests in `tests/test_classifier.py`:

```python
# Rule-based path
assert classify("What does OSHA 1926 say about fall protection?").query_type == "COMPLIANCE_LOOKUP"
assert classify("What anomalies are in Zone C?").extracted_zone == "Zone-C"
assert classify("What is the weather in Austin?").query_type == "OUT_OF_SCOPE"

# Entity extraction
r = classify("What HIGH severity anomalies were found in Zone B last month?")
assert r.extracted_zone == "Zone-B"
assert r.extracted_time_ref is not None

# Session fallback
ctx = {"last_zone": "Zone-D", "last_equipment": None, "last_time_ref": None}
r = classify("What about last month?", session_context=ctx)
assert r.extracted_zone == "Zone-D"  # resolved from session
```
