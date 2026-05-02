# Product Discovery Document
**Site Intelligence Agent — Social Impact Edition**
Nishchay Vishwanath · Cornell MEM 2026
Social Impact Mission: Economic Empowerment & Education · Governance & Collaboration

---

## The One-Sentence Reframe

This is not a RAG pipeline. It is an AI that gives every junior field worker access to the institutional knowledge of a 20-year expert — democratizing safety, skill, and economic opportunity for the working class, powered by a MAGMA-inspired multi-graph agentic memory architecture.

---

## Social Impact Alignment

**Primary: Economic Empowerment & Education**
AI removes the knowledge barrier that keeps junior field technicians underpaid, undertrained, and exposed to preventable harm. The information they need exists — in manuals, OSHA standards, service histories — but is fragmented and inaccessible at the exact moment it matters.

**Supporting: Governance & Collaboration**
Drone inspection intelligence makes infrastructure safety analysis accessible to under-resourced municipalities that cannot afford expert human review teams.

*Machines of Loving Grace* framing: This is exactly the use case Dario Amodei described — AI augmenting capability for the people who build and maintain the physical world, not replacing them. Every field worker, regardless of experience or employer resources, deserves access to the knowledge that keeps them safe and effective.

---

## Problem Statement

### Hook
A 22-year-old HVAC technician is dispatched to their fourth job of the day — a rooftop unit they've never serviced, at a building they've never visited, with a model number they don't recognize. The equipment manual is 400 pages in the truck. The OSHA standard for the correct lockout/tagout procedure is in a binder at the office. The last technician's service notes are in a system no one can access from the field.

They have 30 minutes to diagnose, confirm safety, and fix it correctly.

This is not a technology problem. It is an inequality problem. Large, well-resourced service companies invest in knowledge management systems, training coordinators, and experienced mentors. Small shops and junior workers have none of that. The gap in outcomes — missed diagnoses, repeat truck rolls, workplace injuries — falls entirely on the people who can afford it least.

### Scale

- **425,200** HVAC mechanics and installers employed in the US in 2024, with employment projected to grow 8% through 2034 — faster than average for all occupations [1]
- **20 million** field service technicians operating globally across electrical, plumbing, telecom, infrastructure, and facilities management [2]
- OSHA estimates proper lockout/tagout compliance alone prevents **120 deaths and 50,000 injuries per year** — and approximately **3 million U.S. workers** regularly service equipment that exposes them to hazardous energy [3]
- The industry-wide first-time fix rate averages **77–80%**; organizations below 70% face documented adverse effects on customer retention, SLA compliance, and asset uptime — meaning 1 in 5 service calls requires at least one return trip [4]
- Knowledge workers spend an average of **1.8 hours per day** — nearly a quarter of the workweek — searching and gathering information (McKinsey Global Institute, 2012); while this figure covers office workers, field technicians face the same fragmentation problem with additional constraints: no desk, limited connectivity, and a 30-minute job clock [5]

### Why Existing Solutions Fail

| Workaround | Why It Fails |
|---|---|
| Google the answer | Multi-source synthesis required — the answer spans a manual, an OSHA standard, and the site's service history simultaneously |
| Call the office | Dispatcher lacks the technical depth; engineers aren't available for every call |
| Search the manual | 400+ pages, not indexed, not searchable in the field, often the wrong model |
| Ask a colleague | Knowledge is individual and unstructured; the retiring workforce takes it with them |
| Enterprise FSM software | Custom enterprise pricing that scales with contract size — small shops lack the budget and Salesforce infrastructure required [6] |

---

## Users

### Tier 1 — The Junior Field Technician
**The Social Impact Hero**

**Who they are:**
Vocational-trained, often working-class background, 1–5 years of experience. Dispatched to 3–6 different sites per day — different equipment, manufacturers, building codes, and service histories. Works on rooftops, in basements, mechanical rooms: limited connectivity, under time pressure, often alone.

