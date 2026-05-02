# Full Walkthrough Onboarding Experience

## Rating

**Current plan quality: 9/10.**

The story arc, differentiating moments, persona continuity, and implementation details are strong enough to build. The remaining 1 point is execution risk: Streamlit CSS behavior, clickable heatmap interactions, and session-state handoffs should be validated in the running app.

---

## Navigation Source Of Truth

Use the original walkthrough navigation shown in the target sidebar:

```text
Home
Ask the Agent
View the Site
Inspect a Zone
See the Proof
Find the Gaps
Connect the Dots
```

This is the desired product structure. Do **not** compress the walkthrough into fewer public pages. Each major story beat should be its own sidebar destination so the user can see the full journey and understand where they are.

The sidebar should have two layers:

```text
Home
Ask the Agent
View the Site
Inspect a Zone
See the Proof
Find the Gaps
Connect the Dots

-- WALKTHROUGH --------
-> 1. Ask the Agent
   2. View the Site
   3. Inspect a Zone
   4. See the Proof
   5. Find the Gaps
   6. Connect the Dots
```

The top section is the normal app navigation. The lower `WALKTHROUGH` section is the guided progress tracker.

---

## Story Arc

```text
Home                    <- Cinematic scenario. One CTA.
  -> Begin Walkthrough
Step 1: Ask the Agent   <- HIGH / PARTIAL / LOW routing paths explained.
  -> That was one unit. Here's your whole site.
Step 2: View the Site   <- Zone C is flagged HIGH.
  -> Investigate Zone C
Step 3: Inspect a Zone  <- Query is preloaded from the selected zone.
  -> Next: The proof
Step 4: See the Proof   <- Eval dashboard, 85 test cases, near-miss filter.
  -> Next: The honesty report
Step 5: Find the Gaps   <- Honesty Report: hallucinations that did not happen.
  -> Next: How memory connects it
Step 6: Connect the Dots <- Memory graph, causal edge example, end summary card.
       End: Start over clears walkthrough state.
```

**Single persona throughout:** the field technician. Do not switch to site manager, engineer, or architect language. Each page should answer what the technician would care about.

---

## Target Files

The desired page files should map to the visible sidebar labels:

| Sidebar Label | Target File | Purpose |
|---|---|---|
| `Home` | `Home.py` | Opening scenario and single start CTA |
| `Ask the Agent` | `pages/1_Ask_the_Agent.py` | HVAC agent, HIGH/PARTIAL/LOW routing demo |
| `View the Site` | `pages/2_View_the_Site.py` | Site map / zone overview |
| `Inspect a Zone` | `pages/3_Inspect_a_Zone.py` | Drone agent investigation of Zone C |
| `See the Proof` | `pages/4_See_the_Proof.py` | Evaluation dashboard |
| `Find the Gaps` | `pages/5_Find_the_Gaps.py` | Honesty Report / knowledge gap map |
| `Connect the Dots` | `pages/6_Connect_the_Dots.py` | Memory graph and end summary |

Shared UI and content helpers belong under `src/ui/`, not under `pages/`.

---

## Files To Update Or Create

| File | Change |
|---|---|
| `Home.py` | Turn landing page into cinematic opening with one primary CTA |
| `src/ui/shared.py` | Add walkthrough progress, banner, next-step, and state-clearing helpers |
| `pages/1_Ask_the_Agent.py` | Add Step 1 onboarding, numbered presets, and route-specific aha callouts |
| `pages/2_View_the_Site.py` | Create or restore site map / Zone C overview page |
| `pages/3_Inspect_a_Zone.py` | Create or rename current Drone Agent page and add Zone C arrival callout |
| `pages/4_See_the_Proof.py` | Create or rename current eval dashboard page |
| `pages/5_Find_the_Gaps.py` | Create or restore Honesty Report / knowledge gap page |
| `pages/6_Connect_the_Dots.py` | Create or restore memory graph page |
| `README.md` | Link to this plan so the onboarding direction is discoverable |

---

## Shared Walkthrough Components

Add these to `src/ui/shared.py`.

### `render_walkthrough_progress(current_step: int)`

Render the lower sidebar progress tracker exactly like the target structure:

```text
-- WALKTHROUGH --------
-> 1. Ask the Agent
   2. View the Site
   3. Inspect a Zone
   4. See the Proof
   5. Find the Gaps
   6. Connect the Dots
```

Past steps should be muted with a checkmark. The current step should be bold and visually accented. Future steps should be gray.

### `render_walkthrough_banner(step, persona_line, plain_english)`

Render a top-of-page card with:

- Step pill, such as `Step 2 of 6`
- Persona line, such as `You're looking at your site.`
- Collapsible `What you're seeing` section in simple language

Persist collapsed state with `st.session_state[f"banner_collapsed_{step}"]`.

### `render_next_step(next_page, next_label, bridge="")`

Render a bottom CTA with an optional bridge sentence. The bridge is important because it makes transitions feel authored instead of mechanical.

### `clear_walkthrough_state()`

Clear all `walkthrough_*` keys from `st.session_state`. Use this when the user clicks `Start over`.

---

## Home

File: `Home.py`

Goal: make the user feel the field-technician problem before they see any dashboard.

Structure:

```text
Act 1: Field technician scenario
"It's 2pm. You're on your fourth job today."
"A rooftop unit you've never seen. A model you don't recognize."
"The manual is 400 pages in your truck."
"A wrong safety answer is worse than no answer."

"We built an AI that knows what it doesn't know."

Act 2: Three routing pills
[HIGH - Answer]  [PARTIAL - Conflict]  [LOW - Silence]

Act 3: Single CTA
"Begin Walkthrough" -> pages/1_Ask_the_Agent.py
```

Use a subtle staggered fade-in if Streamlit CSS supports it cleanly. Do not overdo animation.

---

## Step 1: Ask The Agent

File: `pages/1_Ask_the_Agent.py`

Goal: teach the three confidence-routing paths.

Add:

- `render_walkthrough_progress(1)`
- Banner: `You've been dispatched to a unit you've never serviced. Ask the system.`
- Numbered preset buttons: `1. HIGH`, `2. PARTIAL`, `3. LOW`
- Callout above presets: `Try these three queries in order. Each one shows a different routing path.`

Add route-specific aha callouts after results render:

**HIGH**

> Confident answer, cited source. The system found strong documentation and called the LLM.

**PARTIAL**

> Two sources disagreed. The 2017 and 2023 Carrier manuals say different things. The system surfaced both instead of picking one. Most RAG systems would return one answer with no warning.

**LOW**

> The LLM was not called. A standard AI would have generated a confident-sounding answer, likely wrong. This system chose silence instead.

Small contrast line under LOW:

> What a standard LLM would do: generate an answer with no source. What this system did: escalate.

Bridge CTA:

> That was one unit on one rooftop. Here's what your whole site looks like.

Link to `pages/2_View_the_Site.py`.

---

## Step 2: View The Site

File: `pages/2_View_the_Site.py`

Goal: zoom out from one unit to the full site.

Add:

- `render_walkthrough_progress(2)`
- Banner: `Every zone is color-coded by the worst anomaly found there. Zone C is flagged HIGH.`
- Site map or zone overview
- Zone C detail card
- CTA: `Investigate Zone C`

When the user clicks `Investigate Zone C`, set:

```python
st.session_state["walkthrough_zone"] = "Zone-C"
st.session_state["walkthrough_zone_query"] = "What anomalies were found in Zone-C during the last inspection?"
st.session_state["walkthrough_arrived_from_zone"] = True
```

Then navigate to `pages/3_Inspect_a_Zone.py`.

---

## Step 3: Inspect A Zone

File: `pages/3_Inspect_a_Zone.py`

Goal: make the site map to Drone Agent handoff visible.

Add:

- `render_walkthrough_progress(3)`
- Banner: `The system searches inspection records, baselines, and compliance docs, then decides if it is confident enough to answer.`
- Drone Agent query UI

When `walkthrough_zone_query` exists:

- Prefill the Drone Agent input with that query.
- Show arrival callout:

> The map already knew where you were headed. Your query was pre-loaded from the zone you selected.

After rendering the arrival callout, clear only the one-time `walkthrough_arrived_from_zone` flag. Keep `walkthrough_zone` so the Honesty Report can highlight Zone C later.

Bottom CTA:

> Next: The proof

Link to `pages/4_See_the_Proof.py`.

