# Site Intelligence Agent — Phase by Phase Build Plan
**From prototype to portfolio-ready product**
Private planning document

---

## Core Principle

Build version by version. Each phase produces something real that works. Never plan a phase you cannot finish before the next one starts. Agentic skills compound — what you learn in Phase 1 makes Phase 2 faster.

---

## Phase Summary

| Phase | What Gets Built | When |
|-------|----------------|------|
| Phase 1: Foundation | RAG pipeline, confidence scoring, graceful degradation, Streamlit dashboard, eval framework | April 15 – May 13, 2026 |
| Phase 2: Real Data + Multi-Agent | Real inspection metadata, second domain, classifier agent, spatial filters, session memory | May – June 2026 |
| Phase 3: Portfolio Product | Deployed demo URL, longitudinal tracking, map layer, company-specific pitches | July – August 2026 |

---

## Phase 1: Foundation Build
**Initial build phase · April 15 – May 13 · ~35 hours**

**Goal:** A working prototype that demonstrates the full agentic pipeline: query in, confidence-scored answer out, all three routing paths (HIGH / PARTIAL / LOW) visible in the dashboard.

---

### Week 1: User Research and System Design (April 15–22)

**What to do:**

1. **Map the exact user.** Construction site manager or operations lead running drone inspection programs. Write down three specific questions they ask every week that their current tools cannot answer reliably. These become your ground truth queries.

2. **Design the data schema.** Define what a synthetic spatial inspection record looks like:
   ```
   record_id, site_id, zone_id, flight_date, equipment_type,
   anomaly_type, severity (HIGH/MEDIUM/LOW), coordinates (lat/lng as text),
   inspector_notes, compliance_flag, resolution_status
   ```

3. **Design the system architecture on paper.** How does a query flow from Streamlit input → retrieval → confidence scoring → routing → UI? Draw it. This becomes your proposal figure and interview talking point.

4. **Define three Chroma collections:**
   - `inspection_records`: spatial anomaly data with zone and date metadata
   - `compliance_docs`: OSHA standards, site safety requirements
   - `historical_baselines`: what normal looks like per zone and equipment type

5. **Write your three demo queries:**
   - One that triggers HIGH confidence (clear anomaly match)
   - One that triggers PARTIAL (two inspections flagging same zone differently)
   - One that triggers LOW (zone with no inspection history)

**Deliverable:** System design doc (1–2 pages). Data schema. Three demo queries. Architecture diagram. Do not write code this week.

---

### Week 2: Data Layer and Retrieval Pipeline (April 22–29)

**What to do:**

1. **Generate synthetic data.** Update `src/generate_synthetic.py` to use the spatial inspection schema. Generate 50 records. Each must be specific: real zone IDs, real anomaly descriptions, specific coordinates, realistic inspector notes.

2. **Download compliance documents.** OSHA 1910.147 (already have it). Add OSHA 1926 Subpart Q (construction safety). 1–2 public site safety inspection checklists. These go in the `compliance_docs` collection.

3. **Build `src/ingest.py`.** Load all three data types into separate Chroma collections. Tag every inspection record with spatial metadata: `zone_id`, `coordinates`, `flight_date`. This metadata enables spatial filtering in Phase 2.

4. **Build `src/retriever.py`.** Embed queries using `sentence-transformers/all-MiniLM-L6-v2`. Retrieve top-5 from all three collections. Return results with source, collection, similarity score, and spatial metadata.

5. **Test retrieval.** Run 10 test queries. Does querying Zone C return Zone C records? Does a compliance query return OSHA docs? Fix until it does.

**Success condition:**
```python
from src.retriever import retrieve
results = retrieve("What anomalies were flagged in Zone C last month?", collections)
print(results[0])  # Should return a real inspection record with score > 0.50
```

---

### Week 3: Agentic Pipeline (April 29 – May 6)

**What to do:**

1. **Build `src/confidence.py`.** Starting thresholds:
   - HIGH: top score > 0.72, no conflict
   - PARTIAL: top score 0.50–0.72, OR conflict detected (top two results from different collections within 0.15 of each other)
   - LOW: top score < 0.50, OR zero results

