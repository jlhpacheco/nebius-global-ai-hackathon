# TRACK STRATEGIST REPORT — Nebius x NVIDIA Global AI Hackathon

**FROM:** Track Strategist scout
**VERDICT IN ONE LINE:** Primary = **Best Apps and Agents**. Fallback = **Personal AI**. Coding is a talent trap; Physical AI is dead on arrival for this entrant.

---

## 1. How the crowd will distribute (estimates — directional, not page facts)

With 21,107 participants, assume the generic-wrapper crowd sorts roughly like this:

| Track | Expected crowding | Per-entry strength | Why |
|---|---|---|---|
| Best Apps and Agents | **Largest** plurality | Low–medium median | Catch-all; lowest perceived barrier; every productivity copilot, RAG chatbot, resume/travel/study app lands here |
| Personal AI | Second largest | Low median, spiky top | Hackathon marketing pushes it hard; floods with Jarvis clones / "second brain" demos with fake memory |
| Coding & Agentic Engineering | Smaller | **Highest density of pros** | Self-selects working devs, ML engineers, devtool founders |
| Physical AI | **Smallest** | Highest per-entry | Self-selects robotics teams who already own hardware and know ROS/GROOT/Cosmos |

**Key strategic fact: smallest field ≠ best odds.** Physical's thin field is thin because the entry cost is real. Expected value = field softness × capability fit × how legible the entry is to judges in a <3-minute video (judges are not required to test anything).

## 2. Scorecard for THIS entrant (solo + AI help, Token Factory only, 19 days, his asset base)

Scored 1–5 per dimension:

| Dimension | Coding | Best Apps | Personal AI | Physical |
|---|---|---|---|---|
| Fit to his unique assets (fiduciary/board, bilingual nonprofit, union, M365 admin, ADD/dyslexia lived experience) | 2 | **5** | 4 | 1 |
| Buildable solo in 19 days, API-only, no AI Cloud/$25 | 3 | **5** | 2 | 1 |
| Differentiation vs. the generic crowd | 2 | **4** | 3 | 2 |
| Judge legibility in <3 min video | 3 | **5** | 3 | 2 |
| Bonus stacking (Tavily + City + Feedback) | 2 | **5** | 2 | 1 |
| **Total** | **12** | **24** | **15** | **7** |

## 3. Track-by-track reasoning

### Coding and Agentic Engineering — REJECT
- **Table stakes:** an agent that writes, runs, *and tests* code in a sandbox, with self-correction loops and some benchmark or before/after evidence.
- **Distinctive:** real infrastructure depth — sandboxing, eval harnesses, multi-agent orchestration.
- This is a head-on fight against people who ship developer tools for a living, judged by engineers (NVIDIA/Nebius DevRel dominate the panel), on Technological Implementation. His advantages — domain expertise, a real named audience, bilingual community trust — score almost nothing here. A Token Factory code agent is also the single most tutorialized, commoditized build in the field.

### Personal AI — FALLBACK (real, but scope-dangerous)
- **Table stakes (higher than they look):** demonstrable persistent memory across sessions, reusable skills, tool access, and a credible privacy/user-control story — the track text names specialist tooling (NemoClaw, OpenShell, Hermes-style runtimes), so track judges will probe the memory/security architecture, not just the chat UI.
- **His genuine edge:** lived ADD + dyslexia experience. A personal AI designed around executive function — one step at a time, short dyslexia-friendly output, capture-and-nudge — is an authentic, non-obvious angle almost no Jarvis clone will have.
- **Why not primary:** (a) "Always-on" is hard to prove credibly from a demo URL without always-on infrastructure, which pushes toward the AI Cloud spend we're avoiding; (b) you cannot demo it with his real personal data, so the demo runs on synthetic life-data and the impact case thins; (c) scope — integrations, memory, skills, privacy controls — is the easiest build to be half-finished on Oct 30, and Design scoring punishes half-finished directly; (d) Tavily stacking fights the positioning — a "private, your-data-stays-yours" assistant that ships queries to an external search API undercuts its own story.

