# Reference Architecture

Full report: `docs/swarm/architect.md`. Summary of the recommended shape:

## Shape

```
Browser (single polished page, no build step)
  -> FastAPI app
     -> Nebius Token Factory API (OpenAI-compatible, NEBIUS_API_KEY in env)
        - Nemotron Nano / Super: volume work (summaries, drafts, classification)
        - Nemotron 3 Ultra: one hard reasoning step per workflow
     -> Tavily API: web grounding where genuinely functional
```

## Rules of the build

- **Token Factory only.** No AI Cloud, no GPU provisioning, no Vast.ai, no Together.ai.
- **Model routing by cost:** cheap fast models do the volume; Ultra is rationed to 1–2 calls per workflow so the $50 credits survive development + judging.
- **Hosting:** the demo must be hosted free and stay reachable, unrestricted, until the judging period ends (Dec 15, 2026). Pick a host whose free tier does not expire mid-judging (see architect report for the expiry warning).
- **Demo-first design:** judges are not required to test the app. The video, screenshots, and description must carry the full story on their own.
- **State artifact, not text:** every workflow must visibly change a state artifact (approval record, memory file, checklist state, escalation flag). "Good text appeared" is not a demo.

## Top kill risks (from the architect + red team)

1. Demo host sleeps/expires before Dec 15 → judges see a dead link. Mitigation: host choice + a recorded video that shows everything.
2. Token burn during development eats the $50 before judging. Mitigation: Nano/Super default, Ultra rationed, cache sample outputs for the demo path.
3. Scope creep past the Oct 18 kill-bar check. Mitigation: pre-registered kill bars in `MISSION-BRIEF.md` and `docs/swarm/red-team.md`.
