"""
confidence.py
-------------
Confidence scoring and routing logic.

Three confidence levels:
  HIGH    : top result similarity > 0.75, at least 2 results above 0.60
  PARTIAL : top result similarity 0.50-0.75, OR conflict detected between sources
  LOW     : top result similarity < 0.50, OR zero results returned

These thresholds are product decisions, not engineering ones.
In a safety-critical field context, tune conservatively:
false positives (confident wrong answers) are more dangerous than
false negatives (unnecessary escalations).
"""

import os
from dotenv import load_dotenv
from src.retriever import detect_conflicts

load_dotenv()

HIGH_THRESHOLD = float(os.getenv("CONFIDENCE_HIGH_THRESHOLD", 0.75))
PARTIAL_THRESHOLD = float(os.getenv("CONFIDENCE_PARTIAL_THRESHOLD", 0.50))


def score_confidence(
    results: list[dict],
    high_threshold: float = None,
    partial_threshold: float = None,
) -> dict:
    """
    Given retrieved results, return a confidence assessment.

    Returns:
        {
            "level": "HIGH" | "PARTIAL" | "LOW",
            "reason": str,
            "top_score": float,
            "conflict_detected": bool
        }
    """
    high_t = high_threshold if high_threshold is not None else HIGH_THRESHOLD
    partial_t = partial_threshold if partial_threshold is not None else PARTIAL_THRESHOLD

    if not results:
        return {
            "level": "LOW",
            "reason": "No relevant documents found in the corpus.",
            "top_score": 0.0,
            "conflict_detected": False
        }

    top_score = results[0]["score"]
    conflict = detect_conflicts(results)

    # LOW: nothing useful found
    if top_score < partial_t:
        return {
            "level": "LOW",
            "reason": f"Best match similarity ({top_score:.2f}) is below the minimum threshold ({partial_t}). Insufficient context to answer reliably.",
            "top_score": top_score,
            "conflict_detected": conflict
        }

    # PARTIAL: conflict between sources, even if scores are okay
    if conflict:
        sources = list(set(r["collection"] for r in results[:3]))
        return {
            "level": "PARTIAL",
            "reason": f"Conflicting information detected across sources: {', '.join(sources)}. Top match similarity: {top_score:.2f}.",
            "top_score": top_score,
            "conflict_detected": True
        }

    # PARTIAL: score in the middle range
    if top_score < high_t:
        return {
            "level": "PARTIAL",
            "reason": f"Match similarity ({top_score:.2f}) is below high-confidence threshold ({high_t}). Answer may be incomplete.",
            "top_score": top_score,
            "conflict_detected": False
        }

    # HIGH: strong match, no conflict
    strong_results = [r for r in results if r["score"] >= partial_t]
    if len(strong_results) >= 2:
        return {
            "level": "HIGH",
            "reason": f"Strong match found (similarity: {top_score:.2f}). {len(strong_results)} supporting results above {partial_t} threshold.",
            "top_score": top_score,
            "conflict_detected": False
        }

    # HIGH but only one strong result — still acceptable
    return {
        "level": "HIGH",
        "reason": f"Strong match found (similarity: {top_score:.2f}).",
        "top_score": top_score,
        "conflict_detected": False
    }
