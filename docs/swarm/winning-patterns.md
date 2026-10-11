# WINNING PATTERNS SCOUT — Report to Coordinator

**Method:** Opened actual pages (not snippets alone): Devpost's own judge-advice and judging-criteria posts, sponsor winner recaps (CockroachDB×AWS, Microsoft Azure AI), a university write-up of an NVIDIA Nemotron winner (UCSC), a PR Newswire recap of the NVIDIA Nemotron Hackathon grand prize, and — most valuable — a *loser's* published post-mortem from the CockroachDB hackathon explaining why the winner beat him. Lesson appended to the Lyceum.

---

## The 6 winning projects I actually opened

**1. Loomin — 1st place, NVIDIA GTC 2026 Agents for Impact Hackathon (~300 participants, Nemotron-powered)**
https://news.ucsc.edu/2026/04/engineering-student-wins-nvidia-agents-for-impact-hackathon/
- **One narrow job:** type a physics concept → get structured notes, real equations, and an *interactive 3D model you can break*. When the simulation breaks, it explains why.
- Why it won: the problem came from talking to real users at the event (students don't lack information, they lack *intuition*); the demo moment is visceral and visible (break the machine, watch it explain itself); a hard performance number is stated — results in under 3 seconds; Nemotron Ultra + RAG over a local knowledge base is the engine, not a garnish.

**2. Anchor — 1st place, CockroachDB × AWS Agentic Memory Hackathon (3,700 registered, 600+ submitted, 444+ entries per the loser)**
**3. Unsay — 2nd place, same hackathon**
**4. Interlock — 3rd place, same hackathon**
https://www.cockroachlabs.com/blog/winners-cockroachdb-aws-hackathon-agentic-memory/
- **Anchor:** on-call agent that diagnoses *and fixes* DB incidents, and gets measurably faster the 3rd time the same incident recurs — because its memory and its remediation actions commit in the *same transaction*. The sponsor tech is the mechanism of the product.
- **Unsay:** medication-safety agent on live FDA data with one unforgettable twist: when a recall invalidates an earlier answer, it finds everyone it told and drafts corrections. A single, nameable, non-obvious behavior.
- **Interlock:** referee for multiple AI coding agents colliding on one codebase — fixes only what the conflict actually broke, opens the result for human review. Named a failure mode "every team running agents at scale is about to hit."
- Common thread: all three are **one workflow, one user, one dramatic moment** — and all three *act* (fix, retract, repair), they don't just chat.

**5. Trashé — 1st place, Microsoft Azure AI Hackathon on Devpost (900+ participants)**
https://azure.microsoft.com/en-us/blog/microsoft-azure-ai-hackathon-s-winning-projects/
- SmartBin that detects plastic/glass/metal recyclables in real time. The judge quoted in the recap praises, in order: watching the **full end-to-end demo in a real-world environment** (not just "the intelligence"), a well-researched architecture connecting hardware → intelligence → presentation, strong performance from *very little training data*, setup instructions so others can build their own, and a community/scalability story. One bin, one decision, filmed working.

**6. Nota AI — Grand Prize + Track 1st, NVIDIA Nemotron Hackathon (Korea)**
https://pr.norwoodtownnews.com/article/Nota-AI-Wins-Grand-Prize-at-NVIDIA-Nemotron-Hackathon-Proving-MoE-Quantization-Prowess-with-Synthetic-Data-Technology/69eb5c1b25e04a842cd69652
- Won by *inverting the expected approach*: everyone else optimized quantization algorithms; Nota used a Nemotron 3 Super agent to engineer the synthetic *dataset* for MoE quantization. Data-centric beat algorithm-centric — the "Quality of the Idea" criterion rewards the approach judges haven't seen, executed against a measurable outcome (performance loss minimized).

*Search-level only (not page-opened, flagged as weaker evidence):* AITX Austin Nemotron winners 8kEdu (YouTube lectures → continuously evolving interactive lessons) and MasteryWrite (essay grader that explains its reasoning and improves its own graders) repeat the same shape — one input type, one transformation, a self-improvement loop you can watch.

## The control case: why a good project LOST
Throughline post-mortem (same idea space as Anchor, didn't place): https://dev.to/voyagi/agent-memory-that-tells-you-when-it-couldnt-check-2aao
The builder's own diagnosis:
1. His memory layer was independent of the sponsor DB — right call for a library, wrong for a contest asking what the sponsor tech *does for you*. Anchor made the DB the mechanism; he made it storage.
2. He **never deployed the public demo URL the rules required**.
3. He offered a *test count* where winners offered **measured comparisons against a baseline**.

## Patterns — what winners do that runners-up don't

1. **Narrow beats broad, every time.** Every winner above does exactly one job for one named user (physics student, on-call engineer, beekeeper-class specificity). None is a platform, dashboard-suite, or "AI assistant for X and Y and Z." Breadth reads as unfinished; a single workflow executed end-to-end reads as a product.
2. **The sponsor tech is the mechanism, not an ingredient.** Anchor's transaction = the product. Loomin's Nemotron Ultra generation = the product. For Nebius: the Token Factory runtime call must be *load-bearing and visible* — e.g., the product fails without Nemotron's reasoning/tool-calling, and the video shows the call happening. "Powered by" in the README scores nothing.
3. **A before/after or baseline number, not feature lists.** Loomin: under 3 seconds. Anchor: 3rd incident resolved faster than the 1st. Trashé: accurate model from very little training data. Winners quantify the delta; losers count features/tests.
4. **Real problem provenance.** Loomin's problem was found by interviewing users; Trashé and Anchor target pains the builders could describe concretely. Devpost's judge panel is explicit on this failure mode (see below): a pre-existing idea shoehorned to fit the contest, or the same project relabeled across hackathons, is a red flag.
5. **The demo shows a real thing changing in the real interface.** Physical bin sorting, a 3D model breaking, an incident getting fixed, an answer getting retracted. Judges reward watching an outcome happen, not slides about an outcome.
6. **A twist you can say in one sentence.** "It takes back answers the FDA invalidated." "Break the simulation and it teaches you why." If the differentiator can't be spoken in one breath, judges deliberating later won't remember it — and Devpost's own guidance stresses the video/description are what judges use in deliberation after the demo is over.

## What Devpost's own judges say (opened, first-party)
https://info.devpost.com/blog/hackathon-judging-tips and https://info.devpost.com/blog/understanding-hackathon-submission-and-judging-criteria
- Judges **watch the video first** and use it as context for testing; video + text description must complement each other — a slick video with a thin description (or light GitHub code behind a slick homepage) actively hurts.
- The top score-killer is **over-indexing on one criterion** (e.g., all backend, no UI) at the expense of the rest. Nebius scores 4 criteria equally — a submission built to touch all four visibly beats a deep-but-lopsided one.
- Many submissions fail **basic requirements** — judges check those first; missing items are an instant screen-out before quality is ever weighed.
- Submissions that depart furthest from any starter template stand out; reskinned templates and rehashed ideas are named negatives. Voiceover walking through components/code in the video was specifically praised for technical projects.

## Checklist — a winning Nebius submission must…

**In the first 60 seconds of the ≤3-minute video:**
- [ ] 0–10s: Name one real person with one real pain ("A board secretary in San José spends 6 hours…") — no logo intro, no "introducing our revolutionary platform"
- [ ] 10–30s: Show the *before* — the painful manual process, the old way, on screen
- [ ] 30–60s: Show the product doing the whole job **live in its real UI**, ending in a visible changed state (a fix applied, a document produced, a decision made) — with the Nemotron/Token Factory call visibly in the loop
- [ ] By 60s the judge can say the one-sentence twist back to you

**In the rest of the video / submission:**
- [ ] State one measured number vs. a baseline (time saved, accuracy, cost, incidents resolved faster on repeat) — measured, not promised
- [ ] Show the Token Factory architecture in one diagram: which Nemotron model does what, and Tavily's live call happening if claiming the $3k Tavily prize
- [ ] Working demo URL deployed and public — non-negotiable; its absence alone sank a finalist-caliber entry
- [ ] Balance all 4 Nebius criteria visibly: tech depth (model routing/pipeline) + finished-product design (real UI, not a notebook) + impact (named audience, named pain, one number) + idea quality (the one-sentence non-obvious angle)
- [ ] Devpost text mirrors the video beat-for-beat, with "how we built it" detail and honest challenges — judges distrust anything the text claims that the video/code doesn't show
- [ ] Built *for this* hackathon's prompt — nothing that looks relabeled from a prior entry on Jose Luis's profile

**Scope rule distilled from all six winners:** one user, one workflow, one dramatic visible outcome, one number. If a candidate concept needs a second "and also it…" sentence, it's the runner-up shape — cut it before building.