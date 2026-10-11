FROM: Red Team / Evaluator front — Nebius use-case swarm
VERDICT UP FRONT: BoardBrief **as pitched does not win a prize.** It survives Stage 1, lands mid-pack in Stage 2 (~5.5/10 average), and dies on one sentence every judge will think: *"ChatGPT does this."* It is salvageable — but only if it stops being a summarizer and becomes a **verification machine**. Details below.

---

## 1. Scoring rubric — what top marks actually require, per criterion

### A. Technological Implementation
**Top marks (9–10):**
- Video shows the pipeline *live and unedited* for at least one full run: upload → processing → output, with the model routing visible (which Nemotron tier handled what, and *why*).
- README names exact model IDs, shows the routing/fallback logic, and includes a **measured table**: latency and token cost per document for Nano vs. Super vs. Ultra, on Token Factory. Numbers, not adjectives.
- Multi-model use is *load-bearing*: remove one tier and the product measurably degrades (cost, speed, or quality) — and the submission shows that ablation.
- At least one hard technical thing done well: long-document handling (200+ pages in a coherent pass), structured extraction with schema validation, retrieval with page-level citations that actually resolve, tool/function calling, or an eval harness.
- Demo runs on the real stack during judging — runtime Token Factory calls, not cached outputs.

**Mediocre (4–6):**
- One model, one prompt template, chunk-and-summarize. Technically "uses Nebius" but nothing in the architecture would change if you swapped in any other API. This is where ~15,000 of 21,107 entrants will sit.
- README says "powered by Nemotron" with no model IDs, no costs, no benchmarks.
- Video shows only outputs, never the system working.

### B. Design
**Top marks:**
- Looks and behaves like a *product for a named user*, not a hackathon demo: one clear workflow, sensible defaults, output formatted the way the user actually consumes it (a 1-page brief looks like a brief, not a chat transcript).
- The first screen answers "what do I do here?" in under 5 seconds. Demo requires zero explanation from the presenter to follow.
- Edge states handled visibly: huge file, scanned/low-quality PDF, empty result, processing progress. Judges notice the one failure state you show and handle well more than ten happy-path features.

**Mediocre:**
- Streamlit/Gradio default skin, a chat box, a wall of generated text. ("Technical proof of concept" is literally the phrase the Design criterion warns against.)
- Output is a markdown blob the user would have to re-edit before using — i.e., the product creates new work.
- Video spends >30 seconds on the problem pitch before showing the product.

### C. Potential Impact
**Top marks:**
- A **named, specific audience with a number attached**: "The ~200,000 volunteer board members of US nonprofits, who get a median 180-page packet 5 days before a meeting they attend unpaid." Reachable, countable, real.
- At least one **real user who is not the builder**: a quote, a pilot, a letter, a recorded 20-second clip, "tested on the actual (sanitized) packet of [real org]." One real user outweighs any market-size slide.
- A quantified before/after: "3.5 hours of prep → 20 minutes, measured on 4 real packets."
- The problem is *expensive when it goes wrong* (missed risk, unflagged conflict, wrong figure approved) — not merely inconvenient.

**Mediocre:**
- "For everyone who reads documents." "Saves time." TAM slide with three zeros and no user. Judges have scored hundreds of these; the claim is unfalsifiable and therefore worthless.
- Impact asserted in the description but never *demonstrated* in the demo (no real document, only lorem-ipsum sample text).

### D. Quality of Idea
**Top marks:**
- The idea contains a **non-obvious insight about the problem**, not just a use case for the tech: e.g., "Board members don't need summaries — they need to know what in this packet *contradicts* the last packet, the budget, or the vendor's public claims." The technology serves the insight.
- A judge can repeat the idea in one sentence afterward and it still sounds interesting.
- There is a feature a general chatbot *structurally cannot easily replicate*: planted-error/discrepancy detection with measured catch rate, cross-document consistency checking, a verification pass where every figure in the output is machine-checked against the source page it cites.