**What their day looks like:**
Each job starts with a work order. On arrival, they must identify the exact equipment model, determine the correct service procedure, verify compliance requirements specific to that site, and execute safely. Every stop is a series of judgment calls they may not be equipped to make.

**Jobs to be Done:**
- "Tell me the lockout/tagout procedure for this specific unit model, right now"
- "What did the last technician do here and why?"
- "Is this refrigerant pressure reading within spec for this model?"
- "What OSHA standard applies to this type of electrical work at this site?"
- "This anomaly looks wrong — is it normal for this equipment?"

**Pain Points (Critical Intensity):**
- **Safety exposure:** OSHA estimates that failures to control hazardous energy cause 120 preventable deaths and 50,000 preventable injuries annually [3]. Workers injured in these incidents lose an average of **24 workdays** per incident — more than almost any other workplace injury category [3]
- **Information search time:** Knowledge workers spend 1.8 hours/day on average searching for information [5]; field technicians working across multiple sites with different equipment face the same problem with no desk, no reliable internet, and a 30-minute job clock
- **Blame for system failures:** Mistakes caused by missing information are attributed to technician error, not knowledge-system failure — wage and career consequences fall on the worker
- **Repeat truck rolls:** Industry first-time fix rates average 77–80%, with companies below 70% facing documented increases in repeat visits and customer churn [4]

**How this user accesses the system:**
A mobile browser on a smartphone or tablet — no app install required. The Streamlit interface is designed for one-handed use in the field. Offline mode (cached responses for previously-queried equipment and sites) is a Phase 3 target; current deployment assumes minimal connectivity sufficient for a web request.

**Why standard AI fails this user:**
A junior tech can't Google "how do I service THIS Carrier RTU at THIS building today?" — the answer requires pulling from the Carrier service manual, the building's maintenance history, the relevant OSHA standards, and the site's prior service records simultaneously, and synthesizing them into a single actionable response.

---

### Tier 2 — The Small Shop Owner / Operations Manager
**The Economic Buyer**

**Who they are:**
Operations VP or service director at a mid-size HVAC, electrical, or facilities management company. 50–200 technicians, dozens of active service contracts. Competing against larger companies with better-resourced knowledge infrastructure.

**Jobs to be Done:**
- "Reduce first-call resolution failures without hiring a full-time training coordinator"
- "Give junior techs the confidence to handle unfamiliar equipment independently"
- "Know which knowledge gaps are causing the most missed diagnoses and return visits"
- "Reduce liability exposure from compliance mistakes in the field"
- "Level the playing field against competitors with better knowledge infrastructure"

**Pain Points (High Intensity):**
- First-time fix rates and safety incidents directly affect contract renewal and margins
- No affordable way to make institutional knowledge searchable at the point of need
- HVAC certificate programs cost $1,200–$15,000; trade school programs average $15,000–$20,000 before financial aid — per technician [7]. Experienced mentors are retiring and taking that knowledge with them
- Cannot have a senior tech supervising every junior worker on every job

**Value Proposition (Quantified):**
Each unnecessary return visit costs $150–$500 in direct labor and transportation costs, with fully-loaded costs (overtime, SLA penalties, customer attrition) reaching $800–$1,000 per incident [8]. If the tool saves each technician 30 minutes per day in information lookup time — the McKinsey benchmark suggests knowledge access tools can cut search time by up to 35% [5], though that study covered office workers — and improves first-time fix rates by 5 percentage points, a 200-technician organization avoids an estimated $1.5M annually in combined labor waste and return-visit costs. *(Conservative derived estimate based on median HVAC technician wage of $59,810/year [1] and industry truck roll benchmarks [8]; field-specific validation pending operator pilots.)*

---

### Tier 3 — The Municipality / Infrastructure Manager
**The Governance & Public Safety User**

**Who they are:**
City or county engineer responsible for public infrastructure — bridges, power systems, public buildings, water systems. Operating under tight budget constraints with deferred maintenance backlogs. Receives drone inspection data but lacks the expert staff to synthesize it into actionable maintenance decisions.

