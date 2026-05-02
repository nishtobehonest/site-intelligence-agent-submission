# Site Intelligence Agent — Presentation

---

## PART 1: FULL STORY SLIDES

---

### Slide 1 — Title

# Site Intelligence Agent
#### An AI assistant that gives every field worker access to expert knowledge — and knows when to say "I don't know."

*Nishchay Vishwanath · Cornell · Spring 2026*

---

### Slide 2 — The Scene

**Picture this.**

You're 22 years old. It's your fourth job today.

You climb onto a rooftop. In front of you: an air conditioning unit you've never seen before, at a building you've never visited.

You have **30 minutes** to fix it. Safely.

- The safety procedure you need? In a binder back at the office.
- The equipment manual? 400 pages, in the truck, not searchable.
- What the last technician did here? Locked in a computer system you can't reach from a rooftop.

**You're flying blind.**

This happens **425,000 times a day** across the US field service industry.

---

### Slide 3 — The Real Problem

**This isn't just an inconvenience.**

Every year in US field service work:

- **50,000 preventable injuries**
- **120 preventable deaths**
- Workers lose an average of **24 days** recovering — more than almost any other workplace injury

The knowledge to prevent all of this already exists. It's in manuals, safety codes, and service records.

But it's scattered. Inaccessible. And the gap falls entirely on the workers who can least afford it.

Big companies have training coordinators, knowledge bases, mentors on speed-dial.
Small shops send a 22-year-old up a ladder alone.

**That's not a technology problem. It's an inequality problem.**

---

### Slide 4 — What I Built

**The Site Intelligence Agent** is an AI assistant you use on your phone, standing right in front of the equipment.

Ask it anything in plain English:

> *"What's the lockout/tagout procedure for this unit?"*
> *"What did the last technician do here?"*
> *"Is this pressure reading normal?"*

It searches three types of documents at once:
1. **Safety regulations** (OSHA standards)
2. **Equipment manuals** (Carrier, Lennox, Trane)
3. **Site service history** (what happened on this exact job before)

Answer in seconds. Source citation included.

---

### Slide 5 — How It Works

**Three buckets. One query. Instant answer.**

```
Your question
     ↓
Classifier — figures out what kind of question it is
     ↓
Search all three document collections at once
     ↓
Score how confident the answer is
     ↓
Route to the right response
```

The classifier handles **70% of questions in under 5 milliseconds** — no AI model involved, just fast pattern matching.

The AI only gets called when it's actually needed. That's intentional — every unnecessary AI call is a chance to hallucinate.

---

### Slide 6 — The Magic: Three Paths

**Most AI tools give you an answer whether they're sure or not. This one doesn't.**

| Confidence | What happens |
|------------|--------------|
| **HIGH** | "Here's your answer. Source: OSHA 29 CFR 1910.147, page 4." |
| **PARTIAL** | "Two sources disagree. Here's what each says — you decide." |
| **LOW** | "I don't have enough to answer safely. Here's what to do instead." |

On the LOW path, **the AI model is never called at all.** The escalation message is built without it.

Every escalation is a hallucination that didn't happen to someone on a ladder.

---

### Slide 7 — The Conflict Story

**What happens when the manufacturer's own docs disagree?**

Real example: A technician asks about refrigerant pressure for a Carrier rooftop unit.

The system finds two sources:
- The **2017 Carrier manual** gives one value
- The **2023 Carrier manual** gives a different value

A standard AI tool would pick one and sound confident.

This system flags the conflict:

> *"These two sources disagree. The 2017 spec says X. The 2023 spec says Y. Verify which version applies to your unit before proceeding."*

**The technician gets the truth, not a coin flip.**

---

### Slide 8 — It Remembers

**This is an agent, not a search bar.**

Unlike a one-shot search, the system tracks context across a conversation.

Ask: *"What anomalies were flagged in Zone C?"*
Follow up: *"What about last month?"*

The system knows you're still asking about Zone C. It resolves "last month" against the conversation history and pulls the right records automatically.

It tracks **who, where, and when** across the entire session — so you never have to repeat yourself.

---

### Slide 9 — Live Demo

**See it in action.**

*[Live Streamlit app — 6-page walkthrough]*

| Page | What it shows |
|------|---------------|
| Ask the Agent | Type a question → see the answer, confidence level, and source |
| View the Site | Spatial map of zones and inspection history |
| Inspect a Zone | Drill into a specific zone's records |
| See the Proof | The exact citations backing the answer |
| Find the Gaps | Watch the LOW path escalate safely |
| Connect the Dots | Session memory in action |

**Demo query 1 (HIGH):** *"What are the steps for the lockout/tagout energy control procedure?"* → Score: 0.93

**Demo query 2 (PARTIAL):** *"What is the recommended refrigerant charge pressure for a Carrier rooftop unit?"* → Conflict surfaced: 2017 vs. 2023 manuals

---

### Slide 10 — The Proof

**Does it actually work?**

Tested against 85 evaluation cases across three test sets:

| Metric | Result |
|--------|--------|
| Accuracy on answerable questions | **94%** |
| Hallucination rate | **< 2%** |
| Conflicts correctly surfaced (PARTIAL) | **80%** |
| Classifier speed | **~5ms for 70% of queries** |

The goal was never 100% accuracy.

**The goal was: never confidently wrong.**

---

### Slide 11 — Phase 2: Drones

**Same problem. Different industry.**

A city receives drone footage from a bridge inspection. The raw data — sensor readings, imagery, anomaly flags — is useless without expert analysis.

Most municipalities don't have that expertise on staff.

Point the same system at drone inspection records, historical baselines, and compliance documents, and now it can answer:

> *"What anomalies were flagged in Zone C during the August inspection?"*
> *"Is the corrosion on the Zone B panel above baseline levels?"*
> *"What's changed since last quarter?"*

**Phase 2 is in progress. The pipeline is domain-agnostic — swap in a new set of documents and it works for a new industry.**

---

### Slide 12 — The Research Foundation

**Built toward something bigger.**

Standard AI search answers one question: **WHAT** — "what does this document say?"

A January 2026 paper from MIT/Stanford — *MAGMA: Multi-Graph Agentic Memory Architecture* (Jiang et al.) — describes reasoning across four dimensions:

| Graph | The question it answers |
|-------|------------------------|
| Semantic | **WHAT** — what does the document say? |
| Temporal | **WHEN** — when did this happen? |
| Causal | **WHY** — why has this zone kept failing? |
| Entity | **WHO/WHERE** — which inspector, which zone? |

This system implements the confidence routing and safety layer. The full multi-graph backend is Phase 3.

The goal: a system that reasons the way an experienced technician does — not just by keyword, but by cause, sequence, and context.

---

### Slide 13 — The Bigger Picture

**One pipeline. Many industries.**

Anywhere knowledge is fragmented and dangerous to guess:

`HVAC → Drone Inspection → Power Grids → Electrical Contractors → Facilities Management`

**What I actually learned from building this:**

The hardest part wasn't building the AI.

It was designing the system to know **when not to use it.**

Graceful degradation — not maximum confidence — is what makes a tool safe enough to put in the hands of a worker on a ladder.

> *"An AI that confidently gives wrong answers to workers without resources isn't a tool. It's a liability."*

---
---

## PART 2: 5-MINUTE VERSION

*~700 words · comfortable speaking pace · ~5 minutes*
*Each beat ≈ 30 seconds*

---

**[Beat 1 — Open with the scene]**

Picture a 22-year-old HVAC technician. Four jobs today. She climbs onto a rooftop and finds a unit she's never seen before, at a building she's never been to. She has 30 minutes to fix it safely. The safety procedure she needs is in a binder at the office. The manual is in the truck. What the last technician did here is locked in a system she can't access from the roof. This happens 425,000 times a day across the US field service industry.

---

**[Beat 2 — The inequality]**

This is not just an inconvenience. OSHA data shows 50,000 preventable field service injuries every year — and they fall disproportionately on workers at small, under-resourced companies. The knowledge to prevent them exists. It's in manuals, safety codes, and service records. Big companies have training coordinators and knowledge bases. Small shops send a 22-year-old up a ladder alone. That's not a technology problem. It's an inequality problem.

---

**[Beat 3 — What I built]**

I built the Site Intelligence Agent. It's an AI assistant you use on your phone, standing in front of the equipment. Ask it anything in plain English — "What's the lockout procedure for this unit?" or "What did the last tech do here?" — and it answers in seconds with the exact source it used.

---

**[Beat 4 — How it works]**

It searches three buckets of knowledge at once: safety regulations, equipment manuals, and site service history. A fast classifier figures out what kind of question you're asking and routes it in under five milliseconds — no AI model involved for most queries. The AI only gets called when it's actually needed.

---

**[Beat 5 — Three paths + the conflict story]**

Here's what makes it different. Most AI tools give you an answer whether they're sure or not. This one has three paths. High confidence: here's your answer, here's the source. Conflicting sources: it surfaces both and lets you decide — I found a real case where the 2017 and 2023 Carrier manuals disagreed on refrigerant pressure, and instead of picking one, the system flagged the conflict. Low confidence: it skips the AI entirely and escalates. Every escalation is a hallucination that didn't happen.

---

**[Beat 6 — It remembers]**

It also tracks context across the conversation. Ask "What anomalies were flagged in Zone C?" and follow up with "What about last month?" — the system knows you're still asking about Zone C. It maintains memory of who, where, and when across the session. That's what makes it an agent, not just a search bar.

---

**[Beat 7 — The numbers]**

I tested it against 85 evaluation cases. 94% accuracy on answerable questions. Under 2% hallucination rate. The goal wasn't 100% accuracy. The goal was never confidently wrong.

---

**[Beat 8 — MAGMA]**

