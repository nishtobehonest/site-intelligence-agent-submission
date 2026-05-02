"""
assistant.py
------------
Main assistant pipeline. Wires together retrieval, confidence scoring,
LLM generation, and graceful degradation routing.

Usage:
    from src.assistant import FieldServiceAssistant
    assistant = FieldServiceAssistant()
    result = assistant.ask("What is the lockout/tagout procedure for a Carrier RTU-48XL?")
    print(result["response"])
"""

import os
import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from src.retriever import get_embeddings, load_collections, retrieve, build_spatial_filter, detect_conflicts
from src.confidence import score_confidence
from src.degradation import route
from src.classifier import classify
from src import llm

load_dotenv()

SYSTEM_PROMPT = """You are a Site Intelligence Agent helping technicians, inspectors, and field engineers retrieve accurate information during a job.

Your rules:
1. Answer ONLY based on the provided context. Do not use outside knowledge.
2. If the context does not contain enough information to answer, say so explicitly. Do not guess or fabricate.
3. Always cite your source (document name or section) in your answer.
4. Use plain, direct language. Technicians need clear instructions, not corporate language.
5. If a procedure involves safety risks, flag it explicitly.
6. Keep answers concise. If the procedure has steps, use a numbered list.

If you cannot answer reliably from the context provided, respond with:
"I do not have sufficient information in my documents to answer this reliably. Please contact your office or supervisor."
"""


def build_context_block(results: list[dict], max_results: int = 5) -> str:
    """Format retrieved chunks into a context block for the LLM."""
    if not results:
        return "No relevant documents found."
    lines = []
    for i, r in enumerate(results[:max_results]):
        lines.append(f"[Source {i+1}: {r['collection'].upper()} | {r['source']} | relevance: {r['score']:.2f}]")
        lines.append(r["content"].strip())
        lines.append("")
    return "\n".join(lines)


OUT_OF_SCOPE_RESPONSE = (
    "This query is outside the scope of the Site Intelligence Agent. "
    "The system covers: drone inspection records, OSHA compliance standards, "
    "and historical baselines for Zones A–E. "
    "Please consult the appropriate resource for this type of question."
)

DRONE_SYSTEM_PROMPT = """You are a Site Intelligence Assistant helping engineers and inspectors query drone inspection data.

Your rules:
1. Answer ONLY from the provided context. Do not use outside knowledge.
2. Always cite your source (record ID, zone, or document section).
3. If the context is insufficient, say so clearly. Do not guess.
4. Flag safety-critical findings explicitly.
5. Be concise. Use bullet points or numbered lists for multi-item findings.

If you cannot answer reliably: "Insufficient data in the inspection corpus. Please escalate to your site supervisor."
"""


def parse_time_ref(time_ref: str, as_of: date = None) -> str | None:
    """
    Convert a natural language time reference to an ISO date string (lower bound).
    Returns None if time_ref is None or unrecognized.

    as_of: reference date for relative terms (defaults to today).
    """
    if not time_ref:
        return None

    ref = as_of or date.today()
    t = time_ref.lower().strip()

    if t in ("last month",):
        d = (ref - relativedelta(months=1)).replace(day=1)
        return d.isoformat()

    if t in ("last quarter",):
        d = ref - relativedelta(months=3)
        return d.replace(day=1).isoformat()

    if t in ("last year",):
        return date(ref.year - 1, 1, 1).isoformat()

    if t in ("last week",):
        return (ref - timedelta(weeks=1)).isoformat()

    if t in ("this month",):
        return ref.replace(day=1).isoformat()

    if t in ("this quarter",):
        quarter_start_month = ((ref.month - 1) // 3) * 3 + 1
        return date(ref.year, quarter_start_month, 1).isoformat()

    if t in ("recently", "latest",):
        return (ref - timedelta(days=30)).isoformat()

    # "past N days/weeks/months"
    m = re.match(r"past\s+(\d+)\s+(days?|weeks?|months?)", t)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if "day" in unit:
            return (ref - timedelta(days=n)).isoformat()
        if "week" in unit:
            return (ref - timedelta(weeks=n)).isoformat()
        if "month" in unit:
            return (ref - relativedelta(months=n)).isoformat()

    # "August 2025" or "in August 2025"
    m = re.search(
        r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})",
        t,
    )
    if m:
        months = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12,
        }
        return date(int(m.group(2)), months[m.group(1)], 1).isoformat()

    # ISO date passthrough
    m = re.match(r"(\d{4}-\d{2}-\d{2})", t)
    if m:
        return m.group(1)

    return None


class FieldServiceAssistant:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.collections = load_collections(self.embeddings)

        if not self.collections:
            print("[WARN] No Chroma collections loaded. Run src/ingest.py first.")

    def ask(self, query: str) -> dict:
        """
        Main entry point. Takes a technician query, returns a routed response.

        Returns:
            {
                "query": str,
                "route_type": "HIGH" | "PARTIAL" | "LOW",
                "response": str,
                "confidence_level": str,
                "escalate": bool,
                "sources": str,
                "top_score": float
            }
        """
        # Step 1: Retrieve
        results = retrieve(query, self.collections)

        # Step 2: Score confidence
        confidence = score_confidence(results)

        # Step 3: Generate LLM answer (only if confidence is HIGH or PARTIAL)
        llm_answer = None
        if confidence["level"] in ("HIGH", "PARTIAL") and results:
            context_block = build_context_block(results)
            user_message = f"Context:\n{context_block}\n\nTechnician question: {query}"
            try:
                llm_answer = llm.generate(user_message, system=SYSTEM_PROMPT)
            except Exception as e:
                llm_answer = f"[LLM generation failed: {e}]"

        # Step 4: Route through graceful degradation
        routed = route(query, results, confidence, llm_answer)

        return {
            "query": query,
            "route_type": routed["route_type"],
            "response": routed["response"],
            "confidence_level": routed["confidence_level"],
            "escalate": routed["escalate"],
            "sources": routed["sources"],
            "top_score": confidence["top_score"]
        }