**Jobs to be Done:**
- "Know which zones need attention before something fails publicly"
- "Justify infrastructure budget decisions to elected officials with data, not intuition"
- "Make drone inspection data actionable without hiring expensive analysts"
- "Track anomaly trends across inspection cycles to prioritize maintenance"

**Pain Points (High public consequence):**
- Post-flight drone data is rich but requires expert manual review to be actionable — and many municipalities treat drone funding as a discretionary budget item rather than an operational necessity [9]
- Under-resourced departments can't afford continuous expert inspection coverage
- Decisions about which infrastructure gets repaired are driven by budget, not safety data, because safety data is inaccessible
- The global drone inspection and monitoring market is growing at 15–19% CAGR [9], but the tools that convert raw flight data into decision-ready intelligence remain expensive and expert-dependent

---

## Pain Points Summary

| Pain | Evidence | Citation | Who Feels It | Severity |
|------|----------|----------|-----------|---------|
| Information fragmentation at point of need | Multi-source synthesis not possible via search | — | Tier 1 | Critical |
| Time lost searching for information | Knowledge workers: 1.8 hrs/day; search tools cut this 35% | [5] | Tier 1 | High |
| Safety incidents from hazardous energy failures | 120 deaths + 50,000 injuries/yr preventable via LOTO compliance | [3] | Tier 1 | Critical |
| Sub-optimal first-time fix rate | Industry avg 77–80%; below 70% signals systemic issue | [4] | Tier 1, 2 | High |
| Cost of return visits | $150–$500 direct; $800–$1,000 fully loaded per truck roll | [8] | Tier 2 | High |
| Training cost per technician | Certificate: $1,200–$15,000; trade school: $15k–$20k | [7] | Tier 2 | High |
| Retiring workforce knowledge loss | Experienced mentors leaving; knowledge unstructured | — | Tier 1, 2 | Medium |
| Inspection data unusable post-flight | Drone data requires expert manual analysis | [9] | Tier 3 | High |
| Infrastructure monitoring access gap | Drone-as-a-service model exists because cities can't fund in-house fleets | [9] | Public | Critical |

---

## Architecture: Why AI, Why Now, Why This Approach

### The Core Problem with Pure Semantic Retrieval

Standard RAG systems search by semantic similarity — they return documents that *look like* the query. This misses three critical reasoning dimensions in field service intelligence:

- **Temporal reasoning:** "What has changed since the last inspection?" requires knowing the chronological sequence of events, not just finding similar documents
- **Causal reasoning:** "Why has Zone C kept failing?" requires tracing a cause-effect chain (anomaly → deferred maintenance → re-flag), not finding semantically similar anomaly records
- **Entity reasoning:** "Which zones has Inspector Patel worked on?" requires tracking a person across disjoint timeline segments, not keyword matching

### MAGMA: Multi-Graph Agentic Memory Architecture

Inspired by *MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents* (Jiang, Li, Li, Li; arXiv:2601.03236v1 [cs.AI], January 2026) [10], the target architecture represents field service memory as four orthogonal relation graphs:

| Graph | Edge type | Query type it answers |
|---|---|---|
| **Temporal Graph** | Strict chronological ordering of inspection events | WHEN — "When was Zone B last above baseline?" |
| **Causal Graph** | Directed cause → effect relationships (anomaly → maintenance → resolution) | WHY — "Why has Zone C been flagged repeatedly?" |
| **Entity Graph** | Tracks zones, equipment, inspectors across disjoint timeline segments | WHO/WHERE — "Which inspector worked on Zone A?" |
| **Semantic Graph** | Conceptually similar events (similar anomaly types across zones) | WHAT — "What anomaly types commonly co-occur?" |

**Query routing:** An intent-aware classifier detects query type (WHY / WHEN / WHO / WHAT) and routes retrieval to the appropriate graph via Adaptive Traversal Policy — a Heuristic Beam Search calibrated to the detected intent. This achieves a 0.700 overall accuracy score on the LoCo-Mo benchmark, vs. 0.481 for full-context baseline and 0.590 for the next best system (Nemori) [10].