2. **Build `src/degradation.py`.** Three routing paths:
   - HIGH: answer with citation, zone ID, flight date, severity
   - PARTIAL: answer with conflict warning showing both sources explicitly
   - LOW: escalation message — what was searched, what was not found, recommended action. **LOW never calls the Claude API.** The escalation is programmatic.

3. **Build `src/assistant.py`.** Wire everything together. System prompt must enforce: answer only from retrieved context, always cite source and zone ID, flag safety-critical anomalies, say "I do not have sufficient information" when uncertain.

4. **Test all three routing paths.** Run your three demo queries. Verify each hits the correct path. Adjust thresholds if needed.

**The agentic skill you are building:** Your first real multi-step reasoning pipeline: understand query → retrieve → evaluate confidence → decide action → generate or escalate. Know why each threshold is set where it is. This is what you explain in interviews.

---

### Week 4: Dashboard and Evaluation (May 6–11)

**Dashboard (`app.py`):**

1. Streamlit interface: text input, submit button, color-coded confidence badge (green/yellow/red), response area with citations and zone IDs, escalation message area, three preset demo query buttons in sidebar.

2. Make it recordable. Clean layout, clear labels. Test a 2-minute walkthrough showing all three routing paths before the final submission.

**Evaluation framework:**

1. Build three eval sets:
   - 20 ground truth Q&A pairs (known answers from your synthetic data)
   - 10 adversarial queries (zones that do not exist in corpus)
   - 10 contradiction scenarios (same zone flagged differently by two inspections)

2. Build `eval/run_eval.py`. Run all 40 queries. Record route type, top score, whether routing was correct. Output: CSV + summary table.

3. Tune thresholds. Targets:
   - Ground truth: > 85% correct routing
   - Adversarial: > 90% correct escalation (LOW)
   - Contradiction: > 75% PARTIAL detection

---

### Week 5: Documentation and Submission (May 11–13)

1. **Final design document.** Problem statement. System architecture. Three routing paths with design rationale. Eval results table. Limitations. V2 roadmap.

2. **Record the demo video.** 5–7 minutes. Open dashboard, show all three routing paths live, explain confidence scoring out loud, show eval results table, end with V2 roadmap.

3. **Clean the repo.** README with clear setup instructions. CLAUDE.md with full system context. All eval scripts working from a fresh install. Push to GitHub.

4. **Submit by May 13 at 11:59 PM.**

---

## Phase 2: Real Data and Multi-Agent Layer
**Portfolio Extension · May – June 2026 · ~40 hours**

**Goal:** Move from synthetic data to real inspection metadata. Add a second domain. Add a classifier agent that routes queries before retrieval begins. This is the version you show DroneDeploy and Infravision.

### What gets added:

| Component | What Gets Added |
|-----------|----------------|
| Data layer | Real drone inspection metadata from DroneDeploy public datasets or Airdata UAV public API. Replace synthetic records with real flight logs, timestamps, anomaly classifications. |
| Second domain | Power grid or mining inspection records as a second Chroma collection set. Same pipeline, different corpus. Proves the architecture generalizes. |
| Classifier agent | A new agent that runs before retrieval. Classifies query by type (compliance, historical lookup, anomaly query, out-of-scope) and routes to the right retrieval strategy. First multi-agent handoff. |
| Spatial filters | Coordinate-based metadata filtering in Chroma. A question about Zone C only retrieves Zone C records. The spatial indexing problem. |
| Session memory | Agent carries context within a session. "What about last month?" understands it means Zone C last month. |

### The agentic skills you are building:
- **Multi-agent orchestration:** classifier agent + retrieval agent hand off to each other. Design the handoff interface explicitly.
- **Tool use design:** spatial filter, compliance lookup, and historical baseline comparison are all tools the retrieval agent calls. Designing when to call them and what to do when they return nothing is the skill.
- **Stateful agent design:** the difference between a stateless and stateful agent. Session memory is what makes the system feel like an intelligence layer rather than a search box.

---

## Phase 3: Portfolio Product
**Demo-Ready for Target Companies · July – August 2026 · ~30 hours**

**Goal:** A live, deployed, demoable system you can share as a URL. No setup required for the viewer. Positioned for DroneDeploy, Infravision, and Wherobots.