### Physical AI — REJECT, honestly
- The rules' no-hardware path (≥1 minute of module footage instead of robot footage) is a **participation accommodation, not competitive parity**. That footage minute is where hardware teams are most impressive and a software-modules clip is weakest, on the two criteria that dominate here: Technological Implementation and Design.
- Simulation/synthetic-data routes need GPU workloads (Serverless Jobs / AI Cloud) — directly against the avoid-the-$25-and-metered-GPU constraint — plus a robotics stack (GROOT/Cosmos/ROS) that would have to be learned from zero, solo, in 19 days.
- The track prize is a Jetson Orin Nano: the winners will overwhelmingly be people who already build on edge hardware. He has no robot, no IoT rig, no robotics collaborator in his asset list. **Immediate kill bar already met: no hardware in hand and no robotics partner → do not spend one build day here.**

### Best Apps and Agents — PRIMARY ✅
- **Table stakes:** one polished workflow, end-to-end, on Nemotron via Token Factory (Ultra for the hard reasoning step, Nano/Super for fast calls). Achievable solo via API only.
- **Where his moat actually pays:** this track's generalist judges can score what the other tracks can't — a *specific* problem for a *named* audience he credibly belongs to (board/fiduciary work, bilingual patient navigation, union members, M365 workplace users), in EN/ES, with human-in-the-loop and accessibility built in. Potential Impact and Quality of Idea are two of four equal criteria, and both reward domain truth over engineering spectacle.
- **Overall-prize exposure:** Grand/2nd/3rd ($36K of the cash) are cross-track. A complete, well-designed app with a real audience is the most plausible overall-prize shape; the track Jetson is then a fallback prize, not the ceiling.
- **Pivot insurance:** Best Apps is the broadest tent. If the lead use case weakens mid-build, another of his domain concepts slots into the same track without changing architecture or positioning.

## 4. Bonus stacking — all three ride on the Best Apps entry

1. **Tavily, $3K:** Pick a workflow where live external information *changes the answer* (current local resources, deadlines, eligibility rules, public facts to verify). Tavily must be load-bearing: if removing the Tavily call wouldn't break the demo, judges won't credit it. In Best Apps this is natural; in Personal AI it's contradictory (see above).
2. **SF City Winner, $500 × 20:** Set the story in a real SF/Bay Area audience and associate the submission with San Francisco (a listed city; earlier verification found in-person attendance is not required for City Winner consideration). Twenty winners makes this the highest-probability cash prize in the pool — treat it as base-case, not stretch.
3. **Most Valuable Feedback, $100 × 10:** Cheapest stackable in the pool. Write the Token Factory feedback section like a product review — specific friction, specific praise, reproducible detail — regardless of anything else.

Stacking rule check: one overall **or** track prize **plus** one bonus — so the realistic ceiling stack is e.g. 2nd Place + Tavily, or Track Winner (Jetson) + City.

## 5. Recommendation and kill bars

**PRIMARY: Best Apps and Agents.**
**FALLBACK: Personal AI** — only if the winning concept turns out to be inherently a *single-user, longitudinal* companion (its core value is memory over time, not a discrete workflow). That is a positioning/architecture fork, decided once.

**Kill bars / pivot triggers for the primary:**
1. **Architecture fork — Oct 16:** If the chosen concept's core value is persistent memory across weeks rather than one completable job, pivot positioning to Personal AI *then*. After Oct 16, the framings diverge (video story, README, demo data) and switching costs a rebuild of the narrative.
2. **Audience test — Oct 20:** If we cannot name the audience in one sentence AND get the concept in front of 3–5 real members of that audience for reaction/quotes, the Potential Impact case is fiction — narrow the concept or swap it within Best Apps before writing another feature.
3. **Integration trap — any time:** If the MVP starts requiring real email/calendar/EHR access, permissions, or GPU/AI Cloud to demo credibly, kill that scope the same day. The demo must run on sample data through Token Factory API calls only.
4. **Completeness gate — Oct 24:** If the demo is still a single prompt-in/answer-out screen instead of a complete product (entry → workflow → useful output → save/share), stop adding features and spend all remaining days on Design polish, video, and description — in this track, an unfinished "powerful" app loses to a finished narrow one.
5. **Bonus integrity — Oct 27:** If Tavily is still decorative (demo works identically without it), either rewire it into the core workflow or drop the Tavily claim from the story — a fake bonus claim risks judge trust on the main prize.

**Bottom line for the synthesis:** Best Apps and Agents, 24/25 on fit-adjusted scoring; Personal AI held as a single pre-declared pivot with an Oct 16 decision gate; Coding and Physical closed, with reasons on the board.

Lesson appended to `~/workspace/lyceum/LESSONS.md` (hackathon track selection: smallest field ≠ best odds; price fit × judge-legibility, with a pre-declared pivot checkpoint).