**Current implementation vs. Phase 3 target:** The current system implements the graceful degradation and intent-routing principles that MAGMA extends — RAG with confidence scoring, domain-aware classifier, and spatial filters. The full multi-graph backend (temporal/causal/entity/semantic graph construction and traversal) is the Phase 3 production target. The Memory Graph visualization demonstrates the architecture with structured data derived from the existing corpus.

**Why this matters for social impact:** A junior technician asking "WHY does this zone keep failing?" deserves a causal answer — the maintenance chain that was missed, the equipment history that explains the pattern — not a semantic similarity match that returns other records mentioning "zone failure." Structured relational memory is the difference between a search engine and a reasoning system.

### Graceful Degradation: The Anti-Hallucination Layer

The second architectural differentiator: the system is designed with three explicit routing paths after retrieval and confidence scoring.

- **HIGH confidence:** Answer with citation and source — the information is clearly present
- **PARTIAL confidence:** Surface the conflict and flag uncertainty — two sources disagree, human judgment required
- **LOW confidence:** Escalate without answering — the information is not in the corpus

The **LOW path never calls the LLM.** The escalation message is programmatic. This is a safety feature, not a limitation.

> "An AI that confidently gives a wrong answer to a technician about to service high-voltage equipment is not a useful tool. It is a liability. The system is designed to escalate before it guesses."

In the MAGMA paper, adversarial query performance is where structured memory's advantage is most pronounced: 0.742 for MAGMA vs. 0.205 for full-context baseline and 0.325 for Nemori — because causal and entity-consistent traversal avoids the semantically similar but structurally irrelevant results that cause hallucinations [10]. This directly supports the graceful degradation design philosophy.

---

## Social Impact Framing

### Economic Empowerment
The knowledge gap between a 22-year-old junior tech and a 20-year veteran is real, consequential, and structural — not a matter of individual ability. The veteran knows where to look, who to call, and what the equipment history means. The junior tech doesn't, because that knowledge was never made accessible. This system makes it accessible at the exact point of need, for every worker regardless of employer resources.

### Safety Equity
OSHA estimates that proper lockout/tagout compliance prevents 120 deaths and 50,000 injuries annually [3] — meaning these incidents are preventable in aggregate, but the risk is distributed unequally. Workers at under-resourced companies, without mobile access to the right documentation at the right moment, bear a disproportionate share of that risk. The anti-hallucination design is a safety equity intervention: the system escalates when uncertain rather than returning a confident wrong answer.

### Infrastructure Governance
The quality of public infrastructure monitoring should not depend on the size of the municipal budget. The global drone inspection market is projected to reach $74 billion by 2035 [9], but the intelligence layer that converts raw flight data into actionable decisions remains expensive and expert-dependent. The same graceful degradation principle that protects a junior HVAC tech from a confident wrong answer also protects a city engineer from acting on a misread anomaly: the system surfaces conflicts and escalates uncertainty rather than producing false confidence. AI-powered inspection intelligence makes that layer accessible to municipalities that cannot pay enterprise prices for human expert teams.

---

## Competitive Positioning

| Alternative | What They Do | Where They Fall Short |
|---|---|---|
| ServiceMax | Enterprise FSM — asset management, work orders, scheduling | Custom enterprise pricing; requires Salesforce; not recommended for fewer than 50 technicians; not designed for the technician in the field [6] |
| UpKeep | Mobile-first CMMS for smaller maintenance teams; widely adopted by small shops | Asset/work-order management, not multi-source knowledge retrieval; no confidence routing or conflict detection |
| Guru / Tettra | Team knowledge bases with mobile access | General-purpose wikis — not structured around site-specific, model-specific field queries; no graceful degradation |
| Google / generic search | General information retrieval | Cannot synthesize multi-source, model-specific, site-specific answers |
| Standard RAG chatbots | Semantic similarity retrieval | Miss temporal, causal, and entity reasoning; hallucinate when uncertain |
| Manufacturer support lines | Equipment-specific technical support | Not 24/7; doesn't know the site's service history |
| Physical binders / PDFs | Static documentation | Not searchable; out of date; not in the tech's hand at the right moment |

