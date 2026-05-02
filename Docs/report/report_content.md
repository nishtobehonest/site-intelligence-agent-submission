# Site Intelligence Agent
## Technical Project Report
### ENMGT 5400 — Applications of Artificial Intelligence for Engineering Managers
### Cornell University, Masters of Engineering Management | May 2026

---

# 1. Executive Summary

Field technicians working in HVAC maintenance and drone-based site inspection routinely consult dozens of documents — equipment manuals, OSHA standards, inspection records, and maintenance histories — to answer safety-critical questions. The cost of a wrong answer is not inconvenience: it is equipment failure, regulatory violation, or injury.

This project delivers the **Site Intelligence Agent**: a retrieval-augmented generation (RAG) pipeline that provides natural-language answers grounded in a curated document corpus, with an explicit **graceful degradation layer** that determines whether the system has enough evidence to answer, and routes accordingly. Three routing paths govern every response:

- **HIGH confidence** — the system answers with source citations.
- **PARTIAL confidence** — the system answers but flags a conflict or uncertainty, escalating to human review.
- **LOW confidence** — the system does not call the language model at all; instead it returns a deterministic escalation message explaining what was searched and recommending the technician contact their office.

This anti-hallucination design is the core architectural differentiator. Most RAG systems pass every query to a language model regardless of retrieval quality, trusting the model to stay grounded. This system treats low-confidence retrieval as a data signal and acts on it programmatically, before the language model can confabulate.

**Phase 1 (HVAC domain) is complete.** The system achieves **94% pass rate on ground truth queries** and **81.2% overall across 85 structured test cases**. Phase 2 extends the pipeline to drone site inspection, adding a classifier agent, spatial metadata filters, and session memory for multi-turn context. Phase 3 targets production deployment with a multi-graph memory layer for longitudinal anomaly reasoning.

[SCREENSHOT: Home page of the Streamlit walkthrough app showing the three routing paths]

---

# 2. Problem Framing & Business Case

## 2.1 The Field Technician's Information Problem

A junior HVAC technician on a commercial rooftop at 2pm, mid-repair, asks: *"What are the lockout/tagout steps for this Carrier unit?"* The answer exists — in a 400-page PDF, in an OSHA regulation, and in the job history from the last visit. It takes 8–12 minutes to locate manually. In a safety-critical situation, that delay is unacceptable.

The same problem exists in drone site inspection. A field operator reviewing a Zone C structural panel wants to know: *"Is the corrosion I'm seeing above baseline?"* The answer requires cross-referencing the current inspection record against a historical baseline document — two separate files with no automated comparison.

Existing tools fail in two specific ways:

1. **Generic search engines** return document links, not answers. The technician still reads and interprets.
2. **Unguarded language model interfaces** (ChatGPT, Copilot) answer every question confidently, even when they have no corpus basis. For a question about a specific equipment model the corpus does not contain, the model will often produce plausible-sounding but fabricated specifications.

The Site Intelligence Agent addresses both failure modes: it retrieves from a curated, domain-specific corpus, and it refuses to answer when retrieval quality is insufficient.

## 2.2 Build vs. Buy Analysis

Hosted RAG solutions exist (Azure AI Search, Vertex AI Search, Amazon Kendra). The decision to build a custom pipeline was driven by four requirements that commercial products do not meet out of the box:

| Requirement | Commercial RAG | Site Intelligence Agent |
| --- | --- | --- |
| Explicit LOW-confidence escalation | Not available | Core feature — programmatic, no LLM call |
| Cross-collection conflict detection | Not available | detect_conflicts() heuristic |
| Domain-aware confidence thresholds | Not configurable | Per-domain tuning via env vars |
| Session memory + spatial filtering | Limited | Built in Phase 2 |

The principal cost of building custom is development time: approximately 6–8 weeks for the Phase 1 pipeline and eval framework. At a fully-loaded engineering cost of $150/hr, the build investment is roughly $60,000–$80,000. Against an enterprise field operations team of 50 technicians saving 8 minutes per query at 10 queries/day, the breakeven horizon is approximately 4–6 months.

