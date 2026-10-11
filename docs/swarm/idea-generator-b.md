# Idea Generator B — 5 Use Cases: Personal AI + Coding/Agentic Engineering

All are Token Factory–only (runtime API call, key in env var — no AI Cloud, no $25 card charge), scoped for the $50 credit cap, and deliberately NOT board/governance ideas. Model routing follows one rule throughout: **Nano runs the high-frequency loops, Super drafts/generates, Ultra is spent only on the 1–2 hard reasoning steps per run.**

---

## 1. OwnMind — a personal AI whose memory is a folder you own
1. **Pitch:** Always-on private assistant where persistent memory lives in plain, human-readable files on the user's machine — Nebius/open models supply only the brain, never the filing cabinet.
2. **Track:** Personal AI
3. **Winning demo moment:** Assistant gives a morning brief built from a week of simulated activity. On camera, the user opens the memory folder, edits one fact and deletes another ("forget my dentist"), and the next brief visibly changes — then asks "what do you know about me?" and gets an answer generated *from the files shown on screen*, nothing hidden.
4. **Nemotron split:** Nano — continuous triage (classify incoming notes/reminders, decide what's worth storing). Super — brief drafting and summarization. Ultra — once-daily reasoning pass: resolve conflicting memories, plan the day, surface dropped commitments.
5. **Tavily fit:** Strong but gated — web lookup is a per-skill permission the user toggles; the demo shows a cited news/weather check firing only because the toggle is on.
6. **Build days:** 8
7. **Biggest risk:** The privacy story must be honest — prompts do leave the device for inference. Mitigation is part of the product: a local redaction layer strips names/numbers before any call, and the README states exactly what leaves and what never does. If the redaction demo fails, the pitch collapses.
8. **Anti-generic test:** Clones keep memory in a vendor's opaque vector store (or none). OwnMind's memory is inspectable, editable, deletable, and portable — skills are small user-owned files with explicit tool allowlists, and "forget" is a file deletion you can watch happen. The product is the *ownership architecture*, not the chat.

## 2. ThreadKeeper — executive-function companion for ADD/dyslexic minds
1. **Pitch:** You brain-dump messy voice notes all day; it keeps every thread, and gives you back exactly ONE next step at a time — never a wall of text.
2. **Track:** Personal AI
3. **Winning demo moment:** User dumps 12 scattered, rambling notes in 90 seconds. ThreadKeeper clusters them into 3 projects, then resurfaces one *dropped* thread — a promise made in note #3 that contradicts a date in note #10 — and presents a single card: the one next action, in a sentence under 20 words. Judges watch a dropped commitment get caught, which is the whole product.
4. **Nemotron split:** Nano — per-note extraction (commitment? date? person?) at dump time, cheap and fast. Super — clustering notes into projects and drafting the one-step cards. Ultra — the evening review: contradiction/dropped-thread detection across the full day's ledger.
5. **Tavily fit:** Weak/optional — public-fact checks only (e.g., a venue's hours mentioned in a note). Honest answer: ship without it if it dilutes the demo; it's the one idea here that doesn't need the Tavily bonus to win its track.
6. **Build days:** 7
7. **Biggest risk:** Looking like a to-do app. The defense is the demo metric: a scored "dropped-thread catch" on the planted test data, plus enforced output rules (one card, short sentences, dyslexia-friendly formatting) that are visible in every frame of the video.
8. **Anti-generic test:** A chatbot answers what you ask. ThreadKeeper maintains a **commitment ledger with provenance** — every surfaced item cites the exact note it came from — and proactively interrupts with what you *didn't* ask about because you forgot it. The entrant's lived ADD/dyslexia experience is the credential moat: pacing and formatting are designed constraints, not a theme.

## 3. FocusPair — a coding agent built for neurodivergent developers
1. **Pitch:** A coding agent that writes, runs, and tests code in tiny verified steps — plain-language chunked diffs, a checkpoint after every step, and perfect resume after an interruption.
2. **Track:** Coding and Agentic Engineering
3. **Winning demo moment:** Agent fixes a real planted bug in a sample Python repo: 3-step plan on screen → one small change → tests run live → diff shown in two plain-language chunks (no 500-line wall). Mid-task, the session is "interrupted" — one click later a resume card appears: *"You were here. Step 2 passed. Step 3 is next."* That resume shot is the moment no other coding agent demos.
4. **Nemotron split:** Ultra — code reasoning, patch generation, repair after test failures. Super — plain-language explanation of each diff (enforced short-sentence style). Nano — cheap loop work: classifying test failures and log noise between steps.
5. **Tavily fit:** Good — when a test failure traces to a library, the agent pulls current docs/changelog via Tavily and cites them in the fix rationale, instead of hallucinating an API from training data.
6. **Build days:** 7 (CLI + thin web UI, Python repos only, sandboxed test execution)
7. **Biggest risk:** Agent reliability on arbitrary code. Scope is the defense: Python + pytest, small repos, a curated demo bug — and the checkpoint system means a failed step degrades to "resume here," not a dead demo.
8. **Anti-generic test:** ChatGPT clones *talk* about code in huge dumps. FocusPair actually executes in a sandbox, is paced by a step state-machine (plan → change → test → explain → checkpoint), and treats interruption-resume and reading load as first-class engineering requirements. The accessibility layer is measurable: diff chunk size, sentence-length cap, and resume fidelity can all be shown as numbers in the README.

## 4. TenantJanitor — an M365/SharePoint admin agent that proves its fixes in a sandbox first
1. **Pitch:** Point it at a SharePoint tenant; it finds broken permissions, stale sites, and oversharing, writes the remediation scripts, and dry-runs them against a simulated tenant before a human approves anything.
2. **Track:** Coding and Agentic Engineering
3. **Winning demo moment:** A seeded mock tenant with 5 planted problems (an externally-shared confidential site, a dead owner, broken inheritance, etc.). The agent audits, generates PowerShell/PnP scripts, executes them in the sandbox, and the screen shows a **before/after state diff**: 5 problems → 0, with an approval gate and audit log for every change. Nothing touches a real tenant.
4. **Nemotron split:** Nano — classify thousands of site/permission inventory rows cheaply (this is where the credit budget is won). Ultra — remediation planning: which findings are real risks, in what order, with what blast radius. Super — script generation and the human-readable change report.
5. **Tavily fit:** Strong — Microsoft cmdlets and Graph APIs drift constantly; the agent grounds every generated script in current Microsoft documentation fetched via Tavily, with doc citations attached to each script. Stale-training-data scripts are a real admin pain point, so this reads as expertise, not decoration.
6. **Build days:** 9 (the heaviest build of the five — the simulated tenant/state-diff engine is the work)
7. **Biggest risk:** Build time and demo credibility — if the mock tenant looks toy-like, judges discount it. Mitigation: seed it from realistic anonymized inventory shapes (the entrant is a working M365/SharePoint admin — that credibility is the pitch), and cut findings to 5 well-staged ones.
8. **Anti-generic test:** A wrapper gives advice ("you should fix permissions"). TenantJanitor has a deterministic audit rules engine, *executes* its own generated scripts, and proves the result as a state diff — with human approval gates and an audit log, i.e., built the way a real admin (and a union shop: backs up workers, never silently replaces their judgment) would require. Execution + proof + gating is the moat.

## 5. TestRescue — legacy-code agent whose tests are proven by mutation testing
1. **Pitch:** Give it an untested Python module; it writes characterization tests, then *tries to break its own tests* with mutated code — only tests that catch real bugs survive, and the survivors expose the bugs already hiding in your code.
2. **Track:** Coding and Agentic Engineering
3. **Winning demo moment:** An innocent-looking date-handling function. TestRescue generates tests, runs a mutation pass — on-screen kill count climbing — and one surviving mutant reveals a real latent bug (leap-year edge case). The agent patches it, full suite + mutation pass go green. End card: "Tests generated: 24. Mutants killed: 31/33. Bugs found in original code: 1." Numbers, not adjectives.
4. **Nemotron split:** Ultra — edge-case reasoning and mutant design (where would this code silently lie?). Super — test code generation and patch writing. Nano — triage inside the loop: classifying failures, summarizing coverage gaps across many iterations.
5. **Tavily fit:** Moderate — library docs and breaking-change changelogs when the legacy code touches third-party APIs; useful, cited, but not the core story.
6. **Build days:** 6 (tightest scope of the five: Python + pytest, simple hand-rolled mutations — no external mutation framework needed)
7. **Biggest risk:** Crowded dev-tools field. The mutation-verification angle is the entire defense — if the demo leads with "AI writes tests," it dies as a clone; if it leads with the kill count and the caught bug, it's a different product.
8. **Anti-generic test:** Every clone generates plausible-looking tests and never checks whether they catch anything — most generated tests are assertion-free theater. TestRescue closes the loop with execution and adversarial self-verification: a test that kills no mutants is deleted and reported as deleted. That honesty mechanism is demonstrable, measurable, and absent from the 1,000 wrappers.

---

## Generator B ranking (my judgment, for the Synthesizer)

| # | Idea | Track | Days | Why |
|---|------|-------|------|-----|
| 3 | **FocusPair** | Coding/Agentic | 7 | Best fusion of credible lived angle + executable demo + resume moment nobody else will show |
| 5 | **TestRescue** | Coding/Agentic | 6 | Fastest build, hardest numbers, most falsifiable claim — safest strong entry |
| 1 | **OwnMind** | Personal AI | 8 | Cleanest "own your AI on open infrastructure" fit to the Nebius/NVIDIA theme |
| 2 | **ThreadKeeper** | Personal AI | 7 | Strongest human story; risk is category perception (to-do app) |
| 4 | **TenantJanitor** | Coding/Agentic | 9 | Highest expertise moat, highest build risk — needs the full 9 days protected |

**Shared kill bar (pre-registered):** for whichever idea is chosen, if by mid-build the demo moment reduces to "good text appears on screen" with no state artifact changing (memory file, state diff, kill count, checkpoint resume), kill and switch — per the Lyceum lesson appended this run.

**Lesson appended** to `~/workspace/lyceum/LESSONS.md`: "Nebius idea generation B: the demo must show a state artifact changing, not text appearing" — anti-generic test at pitch time + model routing by loop frequency under a hard credit cap.

**Scope compliance:** Research/ideation only. No signups, no submissions, no external messages.