**Mediocre:**
- A vertical wrapper on a horizontal capability: "AI summarizer *for X*," where X is the only novel word. Rebrand risk — this is also the Stage 1 "superficial rebrand" trap's neighborhood.
- Novelty claimed but never proven: no comparison, no baseline, no "here's what a plain chatbot got wrong on this same packet."

---

## 2. BoardBrief scored — harshest-judge version

| Criterion | Score | Harshest objection |
|---|---|---|
| Technological Implementation | **5/10** | "Chunk, summarize, synthesize is a tutorial architecture. Your three models are doing one model's job in three costumes." |
| Design | **6/10** | "A 1-page cited brief is genuinely good output design — the best thing about this pitch. But I've seen no UI, and 'upload PDF, get brief' demos are a dime a dozen." |
| Potential Impact | **7/10** | "Real audience, real pain, the builder has actually sat on boards — credible. But where is *one* board member who used it? So what if it's never touched a real packet?" |
| Quality of Idea | **4/10** | "**ChatGPT does this.** I pasted a board packet into a chatbot last week and got decisions, actions, and risks. What is *this*?" |
| **Average** | **~5.5/10** | Not a prize score in a 21,107-person field. |

**The three kill-shot objections, and the only evidence that answers each:**

1. **"ChatGPT does this."** → Answer must be *demonstrated, not argued*: in the video, run the same packet through BoardBrief and state plainly what the generic approach misses. Requires a **verification layer**: every money figure in the brief is machine-checked against the cited page; the system flags (a) figures that differ between the packet's summary page and its own appendix, (b) action items from last meeting that silently vanished, (c) claims contradicted by a Tavily check. Then publish the number: *"On our annotated test packet with 12 planted errors/inconsistencies, BoardBrief caught 10; a single-prompt chatbot baseline caught 3."* That one number moves Idea from 4 → 7+ and Tech from 5 → 7+. Without it, the objection is simply true.

2. **"Where's the Nebius necessity? This runs on anything."** → Answer with the two honest arguments, with receipts: (a) **Context + routing economics** — Ultra's long context handles the whole packet coherently while Nano/Super do cheap section passes; show the cost/latency table proving the routing saves real money vs. an all-Ultra or all-closed-API run, on Token Factory credits. (b) **Data sensitivity / openness** — board packets contain confidential financial, personnel, and legal material; an open-model stack the organization can audit and self-host is a *governance* argument a closed API cannot make — and it fits the hackathon's "open infrastructure" theme exactly. If the submission doesn't make argument (b) explicitly, it is leaving its best Nebius story untold.

3. **"So what? A nicer summary of a packet nobody showed me."** → Requires one real artifact and one real human before Oct 30: run it on a real, sanitized packet from a real board the builder serves on, and get one named board colleague's reaction on record. Synthetic sample packets score zero on this objection — judges can smell them.

**Upgraded verdict if all three answers land:** ~7.5/10 average — competitive for a track/bonus prize (Tavily bonus and SF City Winner especially), still probably not Grand Prize. Without them: do not expect to place.

---

## 3. Five failure modes expected across 21,107 entrants — and the visible avoidance

1. **The wrapper (Stage 1 near-fail).** A chat UI over one model with a domain label pasted on. *Avoid visibly:* the description's first paragraph names the specific workflow, the specific insight, and the specific multi-model architecture — and the video proves all three in the first 60 seconds.
2. **The dead demo.** Hosted demo asleep, expired, login-walled, or out of API credits when the judge clicks — in a field this size, judges do not retry. *Avoid visibly:* demo is public, no login, wakes in seconds, has a "load sample packet" button so a judge needs no file of their own, and credit budget is reserved for judging period (Dec 1–15), not burned in October. State "no login required" in the submission text.
3. **The pitch-deck video.** Three minutes of narration over slides; the product appears in screenshots. Judges may judge on video alone — a video with no live product is a zero wearing a costume. *Avoid visibly:* ≥80% of the video is screen capture of the real system running a real document end-to-end, with the output inspection (clicking a citation, seeing the flagged discrepancy) shown, not described.
4. **The un-runnable repo.** No license, README says "install dependencies and run," missing env vars, setup fails. Kills Tech Implementation and can fail Stage 1's "real use" sniff test. *Avoid visibly:* MIT/Apache license at top, README with exact model IDs, a `.env.example`, a one-command run, and an architecture diagram. Test the README cold on a clean machine/account before submitting.
5. **Impact theater.** "For everyone," billion-dollar TAM, zero users, zero measurements. *Avoid visibly:* one named audience, one named tester/user, one measured before/after, one real document in the demo. Small and true beats large and invented on this rubric — the criterion literally asks for "a credible, specific case."