**Sustainable differentiation:**
1. **MAGMA-inspired multi-graph memory** — reasons across time, causality, and entity permanence, not just semantic similarity [10]
2. **Graceful degradation** — the only system designed to escalate rather than hallucinate when uncertain
3. **Domain-agnostic pipeline** — HVAC, drone inspection, power grid: same architecture, new corpus

---

## Dashboard & Visualization Design

### 1. Impact Counter (Home Page)
Human-readable numbers, not system metrics. For the demo, projected figures are calculated from eval-suite runs and stated assumptions — clearly labeled as such:
- "Projected hours saved (100 technicians/month): 847" *(30 min/day × technicians × working days)*
- "Safety escalations in this demo session: 23" *(live LOW-path routing count from actual queries)*
- "Confident answers with cited source: 142" *(HIGH-confidence responses from eval suite)*

Labeling projected vs. observed matters — interviewers and reviewers will ask. Live counters (escalations, HIGH responses) update in real time during the demo; projected figures are clearly marked as model estimates.

Every escalation is a hallucination that didn't happen to a worker in the field.

### 2. Memory Graph (MAGMA Visualization — `pages/6_Connect_the_Dots.py`) ✅ Complete
The centerpiece wow factor. Interactive PyVis graph showing the 4 relational dimensions of inspection memory:
- Nodes = inspection events (HVAC service records or drone anomaly detections)
- Edges = typed relationships (temporal / causal / semantic / entity) — constructed from existing Chroma corpus, not a live graph backend
- Query traversal animation: watch the agent navigate the graph to answer a WHY, WHEN, WHO, or WHAT query
- Domain switcher: HVAC service history ↔ Drone inspection records
- Inspired by: Jiang et al., "MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents," arXiv:2601.03236, 2026 [10]

*Note: This page is the centerpiece demo feature for the v1 release. The full graph backend (dynamic edge construction, Adaptive Traversal Policy) is Phase 3.*

### 3. Pipeline Trace Panel (Agent Pages)
Step-by-step visualization of a query moving through the pipeline:
```
[1] CLASSIFY    → ANOMALY_QUERY  (rule-based fast path, ~5ms)
[2] FILTER      → spatial filter: zone_id = Zone-C
[3] RETRIEVE    → 7 results from inspection_records, historical_baselines
[4] SCORE       → top score: 0.91, no conflicts → HIGH
[5] ANSWER      → "3 anomalies flagged..." [inspection_rec_aug25.json]
```

### 4. Knowledge Gap Map — The Honesty Report
Zone × confidence heat map: every red cell is a question the system refused to answer rather than guess. Each gap is a hallucination that didn't happen. Click any red cell in the live demo to see the escalation message that fires instead of an LLM response. This is how you find knowledge gaps before they become incidents — and how you demonstrate the anti-hallucination design working under adversarial conditions.

### 5. Guided Walkthrough UX
The demo experience is a 6-step guided walkthrough from a single persona — the junior field technician. Key design decisions:
- **Home.py:** staggered CSS fade-in on scenario lines; three inline routing pills (HIGH / PARTIAL / LOW); single "Begin Walkthrough →" CTA
- **Session state handoff:** Zone C selection on the Site Map pre-fills the Drone Agent query; an arrival callout fires once on Step 3 to make the connection explicit
- **Route-specific aha callouts on Step 1:** each of the three routing paths has a differentiated in-context explanation when it fires — not a generic label
- **Dismissible walkthrough banners** and a sidebar progress tracker (past ✓ / current → / future numbered)
- **End summary card on Step 6** with headline metrics and a "← Start over" button that clears all walkthrough session state