### What gets built:

1. **Deploy to Streamlit Cloud or Railway.** Free hosting. Shareable URL. This is the difference between a demo you show in a screen share and a demo you send in a cold email.

2. **Longitudinal anomaly tracking.** "Zone C has been flagged in 3 of the last 5 inspections. Severity is trending upward." This is the Inspection AI use case at DroneDeploy.

3. **Reality mapping layer.** Simple map view (Folium or Plotly) that places flagged anomalies at their spatial coordinates. Click a point, see the agent's analysis for that zone.

4. **Company-specific README versions:**
   - DroneDeploy: upstream reliability for AI agents
   - Infravision: safety-critical power grid inspection intelligence
   - Wherobots: spatial intelligence layer for geospatial platforms

5. **2-page portfolio case study.** User problem. System design. Key decisions. Eval results. What you would do next. Link from LinkedIn.

---

## Agentic Skills Across All Phases

| Phase | Skill | What It Teaches |
|-------|-------|----------------|
| 1 | RAG retrieval with confidence scoring | How to build a pipeline that knows when to trust its own outputs |
| 1 | Graceful degradation routing | How to design explicit failure paths so the agent never hallucinates when it should escalate |
| 1 | Human-in-the-loop escalation | What the human sees, what they decide, how that feeds back |
| 2 | Multi-agent orchestration | How two agents hand off. What happens at the boundary. |
| 2 | Tool use design | When to call a tool vs. reason directly. What to do when it returns nothing. |
| 2 | Session memory | Stateless vs. stateful agent design |
| 3 | Longitudinal reasoning | How to reason across time, not just a single query |
| 3 | Spatial intelligence | How to make similarity search spatially aware |

---

## What Not to Do

- Do not build a web scraper for real drone data in Phase 1. Synthetic is enough and faster.
- Do not add the map layer in Phase 1. It is Phase 3 work.
- Do not ask Claude Code to build the whole system in one prompt. Build file by file. Test after each file.
- Do not tune confidence thresholds before you have eval results. Set defaults, run the eval, then tune.
- Do not skip graceful degradation design. This is your differentiator. Every other student project returns an answer. Yours knows when not to.

---

## How to Use Claude Code

**At the start of every session:**
> "Read CLAUDE.md. Here is where I am: [one sentence on what is working]. Here is what I need to do next: [one specific file or function]. Do not rewrite anything that is already working."

**For each file:** Ask Claude Code to explain what it is about to build before writing a line. If the explanation does not match your mental model, correct it first.

**When something breaks:** Paste the exact error. Paste the relevant file. Ask: what is causing this specific thing? Do not let it refactor the whole file to fix a new problem.

---

## Files and What They Do

| File | What It Does |
|------|-------------|
| `src/ingest.py` | Loads inspection records, compliance docs, baselines into three Chroma collections |
| `src/retriever.py` | Embeds queries, searches collections, returns top-k with scores and spatial metadata |
| `src/confidence.py` | Outputs HIGH / PARTIAL / LOW with reason. Most important tuning surface. |
| `src/degradation.py` | Routes based on confidence. LOW path never calls Claude API. |
| `src/assistant.py` | Main pipeline. `assistant.ask(query)` wires everything together. |
| `src/generate_synthetic.py` | Generates inspection records via Claude API. Update schema for spatial fields. |
| `app.py` | Streamlit dashboard. Query input, confidence badge, response, sidebar presets. |
| `eval/run_eval.py` | Runs all eval sets. Outputs CSV and summary table. |
| `CLAUDE.md` | Project context for Claude Code. Read at the start of every session. |
| `PORTFOLIO_STRATEGY.md` | Branch strategy and extension plan. Not committed to any shared repo. |

---

## Timeline

| Date | Milestone |
|------|-----------|
| April 15 | System design complete, no code written |
| April 22 | Retrieval pipeline working with synthetic data |
| April 29 | All three graceful degradation paths firing |
| May 6 | Dashboard running, eval framework built |
| May 13 | Phase 1 complete |
| June 2026 | Phase 2 complete — multi-agent + real data |
| August 2026 | Phase 3 complete — deployed and pitched to target companies |