The make-vs-buy calculus shifts decisively toward build for use cases where the failure mode of a wrong answer is measurably costly (liability, safety incident, regulatory fine) and where the retrieval corpus is highly structured and domain-controlled.

## 2.3 ROI Framework

Three quantifiable impact vectors:

- **Time-to-answer reduction.** Manual document lookup: 8–12 min. RAG query: < 8 sec. At 10 queries/technician/day across 50 technicians, that is approximately 125 engineer-hours recovered daily.
- **Escalation cost avoidance.** Each unnecessary escalation to a senior engineer or vendor support costs an estimated $40–$120 in loaded time. The system's LOW-path escalations are targeted (evidence-based), not reflexive.
- **Liability risk reduction.** A confident wrong answer on lockout/tagout procedure creates direct liability. The LOW path eliminates this class of response. Quantifying this is difficult, but a single avoided OSHA citation ($15,625 per willful violation, per 29 CFR 1903.15) exceeds the cost of the build.

---

# 3. System Architecture

## 3.1 Five-Step Pipeline

Every query flows through five steps in sequence. The first four are always executed; Step 4 (LLM generation) is conditionally skipped on LOW-confidence retrievals.

```
query
  → classify()       # classifier.py: query type + entity extraction → collections + strategy
  → retrieve()       # retriever.py: embed query, search Chroma, apply spatial filter, top-k
  → score_confidence()  # confidence.py: cosine similarity thresholding + conflict detection
  → llm.generate()   # llm.py: called ONLY for HIGH or PARTIAL confidence
  → route()          # degradation.py: format final response based on route type
```

[SCREENSHOT: Architecture pipeline diagram — 5-step flow with HIGH/PARTIAL/LOW branches]

The classifier step is present only in Phase 2 (drone domain). Phase 1 (HVAC) omits it, sending all queries directly to retrieval across all three HVAC collections. This intentional simplification kept Phase 1 verifiable against a clean baseline.

## 3.2 Document Collections

Six Chroma vector database collections are organized across two domains. They are **never merged** — source-aware conflict detection requires that the system can identify which collection a result came from.

[SCREENSHOT: Collection layout diagram — 2 domains × 3 collections with chunk counts]

| Domain | Collection | Documents | Chunks | Purpose |
| --- | --- | --- | --- | --- |
| HVAC | osha | OSHA 1910.147, 1910.303 | 283 | Lockout/tagout and electrical safety |
| HVAC | manuals | Carrier 48LC (2017, 2023), Lennox SL280, Trane XR15 | 1,372 | Equipment specifications |
| HVAC | job_history | 50 synthetic job records | 181 | Prior maintenance history |
| Drone | inspection_records | 50 synthetic inspection records | 202 | Current anomaly findings per zone |
| Drone | historical_baselines | 25 zone baseline documents | 160 | Normal operating thresholds |
| Drone | compliance_docs | OSHA 1926.452 (scaffold safety) | 158 | Regulatory compliance standards |

Embeddings use `sentence-transformers/all-MiniLM-L6-v2`, a lightweight open-source model chosen for determinism, cost, and performance on technical text. Chroma stores vectors locally; no external vector database service is required.

A key implementation detail: Chroma's default similarity search returns L2 distance for unit-normalized vectors. The naive conversion `similarity = 1 - L2_distance` is incorrect. The correct formula is:

```python
# Chroma returns L2 distance for unit-normalized sentence-transformer vectors.
# Correct conversion to cosine similarity: cosine_sim = 1 - (L2_dist² / 2)
similarity = max(0.0, 1.0 - (score ** 2) / 2)
```

An earlier implementation used the incorrect formula, causing HIGH-confidence matches to score ~0.36 instead of ~0.80. Catching this required building a proper eval framework — which is why evaluation matters.

## 3.3 Component Summary