---

## Step 4: See The Proof

File: `pages/4_See_the_Proof.py`

Goal: prove the system works and direct the user to the most interesting evidence.

Add:

- `render_walkthrough_progress(4)`
- Banner: `85 test cases across three scenarios: ground truth, adversarial, and contradictions.`
- Evaluation dashboard
- Suggested filter callout:

> Start here: filter to Adversarial -> Failed. These are the near-misses, queries the system correctly refused instead of hallucinating.

Graceful no-CSV behavior:

If `eval_results.csv` is missing, render an informational card instead of stopping the walkthrough:

> Eval results have not been generated yet. In a live deployment, run `python eval/run_eval.py` to populate this view. This dashboard normally shows routing accuracy across ground-truth, adversarial, and contradiction test cases.

Bottom CTA:

> Next: The honesty report

Link to `pages/5_Find_the_Gaps.py`.

---

## Step 5: Find The Gaps

File: `pages/5_Find_the_Gaps.py`

Goal: reframe the Knowledge Gap Map as a safety feature.

Page title:

> The Honesty Report

Lead copy:

> These are the questions the system refused to answer rather than guess. Every red cell is a hallucination that did not happen.

Axis labels:

- Rows: `Inspection Zone (where the drone flew)`
- Columns: `Problem Type`

Zone C continuity:

- If `st.session_state["walkthrough_zone"] == "Zone-C"`, highlight the Zone C row.
- Add annotation: `You just asked about Zone C.`

Clickable red cells:

```text
No records for [problem type] in [zone].
A query here would return:
LOW - Escalate to supervisor.
The system does not have sufficient documentation to answer this safely.
```

Banner:

> You're seeing where the system chose silence over a guess.

Bottom CTA:

> Next: How memory connects it

Link to `pages/6_Connect_the_Dots.py`.

---

## Step 6: Connect The Dots

File: `pages/6_Connect_the_Dots.py`

Goal: explain the architecture through one concrete graph story.

Add:

- `render_walkthrough_progress(6)`
- Banner: `Four memory types answer WHY something failed, WHEN it changed, WHO is responsible, and WHAT is affected.`
- Memory graph
- Concrete callout:

> The Zone C corrosion anomaly from August triggered a follow-up in Zone B three weeks later. That is a causal edge. Click it.

End summary card:

```text
You've seen the full system.

6 steps · 3 routing paths
85 test cases · <2% hallucination rate
2 domains · 0 guesses on LOW queries

Built by Nishchay Vishwanath
Site Intelligence Agent · GitHub

[Start over]
```

`Start over` must call `clear_walkthrough_state()` before navigating back to `Home.py`.

---

## Verification Checklist

1. Sidebar top navigation shows exactly: Home, Ask the Agent, View the Site, Inspect a Zone, See the Proof, Find the Gaps, Connect the Dots.
2. Sidebar lower walkthrough tracker shows steps 1-6 with the current page highlighted.
3. `Home.py` shows the scenario, routing pills, and one clear CTA.
4. Ask page shows numbered presets and route-specific aha callouts for HIGH, PARTIAL, and LOW.
5. PARTIAL callout explicitly explains the 2017 vs 2023 conflict behavior.
6. LOW callout explicitly states that the LLM was not called.
7. View the Site sets `walkthrough_zone`, `walkthrough_zone_query`, and `walkthrough_arrived_from_zone` when Zone C is selected.
8. Inspect a Zone preloads the Zone C query and shows the arrival callout.
9. See the Proof shows the suggested Adversarial -> Failed filter callout.
10. See the Proof does not break if `eval_results.csv` is missing.
11. Find the Gaps highlights Zone C and shows LOW escalation previews for red cells.
12. Connect the Dots shows the causal-edge callout and end summary card.
13. `Start over` clears walkthrough state before returning to `Home.py`.

---

## Implementation Notes

- Preserve the original seven-item sidebar navigation.
- Keep copy plain and concrete. Avoid architecture terms unless immediately grounded in user-facing behavior.
- Make every transition answer: `Why am I here now?`
- Treat LOW and red gap cells as positive product moments. They prove the system refuses to hallucinate.
- Validate CSS animations and heatmap click behavior in Streamlit before considering the walkthrough complete.