class SiteIntelligenceAgent:
    """
    Phase 2 agent for the drone inspection domain.

    Pipeline per query:
      classify → build_spatial_filter → retrieve (filtered) → [fallback] →
      score_confidence + detect_conflicts → llm.generate / route

    Drone-specific confidence thresholds are lower than HVAC because
    synthetic inspection notes embed at 0.50-0.70 vs OSHA docs at 0.80-0.93.
    """

    # Drone-specific thresholds — inspection records score lower than OSHA docs
    HIGH_THRESHOLD = float(os.getenv("DRONE_HIGH_THRESHOLD", 0.52))
    PARTIAL_THRESHOLD = float(os.getenv("DRONE_PARTIAL_THRESHOLD", 0.35))

    def __init__(self):
        self.embeddings = get_embeddings()
        self.collections = load_collections(self.embeddings, domain="drone")
        if not self.collections:
            print("[WARN] No drone Chroma collections loaded. Run: python src/ingest.py --domain drone")

    def ask(self, query: str, session_memory=None) -> dict:
        """
        Args:
            query: Raw user query.
            session_memory: Optional SessionMemory instance. If provided,
                            context is read before and updated after classification.

        Returns dict with keys:
            query, route_type, response, confidence_level, escalate,
            sources, top_score, pipeline_trace
        """
        session_ctx = session_memory.get_context() if session_memory else {}
        pipeline_trace = {}

        # Step 1: Classify
        classification = classify(query, session_context=session_ctx)
        pipeline_trace["classification"] = {
            "query_type": classification.query_type,
            "confidence": classification.confidence,
            "zone": classification.extracted_zone,
            "equipment": classification.extracted_equipment,
            "time_ref": classification.extracted_time_ref,
            "via_llm": classification.via_llm,
        }

        # Update session memory AFTER classification so this turn's entities
        # inform the NEXT turn, not override context used for THIS retrieval.
        if session_memory:
            session_memory.update(classification)

        # Step 2: Short-circuit OUT_OF_SCOPE — no retrieval, no LLM
        if classification.query_type == "OUT_OF_SCOPE":
            pipeline_trace["route"] = "OUT_OF_SCOPE_SHORT_CIRCUIT"
            return {
                "query": query,
                "route_type": "LOW",
                "response": OUT_OF_SCOPE_RESPONSE,
                "confidence_level": "LOW",
                "escalate": True,
                "sources": "",
                "top_score": 0.0,
                "pipeline_trace": pipeline_trace,
            }

        # Step 3a: Reject unknown zones before retrieval
        known_zones = {"Zone-A", "Zone-B", "Zone-C", "Zone-D", "Zone-E"}
        queried_zone = classification.extracted_zone
        if queried_zone and queried_zone not in known_zones:
            pipeline_trace["route"] = "UNKNOWN_ZONE_LOW"
            return {
                "query": query,
                "route_type": "LOW",
                "response": (
                    f"{queried_zone} does not exist in the Site Intelligence Agent corpus. "
                    f"Available zones: Zone-A through Zone-E. "
                    "Please verify the zone ID and try again."
                ),
                "confidence_level": "LOW",
                "escalate": True,
                "sources": "",
                "top_score": 0.0,
                "pipeline_trace": pipeline_trace,
            }

        # Step 3b: Build spatial filter from extracted entities
        flight_date_after = parse_time_ref(classification.extracted_time_ref)
        where_filter = build_spatial_filter(
            zone_id=classification.extracted_zone,
            flight_date_after=flight_date_after,
        )
        pipeline_trace["filter"] = where_filter

        # Only search collections the classifier selected
        target_collections = {
            k: v for k, v in self.collections.items()
            if k in classification.collections_to_search
        }

        # Step 4: Retrieve (filtered)
        results = retrieve(query, target_collections, where_filter=where_filter)
        pipeline_trace["result_count_filtered"] = len(results)

        # Fallback: if spatial filter returned nothing, retry full corpus
        if not results and where_filter:
            pipeline_trace["fallback"] = "full_corpus"
            results = retrieve(query, self.collections)
            pipeline_trace["result_count_fallback"] = len(results)

        # Step 5: Score confidence + detect conflicts
        confidence = score_confidence(
            results,
            high_threshold=self.HIGH_THRESHOLD,
            partial_threshold=self.PARTIAL_THRESHOLD,
        )
        has_conflict = detect_conflicts(results, domain="drone")
        if has_conflict and confidence["level"] == "HIGH":
            confidence["level"] = "PARTIAL"
        pipeline_trace["confidence"] = confidence["level"]
        pipeline_trace["conflict"] = has_conflict

        # Step 6: Generate LLM answer (skip on LOW — never hallucinate)
        llm_answer = None
        if confidence["level"] in ("HIGH", "PARTIAL") and results:
            context_block = build_context_block(results)
            user_message = f"Context:\n{context_block}\n\nInspector question: {query}"
            try:
                llm_answer = llm.generate(user_message, system=DRONE_SYSTEM_PROMPT)
            except Exception as e:
                llm_answer = f"[LLM generation failed: {e}]"

        # Step 7: Route through graceful degradation
        routed = route(query, results, confidence, llm_answer)

        return {
            "query": query,
            "route_type": routed["route_type"],
            "response": routed["response"],
            "confidence_level": routed["confidence_level"],
            "escalate": routed["escalate"],
            "sources": routed["sources"],
            "top_score": confidence["top_score"],
            "pipeline_trace": pipeline_trace,
        }