*(Runner-up failure mode, worth naming: scope sprawl — six half-features. Every visible half-finished feature taxes the Design score. Ship two features that are flawless.)*

---

## 4. Kill bars — abandon ANY idea if, by **Oct 18**, any of these is true

Pre-registered, measurable, no extensions:

1. **Stack bar:** No end-to-end run yet in which ≥2 Nemotron tiers on Token Factory each do real work in one pipeline execution (logged calls, not mocked). *If the architecture is still single-model on Oct 18, the Tech score is capped at ~5 — kill or rebuild the architecture that week.*
2. **Baseline bar (the BoardBrief-specific one, generalize it):** In a blind A/B on the same input, 3 test readers cannot identify a concrete output advantage over a single plain prompt to a general chatbot. *Indistinguishable from the free baseline = dead idea, regardless of polish.*
3. **Accuracy bar:** On an annotated test case with known ground truth, extraction/citation accuracy <90% (for BoardBrief: figure-to-source-page correctness), or planted-error detection <50%. *Below this, the demo will embarrass itself live; judges do test the sample.*
4. **Reliability bar:** Demo fails or hangs in >1 of 20 consecutive end-to-end runs, or p95 latency makes a live video take impossible (>~3 min per core workflow with no honest progress indicator).
5. **Cost bar:** Projected cost per demo run × a realistic judging load (say 200 runs through Dec 15) exceeds the documented credit stack (~$50 Token Factory credits) with no caching/rate plan — or the build requires the AI Cloud $25 card charge / idle GPU spend the coordinator already ruled out.
6. **Rights bar:** No legally showable, realistic sample input exists (everything real is confidential and nothing sanitized/synthetic-but-realistic can be produced). *No demoable input = no video = no prize, full stop.*
7. **Scope bar:** The core workflow still depends on >3 external services or any unbuilt component rated "more than 2 days of work." After Oct 18 there are 12 days left; anything not already working gets cut, and if cutting it guts the idea, the idea dies with it.

---

## 5. What the Grand Prize winner most likely looks like — honest prediction

It will not be a summarizer, a chatbot, or a dashboard. The Grand Prize ($20k, from 21,107 participants) most likely goes to a team whose demo shows an **agent completing a real, verifiable, multi-step job end-to-end** — coding/agentic-engineering or a physical-AI entry are the structural favorites — where the audience watches work *happen* rather than text appear: tests actually run and pass, a workflow actually executes across tools, a robot actually moves, and the result is checkable by the judge in the demo itself. It will use at least two Nemotron tiers for reasons the cost/latency table makes obvious, name exact models in the README like an engineering team (because it is one — expect strong existing teams, not solo first-timers, at the very top), show one quantified result a baseline visibly fails to match, have one real user or real deployment context, and feel like a *product* — branded, opinionated, reliable — in every frame of a video that opens on the working system, not on a problem statement. BoardBrief's realistic ceiling, even fully upgraded with the verification layer, is a **track-adjacent / bonus-prize outcome (Tavily $3k and SF City $500 are its most winnable targets)** — and the swarm should aim it there deliberately rather than pretend otherwise.

---
Lesson appended to `~/workspace/lyceum/LESSONS.md` (2026-10-11: summarization is a commodity, verification is the moat — kill bar = blind A/B vs. plain chatbot prompt by Oct 18). No signups, submissions, or external actions taken.