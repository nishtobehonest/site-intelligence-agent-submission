"""
session_memory.py
-----------------
Tracks spatial entities across conversation turns for the drone inspection domain.

Resolves ambiguous references like "what about last month?" by remembering
what zone, equipment, and time period the user last asked about.

Designed to live in st.session_state in Streamlit (per-browser-tab, not shared).
"""

from dataclasses import dataclass, field
from datetime import datetime
from src.classifier import ClassificationResult


@dataclass
class SessionMemory:
    last_zone: str | None = None
    last_equipment: str | None = None
    last_time_ref: str | None = None
    last_query_type: str | None = None
    turn_count: int = 0
    session_start: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_context(self) -> dict:
        """Return current context dict for passing to classify()."""
        return {
            "last_zone": self.last_zone,
            "last_equipment": self.last_equipment,
            "last_time_ref": self.last_time_ref,
            "last_query_type": self.last_query_type,
            "turn_count": self.turn_count,
        }

    def update(self, classification: ClassificationResult) -> None:
        """
        Update state from classifier output.
        Only overwrites a field when the classifier returned a non-None value —
        so prior context persists when the user doesn't mention a new entity.
        """
        if classification.extracted_zone is not None:
            self.last_zone = classification.extracted_zone
        if classification.extracted_equipment is not None:
            self.last_equipment = classification.extracted_equipment
        if classification.extracted_time_ref is not None:
            self.last_time_ref = classification.extracted_time_ref
        self.last_query_type = classification.query_type
        self.turn_count += 1

    def reset(self) -> None:
        """Clear all context. Called on New Session button press."""
        self.last_zone = None
        self.last_equipment = None
        self.last_time_ref = None
        self.last_query_type = None
        self.turn_count = 0
        self.session_start = datetime.now().isoformat()

    def has_context(self) -> bool:
        """True if at least one entity has been resolved in this session."""
        return any([self.last_zone, self.last_equipment, self.last_time_ref])

    def summary(self) -> str:
        """One-line human-readable summary for UI display."""
        if not self.has_context():
            return "No session context"
        parts = []
        if self.last_zone:
            parts.append(self.last_zone)
        if self.last_equipment:
            parts.append(self.last_equipment)
        if self.last_time_ref:
            parts.append(self.last_time_ref)
        return " | ".join(parts)