The walkthrough is a product decision, not decoration — it ensures every reviewer reaches the LOW-path escalation and the Zone C handoff, which are the two moments that explain why this system is differentiated from a standard RAG chatbot.

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|-------------|
| Hours saved per technician per day | 30 min | Baseline lookup time vs. agent response time |
| First-time fix rate improvement | +5 percentage points | Operator-reported outcomes vs. historical baseline |
| Safety escalations (LOW-path routing) | Traceable, non-zero | Every LOW response is a hallucination prevented |
| Knowledge gaps identified | Visible in Knowledge Gap Map | LOW-confidence zone distribution across corpus |
| Query routing accuracy (MAGMA intent) | > 90% | Classifier eval suite |
| Coverage (HIGH or PARTIAL on ground truth) | > 80% | Eval suite: ground_truth.json |
| Hallucination rate | < 2% | Adversarial eval: no LOW query returns HIGH |

---

## Demo Narrative (5–7 Minutes)

1. **Open with the story** (30 sec): "Imagine you're a 22-year-old HVAC tech on your 4th job today. You've never seen this unit before. The manual is in the truck. You have 30 minutes. OSHA tells us this exact gap — not knowing the right procedure at the right moment — causes 50,000 preventable injuries a year."
2. **Show the impact counter** (30 sec): "Running on our eval suite and a projected 100-technician deployment, this system would have saved 847 hours and flagged 23 situations where a wrong answer would have mattered to someone's safety."
3. **HIGH demo query** (90 sec): Zone C anomaly query → pipeline trace lights up → confident answer with citation and source
4. **PARTIAL demo query** (90 sec): Baseline comparison → conflict surfaces between two inspection records → "here's what the data disagrees on — human judgment required"
5. **LOW demo query** (60 sec): Zone X (no data) → escalation, not hallucination → "the system doesn't guess. It tells you where the knowledge gap is."
6. **Memory Graph** (90 sec): "Here's what makes this different from a search engine. This WHY query traverses the causal graph: anomaly detected → maintenance deferred → re-flagged. That's not retrieval. That's reasoning. Inspired by the MAGMA architecture from UT Dallas — current system demonstrates the routing principles; full graph backend is Phase 3."
7. **Close** (30 sec): "We didn't build a search engine. We built a system that knows when NOT to answer. In field service, that distinction is the difference between a useful tool and a liability — and between a junior tech who gets hurt and one who doesn't."

---

## Pricing & Go-to-Market

**Hypothesis:** Per-seat SaaS, priced below the training cost it replaces.

| Tier | Target | Price Point | Rationale |
|------|--------|-------------|-----------|
| Small Shop | 10–50 technicians | $25–$40/seat/month | Below the cost of one avoidable truck roll per tech per year |
| Mid-Market | 50–200 technicians | $20–$30/seat/month (volume) | Competes on ROI vs. training coordinator hire |
| Municipality | Public infrastructure teams | Grant-funded / public-sector pricing | Infrastructure governance tier; FEMA, HUD, and DOT grant eligibility for safety tools |

**GTM entry point:** Trade associations (ACCA for HVAC, NECA for electrical) — they have direct access to small shop owners and run continuing education programs where this tool is a natural fit. Content partnerships with certification programs (NATE, EPA 608) as a study and field-reference tool.

**Land and expand:** Start with HVAC (clearest safety story, existing corpus), expand to electrical and facilities via the domain-agnostic pipeline.

---

## Phase Roadmap

| Phase | What Ships | Social Impact Milestone |
|-------|-----------|------------------------|
| Phase 1 (done) | RAG pipeline, confidence routing, eval framework, HVAC domain | Proves the graceful degradation model |
| Phase 2 (current) | Drone domain, classifier, session memory, spatial filters | Dual-domain demo, infrastructure governance story |
| Demo Release (v1) | MAGMA Memory Graph ✅, Guided Walkthrough UX ✅, Pipeline Trace ✅ | Full social impact narrative, differentiated demo experience |
| Phase 3 | Real MAGMA graph backend, offline mode, live deployment, longitudinal tracking | Production-grade reasoning; field connectivity constraint lifted |

---

## Risks & Mitigations