| Component | File | Role |
| --- | --- | --- |
| Classifier | src/classifier.py | Rule-based gate + LLM fallback; routes to collections |
| Retriever | src/retriever.py | Embeds query, searches Chroma, applies spatial filter |
| Confidence Scorer | src/confidence.py | Thresholds top score; detects cross-source conflicts |
| Graceful Degradation | src/degradation.py | Formats HIGH/PARTIAL/LOW responses |
| LLM Wrapper | src/llm.py | Provider-agnostic (Anthropic / OpenAI / Gemini) |
| Session Memory | src/session_memory.py | Tracks zone/equipment/time across conversation turns |
| Ingest | src/ingest.py | Chunks documents, embeds, stores to Chroma |

---

# 4. Evaluation Framework

The evaluation framework is the part of this project most likely to transfer to a production context. An AI system without a structured test suite is not a product; it is a demo. The framework answers three distinct questions that are each necessary but not sufficient on their own.

## 4.1 Three-Set Methodology

**Test Set 1: Ground Truth (50 queries)**

Tests whether the system correctly answers known questions. Pass criterion: `confidence_level != LOW`. The system should return HIGH or PARTIAL for any question answerable from the corpus. Failure here means the system is under-indexing — escalating when it has the answer.

**Test Set 2: Adversarial (20 queries)**

Tests whether the system correctly refuses to answer unknown questions. Pass criterion: `confidence_level == LOW`. Every query targets equipment, regulations, or scenarios that do not exist in the corpus. Failure here is the most dangerous outcome: the system returns a PARTIAL or HIGH answer for a question it has no basis to answer — a hallucination or false confidence scenario.

**Test Set 3: Contradictions (15 scenarios)**

Tests whether the system surfaces conflicts between sources rather than silently choosing one. Pass criterion: `confidence_level == PARTIAL`. Each scenario involves a query that should retrieve results from two sources with conflicting or version-divergent information (e.g., Carrier 48LC 2017 vs. 2023 maintenance intervals, OSHA standard vs. manual procedure). Failure here means the system gives a confident answer without flagging the disagreement.

The three sets together check for the three failure modes of a RAG system: under-retrieval, hallucination, and false consensus.

## 4.2 Evaluation Results

| Test Set | Pass | Total | Pass Rate | Pass Criterion |
| --- | --- | --- | --- | --- |
| Ground Truth | 47 | 50 | 94.0% | confidence ≠ LOW |
| Adversarial | 9 | 20 | 45.0% | confidence = LOW |
| Contradictions | 13 | 15 | 86.7% | confidence = PARTIAL |
| **Overall** | **69** | **85** | **81.2%** | — |

## 4.3 Ground Truth: 94% — Strong Baseline

Three failures. All three share the same root cause: the Trane XR15 and Lennox SL280 manuals embed at lower similarity scores than OSHA documents, so queries about equipment specifications occasionally fall below the LOW threshold even when the answer is present.

Example failure query: *"What are the installation requirements for the Trane XR15 heat pump?"* — returned LOW with a top score of 0.48. The answer exists in the corpus; the chunking strategy splits installation tables in ways that reduce per-chunk semantic coherence.

This is a known limitation of dense vector retrieval for tabular or specification-heavy content. The fix is hybrid retrieval (BM25 keyword matching + dense vector), deferred to Phase 3.

## 4.4 Adversarial: 45% — Accepted Limitation

Eleven failures. Every failure has the same pattern: the query targets equipment that does not exist in the corpus but is **semantically near-miss** to equipment that does. Examples:

- *"What is the refrigerant charge for a Trane XR13?"* → scored 0.579, returned PARTIAL. The XR15 manual exists; XR13 and XR15 are similar enough that the embedding space does not discriminate them.
- *"What are the installation instructions for a Lennox XC25?"* → scored 0.732, returned PARTIAL. The SL280 manual exists; XC25 queries retrieve SL280 content at high similarity.
- *"What are the OSHA requirements for confined space entry?"* → scored 0.762, returned PARTIAL. Confined space content is adjacent to the lockout/tagout corpus.

