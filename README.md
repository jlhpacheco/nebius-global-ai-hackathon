# Nebius x NVIDIA Global AI Hackathon — Project Workspace

Entrant: Jose Luis Pacheco (Devpost: [jlpacheco](https://devpost.com/jlpacheco))
Hackathon: [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/)
Status: **Use-case selection in progress — app not yet built. This repo is PRIVATE during development and will be made public before submission, as the rules require a publicly accessible repository.**

## Deadline

- Submissions close **October 30, 2026 at 10:00 AM PDT**
- Judging: December 1–15, 2026
- Winners announced on or around January 11, 2027

## Hard requirements (verified from the official rules)

- The project must **run on Nebius Token Factory or Nebius AI Cloud** and use **at least one NVIDIA open-source model** (Nemotron family).
- "Runs on Nebius" means a **runtime call to the Token Factory inference API**, or deployment/run on Nebius AI Cloud compute (Serverless Jobs, Serverless Endpoints, or DevPods).
- Deliverables: working demo URL, text description, track selection, public code repo with an open-source license and a README with setup instructions, a public YouTube demo video of 3 minutes or less, and a completed feedback section.
- No Vast.ai and no Together.ai are required or used for this hackathon — the required platform is Nebius.

## Planned stack

- **Nebius Token Factory only** (OpenAI-compatible API). No AI Cloud / GPU provisioning — avoids the $25 AI Cloud card charge and idle-GPU billing.
- Model routing: Nemotron Nano / Super for fast, cheap calls; Nemotron 3 Ultra for one hard reasoning step per workflow.
- Tavily API call where web grounding is genuinely part of the workflow (also the eligibility condition for the Best Use of Tavily bonus prize).
- Budget: $50 in documented Token Factory credits ($25 hackathon form + $25 Builders Program).

## Files in this repo

- `RULES-SUMMARY.md` — verified summary of the official rules (the official rules on Devpost govern, not this summary)
- `MISSION-BRIEF.md` — the swarm mission brief for use-case selection
- `USE-CASES.md` — the scored use-case shortlist and recommendation
- `ARCHITECTURE.md` — reference architecture and kill risks
- `docs/swarm/` — the six swarm front reports (track strategy, winning patterns, two idea generators, architecture, red team)

## Timeline

| Dates | Work |
|---|---|
| Oct 12–13 | Claim credits, test Nemotron API on Token Factory |
| Oct 14–20 | Build the working app (kill-bar check on Oct 18) |
| Oct 21–24 | Polish, host the live demo |
| Oct 25–27 | Repo cleanup, README, license, 3-minute video |
| Oct 28 | Full Devpost draft for entrant review |
| Oct 29 | Submit (one day of buffer) — only on the entrant's explicit go |
| Oct 30, 10:00 AM PDT | Deadline |
