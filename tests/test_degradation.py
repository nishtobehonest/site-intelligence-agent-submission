"""
tests/test_degradation.py
--------------------------
Unit tests for confidence scoring and graceful degradation routing.

Three test groups:
  A. score_confidence() — confidence logic with mocked detect_conflicts
  B. route()            — degradation routing (pure function, no mocks needed)
  C. Integration        — FieldServiceAssistant.ask() verifies LLM is skipped on LOW confidence
"""

import pytest
from unittest.mock import patch, MagicMock

from src.confidence import score_confidence
from src.degradation import route
from src.assistant import FieldServiceAssistant


def make_result(score, source="test.pdf", collection="osha", content="Test content about HVAC procedures."):
    return {"score": score, "source": source, "collection": collection, "content": content, "metadata": {}}


# ---------------------------------------------------------------------------
# Group A: score_confidence()
# ---------------------------------------------------------------------------

class TestScoreConfidence:

    def test_high_path(self):
        results = [make_result(0.90), make_result(0.85), make_result(0.80)]
        with patch("src.confidence.detect_conflicts", return_value=False):
            conf = score_confidence(results)
        assert conf["level"] == "HIGH"
        assert conf["conflict_detected"] is False
        assert conf["top_score"] == pytest.approx(0.90)

    def test_partial_from_conflict(self):
        results = [
            make_result(0.90, collection="osha"),
            make_result(0.85, collection="manuals"),
        ]
        with patch("src.confidence.detect_conflicts", return_value=True):
            conf = score_confidence(results)
        assert conf["level"] == "PARTIAL"
        assert conf["conflict_detected"] is True

    def test_partial_from_low_mid_score(self):
        results = [make_result(0.65), make_result(0.60)]
        with patch("src.confidence.detect_conflicts", return_value=False):
            conf = score_confidence(results)
        assert conf["level"] == "PARTIAL"
        assert conf["conflict_detected"] is False

    def test_low_from_empty_results(self):
        conf = score_confidence([])
        assert conf["level"] == "LOW"
        assert conf["top_score"] == 0.0
        assert conf["conflict_detected"] is False

    def test_low_from_low_score(self):
        results = [make_result(0.30)]
        with patch("src.confidence.detect_conflicts", return_value=False):
            conf = score_confidence(results)
        assert conf["level"] == "LOW"


# ---------------------------------------------------------------------------
# Group B: route()
# ---------------------------------------------------------------------------

class TestRoute:

    def test_high_route_no_escalation(self):
        results = [make_result(0.90), make_result(0.85)]
        confidence = {
            "level": "HIGH", "top_score": 0.90,
            "conflict_detected": False, "reason": "Strong match"
        }
        routed = route("What is the lockout procedure?", results, confidence, llm_answer="Step 1: shut down...")
        assert routed["route_type"] == "HIGH"
        assert routed["escalate"] is False
        assert routed["confidence_level"] == "HIGH"
        assert "Step 1: shut down" in routed["response"]

    def test_partial_route_with_conflict_flags_sources(self):
        results = [
            make_result(0.85, source="osha_1910.pdf", collection="osha"),
            make_result(0.80, source="carrier_2017.pdf", collection="manuals"),
        ]
        confidence = {
            "level": "PARTIAL", "top_score": 0.85,
            "conflict_detected": True, "reason": "Cross-collection conflict"
        }
        routed = route("What are the electrical safety steps?", results, confidence, llm_answer="The procedure is...")
        assert routed["route_type"] == "PARTIAL"
        assert routed["escalate"] is True
        assert "SOURCES DISAGREE" in routed["response"]

    def test_partial_route_low_score_warns_confidence(self):
        results = [make_result(0.65), make_result(0.60)]
        confidence = {
            "level": "PARTIAL", "top_score": 0.65,
            "conflict_detected": False, "reason": "Score below high threshold"
        }
        routed = route("What is the filter size?", results, confidence, llm_answer="Partial answer...")
        assert routed["route_type"] == "PARTIAL"
        assert routed["escalate"] is True
        assert "LOW CONFIDENCE" in routed["response"]

    def test_low_route_empty_results_escalates(self):
        confidence = {
            "level": "LOW", "top_score": 0.0,
            "conflict_detected": False, "reason": "No relevant documents found."
        }
        routed = route("What are Daikin VRV repair steps?", [], confidence, llm_answer=None)
        assert routed["route_type"] == "LOW"
        assert routed["escalate"] is True
        assert "❌" in routed["response"]
        assert routed["sources"] == "None"

    def test_low_route_includes_closest_match_snippet(self):
        results = [make_result(0.30, content="Carrier rooftop unit maintenance guide section 4.")]
        confidence = {
            "level": "LOW", "top_score": 0.30,
            "conflict_detected": False, "reason": "Best match similarity (0.30) is below threshold."
        }
        routed = route("What are Rheem RA20 charge pressures?", results, confidence, llm_answer=None)
        assert routed["route_type"] == "LOW"
        assert "Carrier rooftop unit maintenance guide" in routed["response"]


# ---------------------------------------------------------------------------
# Group C: Integration — LLM must be skipped on LOW confidence
# ---------------------------------------------------------------------------

class TestAssistantLowPathSkipsLLM:

    def test_llm_not_called_on_low_confidence(self):
        low_result = make_result(0.30)
        low_confidence = {
            "level": "LOW", "top_score": 0.30,
            "conflict_detected": False,
            "reason": "Best match similarity (0.30) is below the minimum threshold (0.50)."
        }

        with patch("src.assistant.get_embeddings"), \
             patch("src.assistant.load_collections", return_value={}), \
             patch("src.assistant.retrieve", return_value=[low_result]), \
             patch("src.assistant.score_confidence", return_value=low_confidence), \
             patch("src.assistant.llm") as mock_llm:

            assistant = FieldServiceAssistant()
            result = assistant.ask("What are the fault codes for a Goodman GSXC18?")

            mock_llm.generate.assert_not_called()
            assert result["route_type"] == "LOW"
            assert result["escalate"] is True
            assert result["top_score"] == pytest.approx(0.30)