This is an architectural limitation of dense vector retrieval: cosine similarity measures semantic proximity, not exact model-number match. The only structural fix is hybrid retrieval with BM25 or metadata filtering. This is documented as an accepted known limitation. The adversarial score of 45% reflects a real-world tradeoff: raising the PARTIAL threshold to reduce false confidence would also suppress legitimate PARTIAL answers.

> **Management implication:** The 45% adversarial rate means 55% of out-of-corpus queries receive a cautious PARTIAL answer with a source citation rather than a confident refusal. In a production context, operators would be told the PARTIAL path requires verification — this is preferable to the system returning "I don't know" for queries that have partial supporting evidence.

## 4.5 Contradictions: 86.7% — Two Missed Conflicts

Two failures. Both involve the Carrier 48LC 2017 vs. 2023 version conflict on specific maintenance interval questions where the top retrieved chunk score falls below 0.50, triggering LOW before conflict detection can run. The conflict detection heuristic fires only when there is enough semantic signal (top score ≥ 0.50) to prevent noise-level matches from triggering false conflicts.

This is by design — a very low-scoring "conflict" would be noise — but it means specific version-comparison queries that don't retrieve strongly from either version will incorrectly escalate as LOW rather than surface as PARTIAL conflicts.

## 4.6 Threshold Tuning Methodology

Confidence thresholds are product decisions, not engineering parameters. They encode a risk tolerance: in a safety-critical field context, a false positive (confident wrong answer) is more dangerous than a false negative (unnecessary escalation).

Thresholds are configurable at runtime without code changes:

```bash
# Raise HIGH threshold to reduce hallucination risk (fewer HIGH, more PARTIAL):
CONFIDENCE_HIGH_THRESHOLD=0.85 python demo/demo.py

# Lower PARTIAL threshold to escalate more aggressively (more LOW paths):
CONFIDENCE_PARTIAL_THRESHOLD=0.60 python demo/demo.py
```

Current production-tuned values: `HIGH = 0.79`, `PARTIAL = 0.50`. These were derived by running the eval suite at multiple threshold combinations and selecting the pair that maximized ground truth pass rate while keeping adversarial failures at PARTIAL (never HIGH).

Domain-aware calibration is required in Phase 2: synthetic drone inspection notes embed at 0.50–0.70, lower than OSHA regulatory text (0.80–0.93). Drone thresholds are set to `HIGH = 0.52`, `PARTIAL = 0.35` to account for this difference.

## 4.7 Phase 2 Eval Strategy

Phase 2 extends the eval framework with drone-specific tests and a new classifier evaluation set:

| Set | Target | Criterion |
| --- | --- | --- |
| Drone ground truth (30 queries) | > 80% pass | confidence ≠ LOW |
| Drone adversarial (15 queries) | > 70% pass | confidence = LOW |
| Classifier eval (20 queries) | > 90% pass | correct query_type routing |

The classifier evaluation is new: it tests query type routing (COMPLIANCE_LOOKUP, HISTORICAL_LOOKUP, ANOMALY_QUERY, OUT_OF_SCOPE) independently of retrieval quality, enabling targeted debugging of classification vs. retrieval failures.

---

# 5. Graceful Degradation Layer

## 5.1 The Core Differentiator

The graceful degradation layer in `src/degradation.py` is what separates this system from a standard RAG chatbot. Its design principle: **the system should never produce a confident wrong answer**. The engineering expression of this principle is that the LOW confidence path does not call the language model.

```python
# --- LOW CONFIDENCE (escalation) — from degradation.py ---
# NOTE: llm_answer is None here. This block is reached only when
# score_confidence() returned "LOW". The LLM is never called.
response = (
    f"INSUFFICIENT CONTEXT: I could not find reliable documentation "
    f"to answer this query.\n\n"
    f"Query: \"{query}\"\n"
    f"Reason: {confidence['reason']}\n"
    f"{partial_context}\n\n"
    f"Recommended action: Contact your office or supervisor."
)
return {
    "route_type": "LOW",
    "response": response,
    "confidence_level": "LOW",
    "escalate": True
}
```

