"""
retriever.py
------------
Handles query embedding and retrieval from all three Chroma collections.
Returns ranked results with source metadata and similarity scores.
"""

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
TOP_K = int(os.getenv("TOP_K_RESULTS", 5))

HVAC_COLLECTIONS = ["osha", "manuals", "job_history"]
DRONE_COLLECTIONS = ["inspection_records", "historical_baselines", "compliance_docs"]

# Collections treated as authoritative per domain (used by detect_conflicts)
AUTHORITATIVE_BY_DOMAIN = {
    "hvac": {"osha", "manuals"},
    "drone": {"inspection_records", "historical_baselines"},
}


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_collections(embeddings, domain: str = "hvac") -> dict:
    """
    Load Chroma collections for the given domain.
    domain="hvac"  → Phase 1 collections (osha, manuals, job_history)
    domain="drone" → Phase 2 collections (inspection_records, historical_baselines, compliance_docs)
    """
    names = HVAC_COLLECTIONS if domain == "hvac" else DRONE_COLLECTIONS
    collections = {}
    for name in names:
        try:
            collections[name] = Chroma(
                collection_name=name,
                embedding_function=embeddings,
                persist_directory=CHROMA_PERSIST_DIR
            )
        except Exception as e:
            print(f"[WARN] Could not load collection '{name}': {e}")
    return collections


def build_spatial_filter(
    zone_id: str = None,
    flight_date_after: str = None,
    severity: str = None,
) -> dict | None:
    """
    Build a Chroma where_filter from spatial parameters.
    Returns None if no parameters are provided (no filtering — Phase 1 behavior).

    Args:
        zone_id: e.g. "Zone-C"
        flight_date_after: ISO date string lower bound e.g. "2025-07-01"
        severity: "HIGH", "MEDIUM", or "LOW"
    """
    conditions = []
    if zone_id:
        conditions.append({"zone_id": {"$eq": zone_id}})
    if flight_date_after:
        # Chroma requires numeric types for $gte. Convert ISO date to YYYYMMDD int.
        date_int = int(flight_date_after.replace("-", ""))
        conditions.append({"flight_date_int": {"$gte": date_int}})
    if severity:
        conditions.append({"severity": {"$eq": severity}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def _strip_date_filter(where_filter: dict) -> dict | None:
    """Remove flight_date_int conditions from a filter (for historical_baselines which lacks that field)."""
    if not where_filter:
        return None
    if "flight_date_int" in str(where_filter):
        if "$and" in where_filter:
            conditions = [c for c in where_filter["$and"] if "flight_date_int" not in c]
            if not conditions:
                return None
            return conditions[0] if len(conditions) == 1 else {"$and": conditions}
        # Top-level date-only filter — nothing left after stripping
        if list(where_filter.keys()) == ["flight_date_int"]:
            return None
    return where_filter


def retrieve(
    query: str,
    collections: dict,
    top_k: int = TOP_K,
    where_filter: dict = None,
) -> list[dict]:
    """
    Retrieve top-k results from all collections.
    Returns a list of dicts with: content, source, collection, score, metadata.
    Sorted by similarity score descending.

    where_filter is applied only to inspection_records — compliance_docs and
    historical_baselines don't carry zone_id on every chunk.
    """
    results = []

    for collection_name, vectorstore in collections.items():
        try:
            kwargs = {"k": top_k}
            if where_filter:
                if collection_name == "inspection_records":
                    kwargs["filter"] = where_filter
                elif collection_name == "historical_baselines":
                    # Baselines have zone_id but not flight_date_int — strip date conditions
                    kwargs["filter"] = _strip_date_filter(where_filter)
            docs_and_scores = vectorstore.similarity_search_with_score(query, **kwargs)
            for doc, score in docs_and_scores:
                # Chroma returns L2 distance for unit-normalized vectors (sentence-transformers).
                # Correct conversion to cosine similarity: cosine_sim = 1 - (L2_dist² / 2)
                similarity = max(0.0, 1.0 - (score ** 2) / 2)
                results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "unknown"),
                    "collection": collection_name,
                    "score": round(similarity, 4),
                    "metadata": doc.metadata,
                })
        except Exception as e:
            print(f"[WARN] Retrieval failed for collection '{collection_name}': {e}")

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k * len(collections)]


def detect_conflicts(results: list[dict], domain: str = "hvac") -> bool:
    """
    Conflict detection: two heuristics checked in order.

    1. Cross-collection conflict (top 3): results from different authoritative
       collections with scores within 0.15 of each other.
       HVAC: catches OSHA vs manual disagreements.
       Drone: catches compliance_docs vs historical_baselines disagreements.

    2. Within-collection version conflict (top 6): multiple source files from
       the same collection with their best scores within 0.15 of each other.
       Catches two versions of the same manual or two inspection records with
       conflicting findings.
    """
    if len(results) < 2:
        return False

    authoritative = AUTHORITATIVE_BY_DOMAIN.get(domain, {"osha", "manuals"})
    # Drone inspection results spread across collections more than OSHA/manuals —
    # use a wider window so inspection_records can compete with historical_baselines.
    cross_window = 6 if domain == "drone" else 3

    # --- Heuristic 1: cross-collection (authoritative sources only) ---
    top_auth = [r for r in results[:cross_window] if r["collection"] in authoritative]
    if len(top_auth) >= 2:
        auth_collections = set(r["collection"] for r in top_auth)
        auth_scores = [r["score"] for r in top_auth]
        if len(auth_collections) > 1 and (max(auth_scores) - min(auth_scores)) < 0.15:
            return True

    # --- Heuristic 2: within-collection version conflict ---
    top6 = results[:6]
    by_collection: dict[str, dict[str, float]] = {}
    for r in top6:
        col = r["collection"]
        src = r["source"]
        if col not in by_collection:
            by_collection[col] = {}
        if src not in by_collection[col] or r["score"] > by_collection[col][src]:
            by_collection[col][src] = r["score"]

    for col, source_scores in by_collection.items():
        if len(source_scores) > 1:
            scores = list(source_scores.values())
            if max(scores) >= 0.50 and (max(scores) - min(scores)) < 0.15:
                return True

    return False
