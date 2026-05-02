# Session Memory Design
**Phase 2 · src/session_memory.py**

---

## Why Session Memory

Without session memory, every query is independent. The user asks:
1. "What anomalies are in Zone C?" → agent searches Zone C ✓
2. "What about last month?" → agent has no idea what zone or what "last month" refers to ✗

With session memory, the agent tracks what was referenced in prior turns and uses it to resolve ambiguous references in subsequent queries. This is the difference between a search box and an intelligence layer.

---

## What Gets Tracked

```python
@dataclass
class SessionContext:
    last_zone: str | None = None            # "Zone-C"
    last_equipment: str | None = None       # "rooftop-hvac"
    last_time_ref: str | None = None        # "last month" (raw string)
    last_query_type: str | None = None      # "ANOMALY_QUERY"
    turn_count: int = 0
    session_start: str = field(default_factory=lambda: datetime.now().isoformat())
```

**What is NOT tracked:**
- Full conversation history (that would require a chat buffer — overkill for Phase 2)
- LLM answer text (not needed for entity resolution)
- Retrieval results (too large, not needed)

The goal is entity resolution, not full conversational memory. Minimal state = easier to reason about + easier to demo.

---

## Update Rules

**When to overwrite vs. preserve:**

| Field | Rule |
|-------|------|
| `last_zone` | Overwrite if classifier extracted a new zone; preserve if new query had no zone |
| `last_equipment` | Same — overwrite only when new value is extracted |
| `last_time_ref` | Overwrite if new time reference was mentioned; preserve otherwise |
| `last_query_type` | Always overwrite with most recent query type |

**Rationale:** If the user asks about Zone C, then asks "what about HIGH severity?" — the zone should persist (they're still asking about Zone C). Only overwrite when the user explicitly mentions a new value.

---

## Resolution Examples

| Turn 1 | Turn 2 | Session Resolves To |
|--------|--------|---------------------|
| "What anomalies are in Zone C?" | "What about last month?" | Zone-C + last month |
| "Show me HIGH severity items in Zone B" | "What does the baseline look like?" | Zone-B + HIGH + last_time_ref from T1 (if any) |
| "What does OSHA say about fall protection?" | "What about Zone D?" | Zone-D (compliance context cleared, ANOMALY or HISTORICAL context applies) |
| "Zone C anomalies" | "And Zone A?" | Zone-A (explicit zone mention overwrites Zone-C) |

---

## Storage in Streamlit

Session memory lives in `st.session_state`, not in `st.cache_resource`.

- `st.cache_resource` is per-server (shared across all browser sessions) — wrong for per-user state
- `st.session_state` is per-browser-tab (each tab gets its own session) — correct

```python
# In app.py
if "session_memory" not in st.session_state:
    st.session_state.session_memory = SessionMemory()

memory = st.session_state.session_memory
```

The `SiteIntelligenceAgent` instance (which loads Chroma collections) CAN stay in `st.cache_resource` since it is stateless. Only the `SessionMemory` instance goes in `st.session_state`.

---

## Session Reset

Two triggers for reset:
1. User clicks "New Session" button in sidebar → calls `memory.reset()`
2. Page refresh → `st.session_state` is cleared automatically by Streamlit

After reset, the context panel in the UI should show "No session context yet."

---

## SessionMemory API

```python
class SessionMemory:
    def get_context(self) -> dict:
        """
        Returns current context as dict for passing to classify().
        {"last_zone": ..., "last_equipment": ..., "last_time_ref": ..., "last_query_type": ..., "turn_count": ...}
        """

    def update(self, query: str, classification: ClassificationResult) -> None:
        """
        Update state from classifier output after each turn.
        Only overwrites a field if the classifier returned a non-None value for it.
        Always increments turn_count.
        """

    def reset(self) -> None:
        """Clear all context. Called on 'New Session' button press."""

    def has_context(self) -> bool:
        """True if at least one entity has been resolved in this session."""

    def summary(self) -> str:
        """One-line human-readable summary for UI display."""
        # Example: "Zone-C | rooftop-hvac | last month"
        # If no context: "No session context"
```

---

## Classifier Integration

The classifier's `session_context` parameter expects the dict from `get_context()`:

```python
# In SiteIntelligenceAgent.ask()
session_ctx = self.session_memory.get_context()
classification = classify(query, session_context=session_ctx)

# After classification (before LLM call)
self.session_memory.update(query, classification)
```

**Order matters:** Update session memory AFTER classification, not before. The current query's entities should inform the NEXT turn, not override the context used for THIS turn's retrieval.

---

## UI Display

Session context panel in sidebar (compact):

```
─────────────────────────
Session Context
─────────────────────────
Zone:      Zone-C
Equipment: rooftop-hvac
Time:      last month
Turns:     3

[New Session]
─────────────────────────
```

Show only fields that have values. If `has_context()` is False, show: "Ask a question to start."

---

## Testing

```python
from src.session_memory import SessionMemory
from src.classifier import classify

mem = SessionMemory()
assert mem.has_context() == False
assert mem.get_context()["turn_count"] == 0

# Turn 1
r1 = classify("What anomalies are in Zone C?")
mem.update("What anomalies are in Zone C?", r1)
assert mem.get_context()["last_zone"] == "Zone-C"
assert mem.has_context() == True

# Turn 2 — zone should persist
r2 = classify("What about last month?", session_context=mem.get_context())
assert r2.extracted_zone == "Zone-C"  # resolved from session
mem.update("What about last month?", r2)

# Reset
mem.reset()
assert mem.has_context() == False
assert mem.get_context()["turn_count"] == 0
```