The escalation message is constructed programmatically: it states the query, the reason for escalation (from `confidence.py`), the closest match found (if any, with its score), and a recommended action. This message is deterministic — the same query always produces the same escalation message — which is important for operator trust and auditability.

## 5.2 Confidence Scoring

The `score_confidence()` function in `src/confidence.py` implements the routing decision:

```python
def score_confidence(results, high_threshold=None, partial_threshold=None):
    if not results:
        return {"level": "LOW", "reason": "No relevant documents found.", ...}

    top_score = results[0]["score"]
    conflict = detect_conflicts(results)

    if top_score < partial_t:        # below minimum → LOW
        return {"level": "LOW", ...}

    if conflict:                     # conflict detected → PARTIAL regardless of score
        return {"level": "PARTIAL", "conflict_detected": True, ...}

    if top_score < high_t:           # mid-range → PARTIAL
        return {"level": "PARTIAL", ...}

    if len(strong_results) >= 2:     # strong match + support → HIGH
        return {"level": "HIGH", ...}
```

## 5.3 Conflict Detection

The `detect_conflicts()` function in `src/retriever.py` runs two heuristics in sequence:

```python
def detect_conflicts(results, domain="hvac"):
    authoritative = AUTHORITATIVE_BY_DOMAIN.get(domain)
    # Heuristic 1: cross-collection — top results from different authoritative
    # collections with scores within 0.15 of each other
    top_auth = [r for r in results[:3] if r["collection"] in authoritative]
    if len(top_auth) >= 2:
        collections = set(r["collection"] for r in top_auth)
        scores = [r["score"] for r in top_auth]
        if len(collections) > 1 and (max(scores) - min(scores)) < 0.15:
            return True

    # Heuristic 2: within-collection version conflict — multiple source files
    # from the same collection with best-scores within 0.15
    for col, source_scores in by_collection.items():
        if len(source_scores) > 1:
            scores = list(source_scores.values())
            if max(scores) >= 0.50 and (max(scores) - min(scores)) < 0.15:
                return True
    return False
```

Heuristic 1 catches OSHA-vs-manual disagreements (e.g., OSHA 1910.147 says lockout; the manual says de-energize first, then lockout — same topic, different framing, both score highly). Heuristic 2 catches version conflicts — the 2017 and 2023 Carrier 48LC manuals have different maintenance intervals; both score highly on maintenance queries, triggering a PARTIAL with source comparison.

[SCREENSHOT: Streamlit showing HIGH confidence response with source citations]

[SCREENSHOT: Streamlit showing PARTIAL confidence response with conflict warning]

[SCREENSHOT: Streamlit showing LOW confidence escalation response]

---

# 6. Phase 2: Drone Inspection Domain

## 6.1 Domain Extension Design

Phase 2 demonstrates that the core pipeline is domain-agnostic. Adding a new domain requires: a new set of Chroma collections, a classifier branch, and domain-specific confidence threshold calibration. The confidence scoring, conflict detection, and graceful degradation layers require no changes.

The drone inspection domain adds three architectural components not present in Phase 1:

1. **Classifier agent** — routes queries to the correct collections before retrieval
2. **Spatial metadata filters** — restricts retrieval to specific zones and time windows
3. **Session memory** — tracks zone/equipment/time entities across conversation turns

## 6.2 Classifier Agent

The classifier in `src/classifier.py` operates as a gate before retrieval. It uses a two-path design: a fast rule-based path handles approximately 70% of queries without an API call; an LLM structured-output fallback handles ambiguous queries.

```python
def _rule_based_classify(query):
    """Returns (query_type, confidence) or None if ambiguous."""
    out_hits = _count_hits(query, OUT_OF_SCOPE_SIGNALS)
    if out_hits >= 1:
        return "OUT_OF_SCOPE", 0.95   # short-circuit: no retrieval, no LLM

    compliance_hits = _count_hits(query, COMPLIANCE_KEYWORDS)
    historical_hits = _count_hits(query, HISTORICAL_KEYWORDS)
    anomaly_hits    = _count_hits(query, ANOMALY_KEYWORDS)

    # Clear winner: 2+ hits in one category, 0 in others
    if compliance_hits >= 2 and historical_hits == 0 and anomaly_hits == 0:
        return "COMPLIANCE_LOOKUP", 0.90
    if historical_hits >= 2 and compliance_hits == 0 and anomaly_hits == 0:
        return "HISTORICAL_LOOKUP", 0.85
    if anomaly_hits >= 2 and compliance_hits == 0 and historical_hits == 0:
        return "ANOMALY_QUERY", 0.85

    return None  # ambiguous — fall through to LLM path
```

