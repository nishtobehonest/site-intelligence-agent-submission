"""
classifier.py
-------------
Query classifier for the drone inspection domain (Phase 2).

Runs before retrieval. Takes the raw user query + session context and outputs
a ClassificationResult that tells the pipeline:
  - what type of question this is
  - which Chroma collections to search
  - what spatial entities were extracted (zone, equipment, time reference)
  - what retrieval strategy to use

Two-path design:
  Path 1 — rule-based keyword matching (~70% of queries, ~5ms, no LLM call)
  Path 2 — LLM structured output for ambiguous queries (Anthropic tool_use)
"""

import os
import re
from dataclasses import dataclass, field
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

QueryType = Literal["COMPLIANCE_LOOKUP", "HISTORICAL_LOOKUP", "ANOMALY_QUERY", "OUT_OF_SCOPE"]


@dataclass
class ClassificationResult:
    query_type: QueryType
    confidence: float
    extracted_zone: str | None
    extracted_equipment: str | None
    extracted_time_ref: str | None
    collections_to_search: list[str]
    retrieval_strategy: str          # "filtered" | "full" | "compliance_only" | "skip"
    reasoning: str
    via_llm: bool = False            # True if LLM path was used


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COMPLIANCE_KEYWORDS = {
    "osha", "regulation", "requirement", "procedure", "lockout",
    "tagout", "safety standard", "cfr", "subpart", "compliance",
    "hazard", "fall protection", "scaffolding", "regulatory",
}

HISTORICAL_KEYWORDS = {
    "last month", "previous", "history", "past", "inspection record",
    "was flagged", "has been", "prior", "trend", "baseline", "recurring",
    "historically", "over time", "last quarter", "last year",
}

ANOMALY_KEYWORDS = {
    "anomaly", "anomalies", "flagged", "zone", "severity", "hotspot",
    "corrosion", "damage", "what was found", "current status", "found in",
    "inspection", "detected", "reported", "identified",
}

OUT_OF_SCOPE_SIGNALS = {
    "weather", "stock", "news", "sports", "recipe", "movie",
    "forecast", "price", "crypto", "twitter", "social media",
}

COLLECTION_MAP: dict[QueryType, list[str]] = {
    "COMPLIANCE_LOOKUP": ["compliance_docs"],
    "HISTORICAL_LOOKUP": ["historical_baselines", "inspection_records"],
    "ANOMALY_QUERY":     ["inspection_records", "historical_baselines"],
    "OUT_OF_SCOPE":      [],
}

STRATEGY_MAP: dict[QueryType, str] = {
    "COMPLIANCE_LOOKUP": "compliance_only",
    "HISTORICAL_LOOKUP": "full",
    "ANOMALY_QUERY":     "filtered",
    "OUT_OF_SCOPE":      "skip",
}

KNOWN_ZONES = {"Zone-A", "Zone-B", "Zone-C", "Zone-D", "Zone-E"}

KNOWN_EQUIPMENT = [
    "rooftop-hvac", "structural-panel", "drainage-system",
    "electrical-conduit", "solar-array",
]

EQUIPMENT_ALIASES = {
    "hvac": "rooftop-hvac",
    "rooftop": "rooftop-hvac",
    "panel": "structural-panel",
    "structural": "structural-panel",
    "drainage": "drainage-system",
    "drain": "drainage-system",
    "electrical": "electrical-conduit",
    "conduit": "electrical-conduit",
    "solar": "solar-array",
    "array": "solar-array",
}

TIME_PATTERNS = [
    r"last\s+month",
    r"last\s+week",
    r"last\s+quarter",
    r"last\s+year",
    r"past\s+\d+\s+(?:days?|months?|weeks?)",
    r"(?:in\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}",
    r"\d{4}-\d{2}-\d{2}",
    r"(?:this|the)\s+(?:month|quarter|year)",
    r"recently",
    r"latest",
]

# ---------------------------------------------------------------------------
# Entity extraction (runs regardless of which classification path fires)
# ---------------------------------------------------------------------------

def _normalize_zone(zone: str) -> str:
    """Normalize zone ID to 'Zone-X' format regardless of spacing."""
    return re.sub(r"zone[\s\-]?([a-zA-Z])", lambda m: f"Zone-{m.group(1).upper()}", zone, flags=re.IGNORECASE)


def _extract_zone(text: str, session_context: dict) -> str | None:
    # Match any Zone letter (A-Z), not just A-E — unknown zones route LOW downstream
    match = re.search(r"zone[\s\-]([a-zA-Z])", text, re.IGNORECASE)
    if match:
        return f"Zone-{match.group(1).upper()}"
    # Normalize session fallback too (LLM may have stored with space)
    fallback = session_context.get("last_zone")
    return _normalize_zone(fallback) if fallback else None


def _extract_equipment(text: str, session_context: dict) -> str | None:
    lower = text.lower()
    for equipment in KNOWN_EQUIPMENT:
        if equipment in lower:
            return equipment
    for alias, canonical in EQUIPMENT_ALIASES.items():
        if alias in lower:
            return canonical
    return session_context.get("last_equipment")


def _extract_time_ref(text: str, session_context: dict) -> str | None:
    lower = text.lower()
    for pattern in TIME_PATTERNS:
        match = re.search(pattern, lower)
        if match:
            return match.group(0)
    return session_context.get("last_time_ref")


# ---------------------------------------------------------------------------
# Rule-based fast path
# ---------------------------------------------------------------------------