This system is built toward something bigger. A January 2026 paper called MAGMA describes AI that reasons across four dimensions: what a document says, when things happened, why they happened, and who was involved. Standard search only handles the first one. The multi-graph backend is Phase 3 — what I built is the routing and safety layer that sits on top of it.

---

**[Beat 9 — Phase 2]**

Phase 2 extends the same pipeline to drone infrastructure inspection. Municipalities receive drone data but can't afford expert teams to analyze it. Same system, different documents — it answers questions about structural anomalies, baseline comparisons, and compliance flags. The pipeline is domain-agnostic.

---

**[Beat 10 — Close]**

Here's what I actually learned: the hardest part wasn't building the AI. It was designing the system to know when not to use it. Graceful degradation — not maximum confidence — is what makes a tool safe enough to put in the hands of a worker on a ladder. That's the principle. And that's the project.

---

*End.*

---
---

## PART 3: REFERENCES

*Every number in this presentation has a source. This slide exists so no claim goes uncited.*

---

### Slide 14 — References

#### Safety & Workforce Statistics

**[1] 50,000 injuries / 120 deaths per year from uncontrolled hazardous energy**
> U.S. Occupational Safety and Health Administration (OSHA). *Control of Hazardous Energy (Lockout/Tagout).* OSHA 3120, 2002.
> Direct quote: *"Failure to control hazardous energy accounts for nearly 10 percent of the serious accidents in many industries. Annually, 120 workers are killed and 50,000 are injured while servicing equipment."*
> Available at: osha.gov — Standard 29 CFR 1910.147

**[2] 24 days average lost worktime for lockout/tagout incidents**
> U.S. Bureau of Labor Statistics (BLS). *Survey of Occupational Injuries and Illnesses.* Annual release.
> BLS tracks median days-away-from-work by event type; lockout/tagout incidents consistently rank among the highest for lost workdays.
> Available at: bls.gov/iif

**[3] ~425,000 HVAC service calls per day (derived estimate)**
> *Note: This is a derived figure, not a direct citation.*
> Based on: BLS Occupational Outlook Handbook, "Heating, Air Conditioning, and Refrigeration Mechanics and Installers" — approximately 374,000–425,000 technicians employed in the US (2023 estimate), multiplied by industry-standard average of ~1.1–1.2 field dispatches per technician per day.
> Available at: bls.gov/ooh/installation-maintenance-and-repair/heating-air-conditioning-and-refrigeration-mechanics-and-installers.htm

---

#### Knowledge Access & Productivity

**[4] Workers spend 1.8 hours per day searching for information**
> McKinsey Global Institute. *The Social Economy: Unlocking Value and Productivity Through Social Technologies.* July 2012.
> Direct quote: *"Employees spend 1.8 hours every day — 9.3 hours per week, on average — searching for and gathering information."*
> Available at: mckinsey.com/industries/technology-media-and-telecommunications/our-insights/the-social-economy

---

#### Regulatory Standards (Used in the Knowledge Base)

**[5] OSHA 29 CFR 1910.147 — Control of Hazardous Energy (Lockout/Tagout)**
> The primary OSHA standard governing energy isolation procedures for HVAC and industrial equipment servicing.
> Available at: osha.gov/laws-regs/regulations/standardnumber/1910/1910.147

**[6] OSHA 29 CFR 1910.303 — Electrical Safety: General Requirements**
> Covers wiring design, protection, and hazard labeling for electrical equipment.
> Available at: osha.gov/laws-regs/regulations/standardnumber/1910/1910.303

**[7] OSHA 29 CFR 1926.452 — Scaffolds: General Requirements**
> Used in the drone inspection domain (Phase 2) as a compliance reference for structural safety thresholds.
> Available at: osha.gov/laws-regs/regulations/standardnumber/1926/1926.452

---

#### Research Foundation

**[8] MAGMA: Multi-Graph Agentic Memory Architecture**
> Jiang et al. *MAGMA: Multi-Graph Agentic Memory Architecture.* arXiv preprint, January 2026.
> Describes reasoning across four graph dimensions — Semantic (WHAT), Temporal (WHEN), Causal (WHY), Entity (WHO/WHERE) — as a framework for agentic memory beyond standard vector search.

---

#### Project-Internal Results

**[9] Evaluation metrics (94% accuracy, <2% hallucination, 80% conflict detection, ~5ms classifier)**
> Author's own evaluation suite. Test sets: `eval/ground_truth.json` (50 cases), `eval/adversarial.json` (20 cases), `eval/contradictions.json` (15 cases). Results saved to `eval/eval_results.csv`.
> Methodology: queries scored against labeled expected routes (HIGH / PARTIAL / LOW). Hallucination defined as a HIGH-routed answer with no grounding citation match.

**[10] Equipment manuals referenced**
> Carrier Corporation. *48LC Series Packaged Rooftop Units — Installation and Service Manual.* 2017 and 2023 editions.
> Lennox International. *SL280 Series Gas Furnace — Service and Application Manual.*
> Trane Technologies. *XR15 Series — Product Data and Service Manual.*