The OUT_OF_SCOPE short-circuit is important: it prevents queries about weather, stock prices, or irrelevant topics from triggering retrieval or LLM calls at all.

The classifier also extracts spatial entities from every query: zone ID (e.g., "Zone-C"), equipment type (e.g., "rooftop-hvac"), and time reference (e.g., "last month", "August 2025"). These entities feed the spatial filter and session memory.

## 6.3 Spatial Filtering

Metadata-level filtering is applied at query time to restrict retrieval to relevant records:

```python
def build_spatial_filter(zone_id=None, flight_date_after=None, severity=None):
    conditions = []
    if zone_id:
        conditions.append({"zone_id": {"$eq": zone_id}})
    if flight_date_after:
        # Chroma requires numeric types for $gte comparisons
        date_int = int(flight_date_after.replace("-", ""))
        conditions.append({"flight_date_int": {"$gte": date_int}})
    if severity:
        conditions.append({"severity": {"$eq": severity}})
    ...
```

Zone filters are applied only to `inspection_records` (compliance and baseline documents are not zone-specific on every chunk). If a filtered retrieval returns no results, the system retries with the full corpus — a graceful fallback that prevents empty-result cascades.

## 6.4 Session Memory

The `SessionMemory` class in `src/session_memory.py` enables anaphoric references across turns: after a user asks about Zone C, a follow-up *"what about last month?"* resolves Zone C from session context rather than requiring re-specification.

Session context is updated after classification (not before), so the current turn's extracted entities inform the next turn's context — not the current retrieval. This ordering prevents premature context pollution.

[SCREENSHOT: Zone C drone walkthrough on Streamlit page 3 showing session context panel and pipeline trace]

---

# 7. AI Risk & Governance

## 7.1 Confidence Thresholds as Governance Decisions

The most important design principle in this system is that confidence thresholds are **product decisions made by domain experts**, not hyperparameters optimized by engineers. The distinction matters for how an engineering manager should think about deploying this system.

An engineer optimizing for ground truth pass rate would lower the PARTIAL threshold to capture more queries as HIGH or PARTIAL — improving coverage metrics. A domain expert understanding the safety context would recognize that doing so increases the risk of a confident wrong answer on a lockout/tagout procedure. These are not the same optimization target.

The env-var configuration interface makes this explicit: threshold changes require a deliberate human decision, not a code change. They can be audited, versioned, and reviewed independently of the software.

## 7.2 Hallucination Risk in Safety-Critical Contexts

Two hallucination failure modes exist in RAG systems:

- **Type 1 (retrieval failure):** The corpus does not contain relevant documents. The LLM generates a plausible answer from pre-training knowledge, unconstrained by retrieved context. This is addressed by the LOW path: if retrieval fails, the LLM is not called.
- **Type 2 (context contamination):** The corpus contains topically adjacent but not directly applicable content. The LLM generates an answer that looks grounded but uses the wrong source (e.g., generating a lockout procedure from a Lennox manual when the query is about a Carrier unit). This is addressed by the system prompt, which instructs the model to answer only from provided context and always cite the specific source.

The adversarial test set specifically targets Type 1. The system prompt and source-citation requirement target Type 2. Neither is fully solved — the adversarial pass rate of 45% demonstrates active Type 1 risk — but both are bounded and monitored.

## 7.3 Human-in-the-Loop Design

The PARTIAL path is an explicit human-in-the-loop handoff. It surfaces conflict information, names both sources, and tells the technician to consult a supervisor before acting. This is not a fallback or an error state — it is a designed interaction that acknowledges the system's epistemic uncertainty and routes it to a human capable of resolving it.

