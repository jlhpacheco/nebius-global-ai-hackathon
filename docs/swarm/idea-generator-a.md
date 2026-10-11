# IDEA GENERATOR A — 5 His-World Use Cases for Nebius x NVIDIA

Baseline excluded: BoardBrief. All five below are buildable Token Factory–only (no AI Cloud), fit in the $50 credits if Nano/Super do the volume work and Ultra is rationed to 1–2 calls per workflow.

---

## 1. Podrá Navega — bilingual cancer-navigation copilot, human always in the loop

1. **Pitch:** A Spanish-first WhatsApp-style chat that helps a cancer patient prepare for appointments and understand next steps — every draft reviewed and sent by a human navigator, never the AI alone.
2. **Track fit:** Best Apps and Agents (strongest track fit of the five; Personal AI is a fallback).
3. **Winning demo moment (<3 min):** Patient types in Spanish: *"Me dijeron que necesito una biopsia y no entiendo, y no tengo transporte."* On screen: Nano drafts a plain-language explanation + a question list for the doctor; the view **splits** — a "navigator approval" panel appears, navigator edits one line, taps Approve; only then does the reply send, with a flagged escalation note: "transport barrier — refer to social work." The human-in-the-loop is *shown*, not claimed.
4. **Only Jose Luis:** He chairs Latinas Contra Cancer, is bilingual, and Podrá is his own planned project with a settled design (human-in-the-loop, navigator reviews everything). No generic team can pitch a cancer-nonprofit chair demoing his own org's workflow.
5. **Model split:** Nano/Super — intake, translation, plain-language drafts, question lists (high volume, cheap). Ultra — one call per case: cross-check the full case history for missed barriers (transport, cost, language, fear) and draft the escalation summary for the navigator.
6. **Tavily:** Natural fit — live lookup of clinic hours, support-group listings, and transport resources so referrals are current, not hallucinated. This is also the only idea here where Tavily use is load-bearing enough to plausibly contend for the Tavily bonus.
7. **Build scope:** 8–10 days. WhatsApp itself is the risk — demo in a WhatsApp-*style* web UI, not the real WhatsApp API. Pre-scripted patient persona, fixed resource set + live Tavily on top.
8. **Biggest risk:** Health-safety. One medical-advice slip in the demo kills credibility. Hard guardrails required: information/preparation only, no diagnosis/treatment content, every sensitive case visibly escalates to the human. Also flag: Podrá exists as a *plan* — the submission must frame the Nemotron build as the significant work of the period, in writing.

## 2. Steward's Second Chair — grievance prep that backs up workers, never replaces them

1. **Pitch:** A shop steward pastes messy case notes and the relevant contract articles; the tool returns a clean timeline, the contract clauses that may apply, and a *draft* grievance for the steward to edit — it files nothing, decides nothing.
2. **Track fit:** Best Apps and Agents; secondary Coding and Agentic Engineering (document-to-structured-case pipeline).
3. **Winning demo moment:** Steward drops in a rambling voice-note transcript about a denied overtime rotation. In ~20 seconds: a dated timeline appears, two contract articles are cited with quoted text from the uploaded contract, a missing fact is flagged ("no date for the supervisor's denial — ask this"), and a first-draft grievance letter sits in an edit box with the steward's cursor in it. End card: "Draft. A human files this, or nobody does."
4. **Only Jose Luis:** Union leader (CSEA 363), and this product *embodies* his stated standing principle — "AI backs up union workers, never replaces them." Judges hear plenty of "automate the worker away" pitches; this is the principled opposite, from an actual labor leader.
5. **Model split:** Nano/Super — extract dates/events/entities from notes, classify note chunks against contract sections. Ultra — one reasoning pass: map facts → candidate contract violations, spot the gaps/contradictions in the timeline, draft the grievance in formal register.
6. **Tavily:** Weak/optional — honest answer: mostly unnecessary. Could check current public labor-board filing deadlines/guidance, but forcing it looks bolted-on. Skip Tavily here; don't chase that bonus with this idea.
7. **Build scope:** 6–8 days. Inputs are paste/upload of text + a sample contract (public/sample CBA). No real case data — demo on a fictional case, stated on screen.
8. **Biggest risk:** It reads as legal advice if framed wrong. Mitigation is the framing itself: prep tool for trained stewards, drafts only, "not a lawyer" line in-product. Secondary risk: a judge with no labor context underrates impact — the demo's emotional clarity (a real steward's Friday-night workload) has to carry it.

## 3. ClearRead — dense documents, rewritten for the brain you actually have

1. **Pitch:** Paste a benefits letter, syllabus, or workplace memo; get it back in short plain-language chunks — one idea per card, key dates pulled out, audio-ready — at the reading level and pace *you* set.
2. **Track fit:** Personal AI (user-controlled, persistent preferences/memory of reading settings) — this is the best Personal AI fit of the five.
3. **Winning demo moment:** A real-style 3-page HR benefits letter goes in, impenetrable. Out come 6 cards: what changed, what it costs you, the one deadline (Oct 28) in large type, and a "read it to me" button. Then the kicker: user toggles "Spanish" and "simpler" — same letter, re-rendered instantly, meaning intact, citations back to the original paragraph on every card so nothing is trusted blindly.
4. **Only Jose Luis:** He has severe ADD and dyslexia and says so. This is lived-experience product design — chunking, sentence caps, no walls of text — not an accessibility feature bolted onto a chatbot. That authenticity is un-copyable in this field.
5. **Model split:** Nano/Super — per-paragraph simplification, date/obligation extraction, translation (fast, parallel, per-chunk). Ultra — one fidelity pass: verify the simplified version didn't drop or distort any obligation, deadline, or dollar figure in the original; flag anything it changed. That Ultra "meaning-preservation check" is the tech-implementation story.
6. **Tavily:** Marginal — could fetch plain-language definitions for benefits/legal terms from public sources. Optional; the core demo doesn't need it.
7. **Build scope:** 5–7 days — the simplest build of the five. Paste-text in, cards out, 2–3 sample documents. Leaves schedule buffer, which matters with an Oct 30 hard deadline.
8. **Biggest risk:** Commoditization — "simplify this document" is one prompt in any chatbot. Defense must be the *fidelity check + persistent personal reading profile + citations*, demoed explicitly. If the demo looks like a wrapper, it loses; if the Ultra fact-check visibly catches a dropped deadline, it wins the room.

