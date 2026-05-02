# Ideas Brainstorm — Site Intelligence Agent
**New-age features, company angles, stretch goals**

This doc is a living brainstorm. Add ideas here as they come up. Evaluate against the "ship one phase at a time" constraint before implementing.

---

## Modern Agentic Patterns (Phase 2 Implementation)

### 1. Structured Output for Classifier (implement now)
Use Anthropic's `tool_use` or Gemini's `response_schema` to force the classifier LLM to return structured JSON instead of parsing free text.

**Why it matters as a talking point:** "I used tool_use to enforce schema-level output validation — the classifier can't return malformed JSON because the API won't accept a response that doesn't match the schema."

**Implementation:** In `llm.py`, add `generate_structured(prompt, tool_def)` method. The tool definition contains the JSON schema for `ClassificationResult`.

---

### 2. Retrieval-then-Reflect (implement now)
After retrieval, before calling the main LLM: a one-sentence relevance check.

```
"Does the following context contain information about [query]? 
Answer: YES or NO and one sentence."
```

If NO → trigger fallback (widen filter or escalate). This is a lightweight self-checking loop — the first taste of agentic reflection.

**Why it matters:** Shows you understand the difference between retrieval quality and answer quality. Most RAG systems skip this step.

---

### 3. Streaming Responses (implement in Step 6)
Replace `llm.generate()` with streaming call in `SiteIntelligenceAgent.ask()`. Use `st.write_stream()` to display tokens as they arrive.

**Why it matters for demo:** A streaming response looks dramatically more sophisticated in a screen share. The viewer sees the agent "thinking."

**Implementation:** Add `llm.stream(prompt, system)` → yields token strings. In `app.py`, replace response text area with `st.write_stream()`.

---

### 4. Pipeline Trace as First-Class Output (implement now)
Every response includes a `pipeline_trace` dict visible to the user (expandable panel):

```json
{
  "classifier": {"query_type": "ANOMALY_QUERY", "confidence": 0.92, "reasoning": "..."},
  "spatial_filter": {"zone_id": "Zone-C", "flight_date_after": "2025-07-01"},
  "collections_searched": ["inspection_records", "historical_baselines"],
  "filter_result_count": 7,
  "fallback_triggered": false,
  "reflect_check": "YES — context directly addresses Zone C anomalies",
  "confidence_level": "HIGH",
  "top_score": 0.87
}
```

**Why it matters:** This is your differentiator. No other student demo shows the agent's full reasoning trace. In a DroneDeploy interview: "Click this arrow — you can see every decision the agent made and why."

---

### 5. Tool Framing for Future Upgrade (document now, implement partially)
Wrap `spatial_filter`, `compliance_lookup`, and `baseline_compare` as tool-call-shaped functions in `src/tools.py`. Today they're just direct function calls. But the interface is designed as tools:

```python
TOOLS = [
    {
        "name": "spatial_filter_retrieval",
        "description": "Retrieve inspection records filtered by zone, date, or severity",
        "input_schema": {...}
    },
    {
        "name": "compliance_lookup",
        "description": "Look up OSHA standards and safety regulations",
        "input_schema": {...}
    }
]
```

Even if Phase 2 doesn't use the full tool_use loop, the architecture shows you understand the pattern. Phase 3 or 4 can upgrade to a real tool_use agent loop.

---

## Phase 3 Ideas (July-August 2026)

### Live Deployed URL
- Streamlit Cloud: free, supports secrets management, auto-deploy from GitHub
- Railway: more control, custom domains, still free tier
- Decision: Streamlit Cloud first (faster), Railway if custom domain needed

### Map Layer
- Folium: simple, good enough, integrates with Streamlit via `st.components.v1.html()`
- Plotly: more interactive, `st.plotly_chart()` native support
- Decision: Plotly for Phase 3 (looks more professional in demos)
- Phase 2 prep: store coordinates as floats (lat, lng) in data, not text strings

### Longitudinal Anomaly Tracking
- "Zone C has been flagged in 3 of the last 5 inspections"
- Requires temporal aggregation across inspection_records
- Implementation: `src/longitudinal.py` — query inspector_records for a zone, count flags over time, compute severity trend
- New route type: TREND (alongside HIGH/PARTIAL/LOW) for longitudinal queries

### Anomaly Severity Trends
- "Zone B HIGH severity anomalies trending up Q3→Q4 2025"
- Requires date-aware aggregation
- Could be a new panel in app.py showing a simple bar chart (Plotly)

---

## Company-Specific Angles

### DroneDeploy
**What they care about:** Upstream data intelligence for drone operators. Making inspection data actionable after the flight.
**Your angle:** "The agent reasons across flight history, not just a single inspection. It knows what normal looks like for Zone C and tells you when it's trending above baseline."
**README hook:** "Site Intelligence Layer for DroneDeploy — query your inspection history in plain language."

### Infravision
**What they care about:** Safety-critical infrastructure inspection. Wrong answers = liability.
**Your angle:** Graceful degradation is the pitch. "The system never confidently answers when it doesn't have data. LOW-confidence queries escalate to a human instead of hallucinating."
**README hook:** "Zero-hallucination design for safety-critical infrastructure inspection intelligence."

### Wherobots
**What they care about:** Spatial intelligence, geospatial query layers, making location data queryable.
**Your angle:** Spatial metadata filtering + map layer. "Zone-level filtering means the agent is spatially aware — it retrieves by geography, not just semantics."
**README hook:** "Spatially-aware RAG for site inspection intelligence — built on Chroma + Sentence Transformers."

---

## Ideas to Park (Not Phase 2)

- **Real DroneDeploy API integration** — requires API key + rate limiting. Synthetic data is sufficient for portfolio.
- **Vector DB upgrade to Pinecone or Weaviate** — premature. Chroma works fine at this scale.
- **Fine-tuned embeddings** — overkill for a prototype. Sentence Transformers + Chroma is the story.
- **Multi-user auth** — Phase 3 at earliest. Public demo is fine.
- **Webhook/event triggers** — "new inspection loaded" → agent proactively flags anomalies. Interesting but Phase 4 work.
- **LangGraph for orchestration** — good idea but adds significant complexity. Implement the classifier as a raw Python class first. LangGraph can be the refactor story in Phase 4.
- **Agent memory (cross-session)** — store user preferences and past queries to a database. Phase 4. Phase 2 is within-session only.

---

## Questions to Answer Before Starting Code

- [x] What are the three demo queries for the drone domain? (See 00_phase2_overview.md)
- [x] What metadata fields must inspection_records have? (See 01_data_schema.md)
- [x] What does the classifier output look like? (See 02_classifier_design.md)
- [x] How does spatial filtering interact with the existing retrieval loop? (See 03_spatial_filter_design.md)
- [x] What state does session memory track? (See 04_session_memory_design.md)
- [ ] What is the exact system prompt for the drone domain LLM?
- [ ] How long should the inspector notes be (confirmed: 4-6 sentences)?
- [ ] Should spatial filter apply to historical_baselines or only inspection_records?
