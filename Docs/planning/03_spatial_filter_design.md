# Spatial Filter Design
**Phase 2 · src/retriever.py additions**

---

## The Problem

Phase 1 retrieval is full-corpus: every query searches all chunks across all documents. For drone inspection, this is insufficient — "What anomalies are in Zone C?" should only retrieve Zone C records, not Zone A and Zone B records that happened to mention Zone C in passing.

The fix: store spatial fields as Chroma document metadata, then pass a `where_filter` to Chroma's similarity search. This restricts the candidate set before cosine similarity ranking runs.

---

## How Chroma Metadata Filtering Works

Chroma supports a `filter` parameter (called `where` in older versions) on `similarity_search_with_score()`.

```python
# Without filter — searches all documents
docs = vectorstore.similarity_search_with_score(query, k=5)

# With filter — only documents where metadata matches the condition
docs = vectorstore.similarity_search_with_score(
    query,
    k=5,
    filter={"zone_id": {"$eq": "Zone-C"}}
)
```

**Supported operators:** `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`

**Compound filters:**
```python
# Zone C AND flight_date after July 1, 2025
filter = {
    "$and": [
        {"zone_id": {"$eq": "Zone-C"}},
        {"flight_date": {"$gte": "2025-07-01"}}
    ]
}
```

**Critical requirement:** The metadata fields must exist on the Chroma documents at ingest time. If `zone_id` is not stored as a metadata field, the filter silently returns 0 results. This is why `ingest.py` must call `enrich_inspection_metadata()` before adding documents to Chroma.

---

## Changes to retriever.py

### 1. `retrieve()` — add optional `where_filter` parameter

```python
def retrieve(
    query: str,
    collections: dict,
    top_k: int = TOP_K,
    where_filter: dict = None     # NEW — None means no filter (Phase 1 behavior preserved)
) -> list[dict]:
    all_results = []
    for collection_name, vectorstore in collections.items():
        try:
            kwargs = {"k": top_k}
            if where_filter and collection_name == "inspection_records":
                # Only apply spatial filter to inspection_records
                # compliance_docs and historical_baselines don't have zone_id
                kwargs["filter"] = where_filter
            docs_and_scores = vectorstore.similarity_search_with_score(query, **kwargs)
            ...
```

**Why only apply filter to inspection_records:**
- `compliance_docs` has no `zone_id` metadata — filtering would return 0 results
- `historical_baselines` has `zone_id` but may need to be searched broadly for baseline comparisons
- Apply zone filter to baselines only if the classifier signals `retrieval_strategy == "filtered"` (explicit zone comparison query)

### 2. `build_spatial_filter()` — new helper function

```python
def build_spatial_filter(
    zone_id: str = None,
    flight_date_after: str = None,   # ISO date string: "2025-07-01"
    severity: str = None             # "HIGH", "MEDIUM", or "LOW"
) -> dict | None:
    """
    Build a Chroma where_filter from spatial parameters.
    Returns None if no parameters provided (no filtering).
    """
    conditions = []

    if zone_id:
        conditions.append({"zone_id": {"$eq": zone_id}})

    if flight_date_after:
        conditions.append({"flight_date": {"$gte": flight_date_after}})

    if severity:
        conditions.append({"severity": {"$eq": severity}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}
```

### 3. `load_collections()` — add `domain` parameter

```python
HVAC_COLLECTIONS = ["osha", "manuals", "job_history"]
DRONE_COLLECTIONS = ["inspection_records", "compliance_docs", "historical_baselines"]

def load_collections(embeddings, domain: str = "hvac") -> dict:
    """
    domain="hvac"  → loads Phase 1 collections (backward-compatible default)
    domain="drone" → loads Phase 2 drone inspection collections
    """
    names = HVAC_COLLECTIONS if domain == "hvac" else DRONE_COLLECTIONS
    ...
```

---

## Time Reference → Date Conversion

The classifier extracts `extracted_time_ref` as a raw string ("last month", "August 2025"). Before passing to `build_spatial_filter()`, convert to an ISO date string.

This conversion lives in `assistant.py`, not `retriever.py` — the retriever only deals with explicit date strings.

```python
def parse_time_ref(time_ref: str, as_of: str = None) -> str | None:
    """
    Convert natural language time reference to ISO date for flight_date_after filter.
    as_of: reference date (defaults to today). Useful for testing.

    Examples:
      "last month"    → first day of previous calendar month
      "last quarter"  → first day of previous quarter
      "August 2025"   → "2025-08-01"
      "past 90 days"  → today - 90 days
      None            → None (no date filter)
    """
    ...
```

---

## Fallback When Filter Returns No Results

If `where_filter` is applied and retrieval returns 0 results, the agent must not silently return an empty response. Fallback sequence:

1. Log in `pipeline_trace`: `{"filter_applied": filter, "filter_result_count": 0, "fallback": "full_corpus"}`
2. Retry `retrieve()` with the same query but no `where_filter`
3. If fallback also returns 0 results → LOW confidence → escalate

The fallback retry must be transparent in the UI: show a badge "Spatial filter applied — no zone-specific results found, showing full corpus results."

---

## Verification

After ingest, verify metadata exists before building spatial filtering:

```python
import chromadb
client = chromadb.PersistentClient(path="./data/chroma_db")
col = client.get_collection("inspection_records")
peek = col.peek(5)
# Must see zone_id, flight_date, severity in each record's metadata
assert "zone_id" in peek["metadatas"][0]
assert "flight_date" in peek["metadatas"][0]
assert "severity" in peek["metadatas"][0]
```

After spatial filter is implemented:

```python
from src.retriever import retrieve, build_spatial_filter, load_collections, get_embeddings
embeddings = get_embeddings()
collections = load_collections(embeddings, domain="drone")
f = build_spatial_filter(zone_id="Zone-C")
results = retrieve("What anomalies were found?", collections, where_filter=f)
# All inspection_records results must be Zone-C
inspection_results = [r for r in results if r["collection"] == "inspection_records"]
assert all(r["metadata"]["zone_id"] == "Zone-C" for r in inspection_results)
```