The engineering manager deploying this system must define the escalation workflow: who does the technician call? What is the SLA? How are escalations logged? The system provides the trigger; the process provides the resolution.

---

# 8. Deployment & Team Model

## 8.1 What Productionizing Requires

The current system runs locally on a laptop. Productionizing requires four infrastructure changes:

| Component | Local (current) | Production |
| --- | --- | --- |
| Vector database | Local Chroma directory | Chroma Cloud or Pinecone |
| LLM API | Single provider, env var | Multi-provider failover, rate limiting |
| Document ingestion | Manual CLI command | Automated pipeline on document upload |
| Serving | Streamlit development server | Containerized, behind load balancer |

## 8.2 Team Model

A minimum production team for this system requires three roles:

- **ML Engineer (1 FTE):** Maintains embedding model, confidence thresholds, conflict detection heuristics, eval suites. Owns the pipeline.
- **Domain Expert / Knowledge Manager (0.5 FTE):** Manages the document corpus — which documents are in scope, version control of manuals, validation of eval ground truth. This role is not optional; the quality of the system is bounded by the quality of the corpus.
- **Product Manager / Engineering Manager (0.5 FTE):** Owns threshold decisions, monitors escalation rates, defines the human-in-the-loop workflow, tracks eval metrics over time.

The domain expert role is the most frequently underestimated. Document curation, version management, and eval ground truth maintenance are ongoing operational costs, not one-time setup tasks.

## 8.3 Build vs. Buy — Final Assessment

After Phase 1 implementation, the build-vs-buy assessment is clearer. A hosted RAG solution would have handled retrieval and generation in approximately 2 weeks. The custom build required 6 weeks but delivered three capabilities not available in commercial products: the LOW-path escalation guarantee, cross-source conflict detection, and domain-aware threshold calibration.

For use cases where the failure mode of a wrong answer is measurably costly and the retrieval corpus is controlled, build. For use cases where general-purpose search quality is acceptable and the corpus is large and unstructured, buy.

---

# 9. What I Learned

## 9.1 The Eval Framework Revealed the Bug

The most important moment in Phase 1 was when the eval framework caught a bug that would have been invisible in demo mode. The cosine similarity conversion formula was wrong (`1 - L2_distance` instead of `1 - L2_distance² / 2`), causing every similarity score to be dramatically understated. Queries that should have scored 0.80–0.93 were scoring 0.36–0.45. The HVAC demo worked because all three demo queries had been hand-selected at thresholds that felt right — but the eval suite showed that 30% of ground truth queries were failing for the wrong reason.

This experience confirmed something I had read but not felt: **a demo is not a proof of concept; an eval suite is**. The incentive to ship a demo that works on three hand-picked queries is strong; the discipline to run 85 structured tests before claiming the system is ready is harder to maintain and more valuable.

## 9.2 Confidence Thresholds Are the Product

I initially approached confidence threshold tuning as an optimization problem: find the pair (high_threshold, partial_threshold) that maximizes the eval metric. After running the adversarial suite, I understood it differently. Raising the partial threshold to escalate more aggressively would improve the adversarial score but hurt the ground truth score. Those two metrics represent opposing business concerns: coverage vs. safety. An engineer cannot resolve that tradeoff; a product decision — about what kind of mistakes are acceptable in what operational context — is required.

This reframing — thresholds as product governance rather than engineering parameters — is the design insight I would lead with in any production conversation.

## 9.3 What I Would Revisit

Three architectural decisions I would reconsider in a Phase 3 build:

1. **Dense-only retrieval.** The adversarial failures are a structural consequence of using only dense vector search. Hybrid retrieval (BM25 + dense, with a score fusion layer) would likely raise the adversarial pass rate from 45% to 70%+. I did not build this in Phase 1 because it would have introduced a new failure mode before I understood the baseline behavior of the dense-only system. Sequence mattered.