def _count_hits(text: str, keyword_set: set[str]) -> int:
    lower = text.lower()
    return sum(1 for kw in keyword_set if kw in lower)


def _rule_based_classify(query: str) -> tuple[QueryType, float] | None:
    """
    Returns (query_type, confidence) if the rule-based path fires,
    or None if the query is ambiguous and needs the LLM path.
    """
    out_hits = _count_hits(query, OUT_OF_SCOPE_SIGNALS)
    if out_hits >= 1:
        return "OUT_OF_SCOPE", 0.95

    compliance_hits = _count_hits(query, COMPLIANCE_KEYWORDS)
    historical_hits = _count_hits(query, HISTORICAL_KEYWORDS)
    anomaly_hits = _count_hits(query, ANOMALY_KEYWORDS)

    # Clear winner: 2+ hits in one category, 0 in others
    if compliance_hits >= 2 and historical_hits == 0 and anomaly_hits == 0:
        return "COMPLIANCE_LOOKUP", 0.90
    if historical_hits >= 2 and compliance_hits == 0 and anomaly_hits == 0:
        return "HISTORICAL_LOOKUP", 0.85
    if anomaly_hits >= 2 and compliance_hits == 0 and historical_hits == 0:
        return "ANOMALY_QUERY", 0.85

    return None  # ambiguous — fall through to LLM


# ---------------------------------------------------------------------------
# LLM path (Anthropic tool_use for structured output)
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a query classifier for a drone site inspection intelligence system.

The system has three data sources:
- inspection_records: actual drone inspection records with zone IDs, dates, anomaly types, severity
- compliance_docs: OSHA safety standards (1910.147, 1926 Subpart Q)
- historical_baselines: normal operating baselines per zone and equipment type

Classification rules:
- COMPLIANCE_LOOKUP: regulatory/safety procedure/standard questions
- HISTORICAL_LOOKUP: past records, trends, baselines, recurring patterns
- ANOMALY_QUERY: current or recent anomaly status for a specific zone/equipment
- OUT_OF_SCOPE: no relevant data exists in any collection

Always use the classify_query tool."""


def _llm_classify(query: str, session_context: dict) -> tuple[QueryType, float, str, str | None, str | None, str | None]:
    """
    Returns (query_type, confidence, reasoning, extracted_zone, extracted_equipment, extracted_time_ref).
    Falls back to ANOMALY_QUERY on any error.
    """
    import google.generativeai as genai
    import json

    session_summary = ""
    if session_context.get("last_zone") or session_context.get("last_equipment"):
        parts = []
        if session_context.get("last_zone"):
            parts.append(f"zone: {session_context['last_zone']}")
        if session_context.get("last_equipment"):
            parts.append(f"equipment: {session_context['last_equipment']}")
        if session_context.get("last_time_ref"):
            parts.append(f"time: {session_context['last_time_ref']}")
        session_summary = f"Prior session context: {', '.join(parts)}."

    prompt = (
        f"{_SYSTEM_PROMPT}\n\n"
        f"{session_summary}\n\n"
        f"Classify this query: \"{query}\"\n\n"
        "Respond with ONLY a JSON object with keys: "
        "query_type, confidence, reasoning, extracted_zone, extracted_equipment, extracted_time_ref. "
        "query_type must be one of: COMPLIANCE_LOOKUP, HISTORICAL_LOOKUP, ANOMALY_QUERY, OUT_OF_SCOPE. "
        "Use null for fields that don't apply."
    ).strip()

    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        result = json.loads(text)
        raw_zone = result.get("extracted_zone")
        return (
            result["query_type"],
            float(result.get("confidence", 0.70)),
            result.get("reasoning", ""),
            _normalize_zone(raw_zone) if raw_zone else None,
            result.get("extracted_equipment"),
            result.get("extracted_time_ref"),
        )
    except Exception as e:
        print(f"[WARN] LLM classifier failed: {e}. Falling back to ANOMALY_QUERY.")
        return "ANOMALY_QUERY", 0.50, f"LLM fallback due to error: {e}", None, None, None


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def classify(query: str, session_context: dict | None = None) -> ClassificationResult:
    """
    Classify a user query and extract spatial entities.

    Args:
        query: Raw user query string.
        session_context: Dict from SessionMemory.get_context(). Pass None for stateless use.

    Returns:
        ClassificationResult with query_type, collections, spatial entities, and strategy.
    """
    if session_context is None:
        session_context = {}

    via_llm = False
    llm_zone = llm_equipment = llm_time_ref = None

    rule_result = _rule_based_classify(query)
    if rule_result is not None:
        query_type, confidence = rule_result
        reasoning = f"Rule-based: matched keywords for {query_type}."
    else:
        query_type, confidence, reasoning, llm_zone, llm_equipment, llm_time_ref = _llm_classify(query, session_context)
        via_llm = True

    # Entity extraction — LLM path may have already extracted; regex runs for both paths
    extracted_zone = llm_zone or _extract_zone(query, session_context)
    extracted_equipment = llm_equipment or _extract_equipment(query, session_context)
    extracted_time_ref = llm_time_ref or _extract_time_ref(query, session_context)

    return ClassificationResult(
        query_type=query_type,
        confidence=confidence,
        extracted_zone=extracted_zone,
        extracted_equipment=extracted_equipment,
        extracted_time_ref=extracted_time_ref,
        collections_to_search=COLLECTION_MAP[query_type],
        retrieval_strategy=STRATEGY_MAP[query_type],
        reasoning=reasoning,
        via_llm=via_llm,
    )
