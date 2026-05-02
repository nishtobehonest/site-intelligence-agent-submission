# Site Intelligence Agent

**Site Intelligence Agent | April 2026**

---

## Course Report

**[ENMGT-AI-Site-Intelligence-Agent-nishchay-vishwanath.pdf](ENMGT-AI-Site-Intelligence-Agent-nishchay-vishwanath.pdf)**

Full written report covering problem framing, system architecture, evaluation methodology, Phase 1 results, and Phase 2 design. Start here for the complete picture.

---

## What This Is

A RAG-based assistant for frontline field workers (HVAC technicians, drone inspectors, field engineers) that retrieves relevant documentation, past job history, and compliance requirements in real time during a job.

The system spans two domains — **HVAC** (Phase 1, complete) and **drone inspection** (Phase 2) — handled by a dual-domain `SiteIntelligenceAgent` with a shared pipeline and domain-aware classifier, session memory, and spatial zone filtering.

The core design question: **what happens when the retrieved context is incomplete or contradictory?** Most RAG systems stop at "the model found something." This system is designed for when it does not.

---

## Three Routing Paths (Graceful Degradation)

| Confidence | Trigger | Response |
|------------|---------|----------|
| **HIGH** | Top result similarity > 0.75, no conflict | Answer with source citations |
| **PARTIAL** | Conflicting sources, or similarity 0.50–0.75 | Answer with explicit conflict flag and both sources |
| **LOW** | Similarity < 0.50, or no results | Escalation message with what was and was not found |

---

## Streamlit Walkthrough App

A 6-page persona-driven walkthrough ships with the project (`streamlit run Home.py`):

| Page | What it does |
|------|--------------|
| Home | Cinematic scenario intro with CTA |
| 1 — Ask the Agent | Interactive demo of all three confidence paths (HIGH / PARTIAL / LOW) |
| 2 — View the Site | Dual-domain site overview |
| 3 — Inspect a Zone | Drone agent with Zone C pre-loaded, session memory and pipeline trace |
| 4 — See the Proof | Eval metrics dashboard |
| 5 — Find the Gaps | "Honesty Report" — coverage heatmap (green = answered, red = escalated) |
| 6 — Connect the Dots | Memory graph finale and summary card |

---

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# Add documents to data/raw/ (see Data Sources below)

# Ingest HVAC collections (Phase 1)
python src/ingest.py

# Ingest drone inspection collections (Phase 2)
python src/ingest.py --domain drone

# Ingest both domains
python src/ingest.py --domain all

# Generate synthetic HVAC job history
python src/generate_synthetic.py

# Generate synthetic drone inspection data
python src/generate_drone_data.py

# Launch Streamlit walkthrough app
streamlit run Home.py

# Run CLI demo with three preset queries (HIGH / PARTIAL / LOW)
python demo/demo.py

# Run evaluation suite
python eval/run_eval.py
```

---

## Data Sources

**HVAC domain:**

| Collection | What | Where to get it |
|------------|------|-----------------|
| `osha` | 29 CFR 1910.147 (Lockout/Tagout), 29 CFR 1910.303 (Electrical Safety) | osha.gov (public domain) |
| `manuals` | HVAC equipment manuals (Carrier 48LC 2017/2023, Lennox SL280, Trane XR15) | Manufacturer sites (public) |
| `job_history` | Synthetic job records | Run `generate_synthetic.py` |

**Drone inspection domain:**

| Collection | What | Where to get it |
|------------|------|-----------------|
| `inspection_records` | Synthetic drone inspection records | Run `generate_drone_data.py` |
| `historical_baselines` | Historical baseline metrics per zone | Run `generate_drone_data.py` |
| `compliance_docs` | OSHA 1926.452 scaffold safety | osha.gov (public domain) |

---

## Project Structure

```
src/
  assistant.py           # FieldServiceAssistant (HVAC) + SiteIntelligenceAgent (dual-domain)
  classifier.py          # Rule-based + LLM fallback query classification
  session_memory.py      # Zone/equipment/time entity tracking across turns
  retriever.py           # Vector retrieval, spatial filter, conflict detection
  confidence.py          # Confidence scoring + routing decision
  degradation.py         # Graceful degradation (HIGH / PARTIAL / LOW)
  llm.py                 # LLM wrapper (Anthropic / OpenAI / Gemini)
  ingest.py              # Document loading + Chroma indexing (HVAC + Drone)
  generate_synthetic.py  # Synthetic HVAC job history
  generate_drone_data.py # Synthetic drone inspection data

pages/
  1_Ask_the_Agent.py     # Three-path confidence demo
  2_View_the_Site.py     # Site overview
  3_Inspect_a_Zone.py    # Drone agent + session memory trace
  4_See_the_Proof.py     # Eval metrics dashboard
  5_Find_the_Gaps.py     # Honesty report / coverage heatmap
  6_Connect_the_Dots.py  # Memory graph finale

eval/
  ground_truth.json      # 50 HVAC query-answer pairs
  adversarial.json       # 20 out-of-corpus queries
  contradictions.json    # 15 conflict scenarios
  run_eval.py            # Evaluation runner

demo/
  demo.py                # CLI demo for live presentation
```

---

## Troubleshooting

**Duplicate chunks in Chroma** (if ingest was run more than once):
```bash
rm -rf data/chroma_db/
python src/ingest.py --domain all
```
Never run `ingest.py` twice without clearing `data/chroma_db/` first — each run appends to existing collections.

**Switching LLM providers** — set `LLM_PROVIDER` in `.env` (`anthropic` / `openai` / `gemini`). Current working model: `gemini-2.5-flash`.

**Tuning confidence thresholds** without code changes:
```bash
CONFIDENCE_HIGH_THRESHOLD=0.80 CONFIDENCE_PARTIAL_THRESHOLD=0.55 python demo/demo.py
```

---

## References

1. Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS 2020. https://arxiv.org/abs/2005.11401
2. Gao et al. "RAG for Large Language Models: A Survey." arXiv 2023. https://arxiv.org/abs/2312.10997
3. OSHA Field Operations Manual. U.S. DOL, 2024. https://www.osha.gov/enforcement/directives/cpl-02-00-164
4. Anthropic. Claude Model Card. 2024. https://www.anthropic.com/claude