## 4. Fiduciary Red Flag — a pay-and-cyber pre-check for committee members

1. **Pitch:** Before a compensation or audit committee meets, upload a proposed executive-pay package or a vendor cybersecurity proposal; get the red flags a seasoned fiduciary would hunt for — benchmarked against live peer data.
2. **Track fit:** Best Apps and Agents.
3. **Winning demo moment:** A sample CEO pay proposal goes in. Out: "Pay rose 18% while total shareholder return fell 4% — pay/performance disconnect," each flag tied to a peer figure pulled live, plus five pointed questions to ask management, written in committee language. Second act, 30 seconds: a vendor cyber proposal gets flagged for a known-vulnerability disclosure found in search. One tool, both of his committee worlds.
4. **Only Jose Luis:** He chaired CalPERS' Performance, Compensation & Talent committee at one of the largest pension funds in the world *and* chaired a credit-union cybersecurity committee. Almost no hackathon entrant on Earth holds both seats. This is the highest credential-moat idea in the set.
5. **Model split:** Nano/Super — extract pay components, contract terms, and claims from the proposal into structured tables. Ultra — the fiduciary reasoning pass: pay-vs-performance logic, flag generation, and drafting questions in the register a committee actually uses.
6. **Tavily:** Strong, natural fit — peer executive-pay figures, recent governance news, and vulnerability/CVE lookups *must* be live data; stale benchmarks are worthless. Second-best Tavily-bonus story after Podrá.
7. **Build scope:** 8–10 days — the hardest build here. Needs 2 polished sample proposals and a constrained benchmark set (don't attempt live SEC-filing parsing at scale; Tavily + a curated peer table is enough for demo).
8. **Biggest risk:** Data accuracy. A wrong peer figure or a flag that reads as an accusation against a real company is a credibility/defamation hazard — demo only on fictional companies with real *methodology*. Second risk: audience is narrow (judges must grasp fiduciary stakes fast — the demo script has to teach it in 20 seconds). Note: deliberately *not* BoardBrief — no packet summary; this is benchmarking + adversarial flagging.

## 5. SharePoint Steward — the stale-document audit that never deletes anything itself

1. **Pitch:** Point an agent at a (demo) SharePoint library; it finds duplicate, conflicting, and expired policy documents, and produces a cleanup plan a human approves item-by-item — the AI proposes, staff dispose.
2. **Track fit:** Coding and Agentic Engineering (multi-step agent over a document corpus) — the only strong entry in this track from his world, and that track's Jetson prize has a different competitive pool.
3. **Winning demo moment:** A messy mock library of 40 files: "Travel Policy 2023," "Travel Policy FINAL v2," "Travel-Policy-USE-THIS-ONE." The agent's audit table lands: these two **contradict** each other on the per-diem rate (quotes both lines side by side), these five are duplicates, this one expired in 2024 but is still the top search hit. Admin clicks Approve on three items; only those move to the archive folder. Nothing deleted, everything logged.
4. **Only Jose Luis:** He's a working SharePoint/M365 administrator at a community college district — he lives in other people's document chaos daily — and again the labor-first design (backs up records staff, replaces nobody) is his signature, not a slogan.
5. **Model split:** Nano/Super — classify, dedupe, and date/extract every document (the volume tier; this is what keeps 40 docs inside the credit budget). Ultra — contradiction detection across the surviving candidate pairs and drafting the audit rationale a records officer can defend.
6. **Tavily:** One honest use: check Microsoft's official current guidance on retention/versioning to cite in the cleanup plan. Minor, credible, not load-bearing.
7. **Build scope:** 7–9 days. Critical scoping call: **mock library, not a real tenant** — no M365 app registration, no Graph API permissions battle. Upload a folder of sample docs; the agent behavior is identical and demoable.
8. **Biggest risk:** Demo flatness — document hygiene sounds boring next to health and safety apps. It lives or dies on the contradiction moment (two policies, two per-diem rates, one employee reimbursed wrong). Also: real-SharePoint integration will be the first judge question — the README must state the mock-library scope and the Graph API path honestly.

---

## Generator A's honest ranking (for the coordinator's synthesis)

1. **Podrá Navega** — best impact + best Tavily story + his chairmanship. Highest ceiling, highest safety-engineering burden.
2. **Fiduciary Red Flag** — highest credential moat; harder build, data-accuracy risk.
3. **ClearRead** — fastest, safest build; authenticity carries it; commoditization is the fight.
4. **Steward's Second Chair** — most distinctive values story; narrower judge resonance.
5. **SharePoint Steward** — best Coding-track hedge if the swarm wants a second, less-contested track.

Lesson appended to `~/workspace/lyceum/LESSONS.md` (2026-10-11: pitch the credential moat, not the chatbot). No signups, submissions, or external actions taken.