| Risk | Current Mitigation | Phase 3 Target |
|---|---|---|
| **Field connectivity** — field workers often have limited or intermittent signal | Streamlit app is lightweight; requires only a minimal web request per query | Response caching for previously-queried equipment and sites (offline mode) |
| **Synthetic corpus** — current demo data is generated, not production records | All data generated via Claude API from realistic field scenarios; statistically plausible and domain-accurate | Corpus ingestion pipeline from real FSM and document management systems at operator onboarding |
| **Semantic model number blindness** — near-miss equipment can score high similarity | Known limitation; XR13 ≈ XR15 scores 0.82 similarity and may route PARTIAL instead of LOW; documented in eval suite | Hybrid retrieval: BM25 + dense, or explicit model-number metadata filter |
| **Data freshness** — corpus is static per deployment | No live sync currently; corpus reflects the state at ingestion time | Scheduled re-ingestion from connected FSM at configurable intervals |

---

## References

[1] U.S. Bureau of Labor Statistics. *Heating, Air Conditioning, and Refrigeration Mechanics and Installers.* Occupational Outlook Handbook, 2024–2034. https://www.bls.gov/ooh/installation-maintenance-and-repair/heating-air-conditioning-and-refrigeration-mechanics-and-installers.htm

[2] SightCall. *52 Field Service Stats That You Need to Know.* https://sightcall.com/blog/52-field-service-stats-that-you-need-to-know/

[3] U.S. Occupational Safety and Health Administration. *Control of Hazardous Energy (Lockout/Tagout) — Overview.* 29 CFR 1910.147. https://www.osha.gov/control-hazardous-energy — and OSHA Fact Sheet FS-3529: https://www.osha.gov/sites/default/files/publications/OSHAFS3529.pdf

[4] CompareSoft / Service Council. *What Is First-Time Fix Rate & How to Improve Your FTFR.* https://comparesoft.com/field-service-management-software/first-time-fix-rate-ftfr/ — IBM. *What is First-Time Fix Rate (FTFR)?* https://www.ibm.com/think/topics/first-time-fix-rate

[5] McKinsey Global Institute. *The Social Economy: Unlocking Value and Productivity Through Social Technologies.* 2012. Cited in: ProProfs. *Cut Time Spent Searching for Information With Knowledge Base Software.* https://www.proprofskb.com/blog/workforce-spend-much-time-searching-information/

[6] SelectHub / Capterra. *ServiceMax Reviews 2026: Pricing, Features & More.* https://www.selecthub.com/p/field-service-software/servicemax/ — Capterra: https://www.capterra.com/p/107954/ServiceMax/

[7] HVACCareerNow. *How Much Does HVAC Training Cost?* https://hvaccareernow.com/articles/the-cost-of-hvac-training-programs — SkillCat. *HVAC Training Cost in 2026: Tuition, Tools & Fees Guide.* https://www.skillcatapp.com/post/hvac-training-cost-tuition-tools-fees

[8] SightCall. *How to Reduce Truck Rolls — Truck Roll Optimization.* https://sightcall.com/blog/how-to-reduce-truck-rolls/ — CareAR. *What is a truck roll and how to reduce them?* https://carear.com/blog/what-is-a-truck-roll-how-to-reduce-them/ — Blitzz. *What is Truck Roll? The True Cost of Truck Rolls for Businesses.* https://blitzz.co/blog/what-is-truck-roll-the-true-cost-of-truck-rolls-for-businesses

[9] MarketsandMarkets. *Drone Inspection and Monitoring Market Size, Share & Trends Analysis.* https://www.marketsandmarkets.com/Market-Reports/drone-inspection-monitoring-market-99915267.html — Hammer Missions. *Why Infrastructure & Energy Are Driving the Next Phase of Drone Inspection Market Growth.* https://www.hammermissions.com/post/next-phase-of-drone-inspection-market-growth

[10] Jiang, Dongming; Li, Yi; Li, Guanpeng; Li, Bingzhe. *MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents.* arXiv:2601.03236v1 [cs.AI], 6 January 2026. https://arxiv.org/abs/2601.03236