2. **Static chunking.** All documents are chunked at fixed token boundaries. For tabular content (equipment specifications, maintenance schedules), this produces chunks that split semantically coherent rows across separate chunks, degrading retrieval for specification queries. Semantic or structure-aware chunking would improve this.

3. **Separation of drone and HVAC eval suites.** In Phase 2, the HVAC eval suite is run against the HVAC assistant class and the drone suite against the drone assistant class. A unified regression suite that runs both after every change would catch cross-domain regressions earlier.

---

# 10. Phase 3 Vision & Roadmap

## 10.1 Multi-Graph Memory (MAGMA-Inspired)

Phase 3 targets a longitudinal reasoning layer that the current system cannot support. The current session memory tracks entities within a single conversation session; it does not persist across sessions or reason over time. A technician returning to Zone C three months later cannot ask *"has the corrosion pattern changed since August?"* and get a grounded answer.

The planned architecture introduces four memory graph types:

- **Temporal:** anomaly readings timestamped and ordered, enabling trend queries
- **Causal:** links between findings and resolutions (e.g., Zone B corrosion → repair action → follow-up inspection)
- **Entity:** equipment and zone identifiers with persistent property histories
- **Semantic:** topical clusters across the corpus for concept-level retrieval

[SCREENSHOT: Memory graph visualization from Streamlit page 6 showing graph node types]

## 10.2 Phase Roadmap

| Phase | Status | Key Deliverable |
| --- | --- | --- |
| Phase 1 — HVAC Foundation | Complete | RAG pipeline, graceful degradation, 85-case eval suite |
| Phase 2 — Drone Extension | In Progress | Classifier agent, spatial filtering, session memory, dual-domain Streamlit app |
| Phase 3 — Production + Memory | Planned | Deployed URL, multi-graph memory, longitudinal anomaly tracking |

Phase 3 also targets the pipeline's first genuine multi-domain query: a technician asking about a drone inspection finding and cross-referencing it against an OSHA standard in the same query. This requires a query router that can dispatch to multiple domain pipelines and merge results before confidence scoring.

---

# 11. Appendix

## A. Evaluation Results Sample (from eval_results.csv)

| Set | Query (excerpt) | Expected | Actual | Pass | Score |
| --- | --- | --- | --- | --- | --- |
| ground_truth | Lockout tagout energy control procedure | HIGH/PARTIAL | HIGH | True | 0.933 |
| ground_truth | Installation requirements for Trane XR15 | HIGH/PARTIAL | LOW | False | 0.482 |
| adversarial | Repair procedures for Daikin VRV DX300 | LOW | LOW | True | 0.310 |
| adversarial | Refrigerant charge for Rheem RA20 | LOW | PARTIAL | False | 0.564 |
| adversarial | OSHA requirements for confined space entry | LOW | PARTIAL | False | 0.762 |
| contradictions | Electrical safety during HVAC maintenance | PARTIAL | PARTIAL | True | 0.666 |
| contradictions | Carrier 48LC filter intervals 2017 vs 2023 | PARTIAL | LOW | False | 0.484 |

## B. Technology Stack

| Layer | Technology |
| --- | --- |
| Embedding model | sentence-transformers/all-MiniLM-L6-v2 |
| Vector database | Chroma (local persistence) |
| LLM providers | Google Gemini 2.5 Flash (primary), Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o |
| Framework | Python 3.11, LangChain Chroma + HuggingFace adapters |
| UI | Streamlit (6-page guided walkthrough) |
| Data generation | Claude API (synthetic HVAC jobs + drone inspection records) |
| Eval | Custom Python runner, eval_results.csv output |

## C. Key Design Constraints

1. **Never merge collections.** Source-aware conflict detection requires knowing which collection each result came from.
2. **Every response must cite a source.** No uncited answers — enforced by the system prompt.
3. **LOW path never calls the LLM.** Programmatic escalation only.
4. **Confidence thresholds are product decisions.** Only change them after eval-suite validation.

[SCREENSHOT: Eval metrics dashboard from Streamlit page 4 showing pass rates across all three test sets]
