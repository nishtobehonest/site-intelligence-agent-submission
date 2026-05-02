"""
degradation.py
--------------
Graceful degradation routing. The core differentiator of this system.

Three routing paths based on confidence level:

HIGH    -> Return answer with source citations
PARTIAL -> Return answer WITH explicit conflict flag surfacing both sources
LOW     -> Return escalation message: what was found, what was not, recommend calling office

This is a product design layer, not just engineering logic.
The routing decisions here determine whether the system is trustworthy
enough for enterprise field operators to actually use.
"""


def format_sources(results: list[dict], max_sources: int = 3) -> str:
    """Format source citations for inclusion in the answer."""
    seen = set()
    citations = []
    for r in results[:max_sources]:
        source = r.get("source", "unknown")
        collection = r.get("collection", "unknown")
        score = r.get("score", 0.0)
        key = f"{source}_{collection}"
        if key not in seen:
            seen.add(key)
            citations.append(f"  - [{collection.upper()}] {source} (relevance: {score:.2f})")
    return "\n".join(citations)


def format_conflict_sources(results: list[dict]) -> str:
    """Format conflicting sources for PARTIAL route."""
    by_collection = {}
    for r in results[:4]:
        col = r["collection"]
        if col not in by_collection:
            by_collection[col] = r
    lines = []
    for col, r in by_collection.items():
        snippet = r["content"][:200].replace("\n", " ").strip()
        lines.append(f"  [{col.upper()}] {r['source']}\n    Excerpt: \"{snippet}...\"")
    return "\n".join(lines)


def route(
    query: str,
    results: list[dict],
    confidence: dict,
    llm_answer: str = None
) -> dict:
    """
    Route the response based on confidence level.

    Returns a dict with:
        route_type: HIGH | PARTIAL | LOW
        response: the full text to show the technician
        sources: formatted source citations
        confidence_level: HIGH | PARTIAL | LOW
        escalate: bool (True if human review recommended)
    """
    level = confidence["level"]
    sources = format_sources(results)

    # --- HIGH CONFIDENCE ---
    if level == "HIGH":
        response = f"{llm_answer}\n\nSources:\n{sources}"
        return {
            "route_type": "HIGH",
            "response": response,
            "sources": sources,
            "confidence_level": "HIGH",
            "escalate": False
        }

    # --- PARTIAL CONFIDENCE (conflict or low-mid score) ---
    if level == "PARTIAL":
        conflict_sources = format_conflict_sources(results)
        if confidence["conflict_detected"]:
            conflict_notice = (
                "\n\n⚠️  SOURCES DISAGREE: Multiple documents returned conflicting information "
                "on this topic. Review both sources before acting:\n"
                f"{conflict_sources}\n\n"
                "Consult your supervisor or office before proceeding."
            )
        else:
            conflict_notice = (
                f"\n\n⚠️  LOW CONFIDENCE: This answer is based on partial context "
                f"(best match: {confidence['top_score']:.2f}). Verify before acting."
            )

        response = f"{llm_answer}{conflict_notice}\n\nSources:\n{sources}"
        return {
            "route_type": "PARTIAL",
            "response": response,
            "sources": sources,
            "confidence_level": "PARTIAL",
            "escalate": True
        }

    # --- LOW CONFIDENCE (escalation) ---
    partial_context = ""
    if results:
        best = results[0]
        snippet = best["content"][:300].replace("\n", " ").strip()
        partial_context = (
            f"\nClosest match found (relevance: {best['score']:.2f}):\n"
            f"  [{best['collection'].upper()}] {best['source']}\n"
            f"  \"{snippet}...\"\n"
            f"This match is below the minimum confidence threshold and should not be acted on alone."
        )

    response = (
        f"❌ INSUFFICIENT CONTEXT: I could not find reliable documentation to answer this query.\n\n"
        f"Query: \"{query}\"\n"
        f"Reason: {confidence['reason']}\n"
        f"{partial_context}\n\n"
        f"Recommended action: Contact your office or supervisor for guidance on this item."
    )

    return {
        "route_type": "LOW",
        "response": response,
        "sources": sources if results else "None",
        "confidence_level": "LOW",
        "escalate": True
    }
