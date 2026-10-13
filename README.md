# Podrá Navega

A bilingual (English/Spanish) cancer-navigation copilot for **Latinas Contra Cancer**. A patient writes in plain words; the AI drafts a plain-language reply, a question list for the doctor, and flags the barriers patients never say out loud — and **nothing is sent until a human navigator reviews, verifies, and approves it**.

Built for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) — Best Apps and Agents track. Entrant: Jose Luis Pacheco (Devpost: [jlpacheco](https://devpost.com/jlpacheco)).

## Live demo

**https://podra-navega.onrender.com**

- Hosted on Render's free tier, which **sleeps when idle** — the first click after a quiet spell can take ~50 seconds to wake. That is normal, not broken.
- The demo runs in **demo mode** with **fictional patients only**.

## Demo video

**https://www.youtube.com/watch?v=RXGDiJFIHnk** (2:51, public)

The voiceover is the author, a real person. Elena, the demo navigator, is synthetic — see Safety and scope below.

## What it does

- **A patient writes** in Spanish or English, in their own words (WhatsApp-style web chat).
- **The AI drafts**: Super writes a plain-language reply in the patient's language, Nano renders a faithful English gloss, and the doctor question list comes from an approved template — never free-generated medical text.
- **Ultra audits the case** — exactly **one call per case**. It re-reads the message against the barrier taxonomy (transport, cost, childcare, work schedule, fear, language, health literacy) to catch the barriers the patient only implied.
- **Every resource named in the draft is verified live with Tavily** (the ride program, the clinic page) before it can be used. Approve stays **locked server-side** until every resource checks out.
- **A human navigator approves.** The navigator can edit the draft, and must tap Approve before anything is sent. Crisis or medical-advice messages **escalate instantly** — no draft is generated at all.

## Measured results

Live evaluation, October 11, 2026 — real Nemotron calls through Nebius Token Factory, one pre-registered pass, same harness and case file for all three detectors. **12 fictional cases, 25 planted barriers.**

| Detector | Barriers caught | Catch rate |
|---|---|---|
| **Podrá pipeline (draft + Ultra audit)** | **24 / 25** | **96.0%** |
| Plain-chatbot baseline (one call per case) | 19 / 25 | 76.0% |
| Podrá with the audit step removed | 11 / 25 | 44.0% |

- **Safety battery: 31/31** adversarial prompts passed (zero tolerance on crisis and medical-advice cases).
- The audit step is load-bearing: removing it drops the catch rate from 96.0% to 44.0%.
- Total live-eval cost: **$0.035068 across 48 real Nemotron calls** — zero calls fell back to demo responses.
- Full method, case file, and raw output: [`eval/README-eval.md`](eval/README-eval.md).

## How it uses the sponsor stack

- **Nebius Token Factory** — every AI step is a **runtime call** to the Token Factory inference API (OpenAI-compatible, `https://api.tokenfactory.nebius.com/v1/`). Model routing is tiered on purpose: cheap models for drafting, the flagship model once per case where it measurably matters.
- **NVIDIA Nemotron** (open-source models, exact API IDs):
  - Nano — `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` — English gloss
  - Super — `nvidia/nemotron-3-super-120b-a12b` — patient-language draft reply
  - Ultra — `nvidia/Nemotron-3-Ultra-550b-a55b` — one barrier-audit pass per case
- **Tavily** — the app calls the **Tavily API** at runtime to verify every resource named in a draft against the live web (search restricted to the resource's own domain), and stores the evidence snippet on the case. If Tavily finds no matching source, the resource stays unverified and approval stays blocked — the app never fakes a check.

## Run it locally

From the repo root:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Environment variables (set them in your shell or a local `.env` — never commit keys):

| Variable | What it does |
|---|---|
| `NEBIUS_API_KEY` | Nebius Token Factory key. Set → live Nemotron calls. **Blank → demo mode**: the full flow runs end-to-end with deterministic drafting, every response flagged `demo_mode: true`, and no paid calls. |
| `TAVILY_API_KEY` | Tavily key. Set → resource verification runs as a real Tavily search (`verified_via: "tavily"`). Blank → the navigator's manual verification against the local directory, honestly labeled `verified_via: "local_cache"`. |

Then open `http://localhost:8000`. The app seeds one golden fictional case (`CASE-0001`) so the full flow — draft, verify, approve — works with one click.

Tests:

```bash
python -m pytest app/test_main.py app/test_tavily.py -v
```

More detail: [`app/README-backend.md`](app/README-backend.md) (endpoints, workflow, cost ledger) and [`DEPLOY.md`](DEPLOY.md) (Render deploy steps).

## Safety and scope

- **Fictional patients only.** All demo and eval data is invented; cases use case IDs, never names. No real patient data is used, stored, or sent — the app keeps no database by design (in-memory only; state resets when the host sleeps).
- **Information and preparation only.** Podrá explains and helps a patient prepare. It does **not** diagnose, treat, or give medical advice; medical-advice and crisis messages escalate to a human immediately, with no AI draft.
- **Synthetic demo navigator.** The demo navigator, **Elena**, is a synthetic persona and is labeled as such on screen. Human-in-the-loop is the design, not a disclaimer: in real use, a real navigator holds the Approve button.
- **No diagnosis, no treatment, no exceptions** — enforced server-side, not just hidden in the UI.

## Project docs

- [`RULES-SUMMARY.md`](RULES-SUMMARY.md) — verified summary of the official hackathon rules (the official rules on Devpost govern, not this summary)
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — reference architecture and kill risks
- [`app/README-backend.md`](app/README-backend.md) — backend: model routing, workflow, Tavily verification, endpoints
- [`eval/README-eval.md`](eval/README-eval.md) — the live evaluation: method, results, and honest caveats
- [`DEPLOY.md`](DEPLOY.md) — deploy guide and judging-window notes
- [`docs/DECISION-synthetic-navigator.md`](docs/DECISION-synthetic-navigator.md) — why the demo navigator is synthetic

## License

MIT — see [`LICENSE`](LICENSE).
