# Use Cases — Shortlist and Synthesis

Source reports (full text): `docs/swarm/idea-generator-a.md`, `docs/swarm/idea-generator-b.md`,
`docs/swarm/track-strategist.md`, `docs/swarm/red-team.md`, `docs/swarm/winning-patterns.md`,
`docs/swarm/architect.md`.

## Track verdict (Track Strategist)

- **Primary track: Best Apps and Agents.** Fallback: Personal AI.
- Coding and Agentic Engineering is a "talent trap" for this entrant; Physical AI is not viable for this entrant (no hardware path worth the risk).

## Idea Generator A — "his-world" ideas (ranked by its author)

1. **Podrá Navega** — bilingual (Spanish-first) cancer-navigation copilot for Latinas Contra Cancer. A patient asks in Spanish; the AI drafts a plain-language explanation, a question list for the doctor, and flags barriers (e.g., transport). **A human navigator reviews, edits, and approves before anything is sent** — the human-in-the-loop is shown on screen, not just claimed. Best impact + best Tavily story + the entrant chairs LCC. Highest ceiling; highest safety-engineering burden.
2. **Fiduciary Red Flag** — pay-and-cyber pre-check for board/committee members. Highest credential moat (former CalPERS board, comp committee chair); harder build, data-accuracy risk.
3. **ClearRead** — dense documents rewritten for the brain you actually have (ADD/dyslexia-first reading). Fastest, safest build; authenticity carries it; commoditization is the fight.
4. **Steward's Second Chair** — grievance prep that backs up union workers, never replaces them. Most distinctive values story; narrower judge resonance.
5. **SharePoint Steward** — stale-document audit for M365/SharePoint that never deletes anything itself. Best Coding-track hedge.

## Idea Generator B — Personal AI + Coding ideas (ranked by its author)

1. **FocusPair** — a coding agent built for neurodivergent developers (Coding track, ~7 days). Best fusion of lived angle + executable demo.
2. **TestRescue** — legacy-code agent whose tests are proven by mutation testing (Coding track, ~6 days). Fastest build, hardest numbers, most falsifiable claim.
3. **OwnMind** — a personal AI whose memory is a folder you own (Personal AI track, ~8 days). Cleanest "own your AI on open infrastructure" fit to the hackathon theme.
4. **ThreadKeeper** — executive-function companion for ADD/dyslexic minds (Personal AI, ~7 days). Strongest human story; risk is being read as a to-do app.
5. **TenantJanitor** — M365/SharePoint admin agent that proves its fixes in a sandbox first (Coding, ~9 days). Highest expertise moat, highest build risk.

## Baseline idea — BoardBrief (coordinator's original proposal)

Upload a board packet PDF → one-page cited brief (decisions, actions, money, risks).

**Red Team verdict: as pitched, it does not win.** It passes Stage 1 but scores ~5.5/10 in Stage 2 and dies on the judge's thought: "ChatGPT does this."
Salvage path: it must stop being a summarizer and become a **verification machine** (cross-checking the packet's claims against outside sources — where Tavily is functional, not decorative). With all three red-team fixes landed, it rises to ~7.5/10 — competitive for a track/bonus prize, probably not Grand Prize.

## Coordinator synthesis — recommendation

**Build Podrá Navega (Best Apps and Agents track).**

Reasons:

1. It is the only top idea where the entrant's credibility is the moat: he chairs the organization it serves. No other entrant can copy that.
2. Human-in-the-loop is a *visible state change* in the demo (draft → navigator edit → approve → send), which passes the swarm's anti-generic test: the demo shows an approval artifact changing, not just good text appearing.
3. Tavily is functional here (verifying resources, clinics, transport options), which keeps the $3,000 Tavily bonus honestly in play, plus the SF City Winner path.
4. Impact is specific and real: Spanish-speaking cancer patients who do not understand their next steps — a named audience, a named problem, a demonstrated fix.
5. It reuses a design the entrant already settled for Podrá (human-in-the-loop, escalation of sensitive cases), so the build starts from a real plan, not a blank page.

Tradeoff (stated honestly): Podrá carries the highest safety-engineering burden of the five. The demo must use only sample/fictional patient scenarios, no real patient data, and the escalation path must be visibly built in — not bolted on.

Runner-up if Podrá is killed by Oct 18: **ClearRead** (fastest safe build) or the salvaged **BoardBrief-as-verifier**.

## Decision needed

Entrant picks the use case (coordinator recommends Podrá Navega). Build starts on the pick.
