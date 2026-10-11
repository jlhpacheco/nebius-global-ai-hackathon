# Deploy Guide — Podrá Navega

Plain-language steps for putting the demo on the web and keeping it alive
through judging. Read this top to bottom once; it is short on purpose.

## The plan in one paragraph

The demo runs on **Render's free tier** as one small web service
(`render.yaml` in this repo). It holds **no data**: no disk, no database.
That is on purpose — a free Render database would expire during the
December judging window, and a demo that dies in December scores zero.
With nothing stored, there is nothing to expire.

## Deploy steps

1. Push this repo to GitHub (it stays private until submission — see the
   checklist at the bottom).
2. In Render: **New → Blueprint**, pick this repo. Render reads
   `render.yaml` and creates the `podra-navega` web service.
3. Render will ask for the two secret values below. Paste them in the
   dashboard when asked. Never type a key into any file in this repo.
4. Wait for the first build (`pip install -r requirements.txt`, then the
   app starts). Open the service URL and check `/api/health` answers.
5. Run one full demo case end to end before calling it done.

## Secrets (set in Render, never in git)

| Name | What it is | Required? |
|---|---|---|
| `NEBIUS_API_KEY` | Nebius Token Factory key — the live Nemotron calls | For live mode |
| `TAVILY_API_KEY` | Tavily key — the live resource-check searches | For live mode |

- In `render.yaml` both are marked `sync: false`, which means Render
  prompts for them in the dashboard instead of reading them from git.
- With **no keys set, the app runs in demo mode**: it serves the
  pre-computed golden sample run and makes no paid calls. That is the
  safe default, and it is also what protects the credit reserve below.
- Locally, copy `.env.example` to `.env` and fill that in instead.
  `.env` is in `.gitignore` — it must never be committed.

## The spin-down reality (free tier)

- A free Render service **falls asleep after about 15 idle minutes**.
  The first visit after that takes **about 1 minute** to wake up.
- That is normal, not broken. The app shows a **"waking up" state**, so a
  judge's first click does not look like an error page.
- Do not panic-fix this by upgrading or re-deploying during judging.
  A slow first load with an honest waking-up message beats a dead link.

## Judging window: December 1–15, 2026 — keep it alive, keep the reserve

Judges may visit at any time in that window, and they are **not required
to test the app** — but if they do click, the demo must work.

- **Credit reserve is locked: $30 of the $50** in Token Factory credits
  is reserved for judging. Development and filming stay inside the other
  $20. Do not "borrow" from the reserve in October — a demo that runs
  out of credits in December is the same as a dead link.
- **Rate limits live in the app itself** (per-visitor limits, a daily
  spend ceiling, a cap of 3 Tavily searches per case, and demo mode /
  replay as the default path). They exist so strangers clicking around
  cannot drain the reserve.
- **Health checks:** open the demo URL and run one case on
  **Dec 1, Dec 8, and Dec 15**. If it is asleep, one visit wakes it.
  If it errors, fix it that day — do not wait.
- Change nothing structural during judging. No new features, no
  re-deploys unless the service is actually down.

## Two-URL plan

- **Primary:** the Render URL above. This is the URL that goes on the
  Devpost submission.
- **Mirror: TODO.** A second host (for example a Streamlit Community
  Cloud copy) as a backup link in the README, in case the primary is
  asleep or down when a judge clicks. Not built yet — set it up before
  Oct 28 and test that it runs the same golden demo.
- Both URLs must be **public, with no login**. A judge who hits a
  sign-in wall will not come back.

## Pre-submission checklist

Do these before the submission goes in (deadline: **Oct 30, 2026,
10:00 AM PDT**). The entrant's explicit go is required before submitting.

- [ ] **Flip this repo to public.** The rules require a publicly
      accessible repository with the license visible at the top of the
      repo page. Private is for development only.
- [ ] **README cold-test:** on a clean machine / fresh account, follow
      only the README — clone, set the two keys (or none, for demo
      mode), install, run. If any step needs knowledge that is not
      written down, fix the README, not the tester.
- [ ] **Run `python3 verify_models.py` with the real key** and confirm
      the three Nemotron model IDs in the app match the exact casing
      the Token Factory API returns.
- [ ] **Demo link is public and needs no login**; the golden sample
      loads with one click (a judge may have no file of their own).
- [ ] **Video is live and public** (YouTube, 3 minutes or less) and
      shows the real app running — not slides.
- [ ] **Credit reserve intact:** at least $30 of Token Factory credit
      untouched for the December judging window.
- [ ] Feedback section on Token Factory / NVIDIA tools filled in on
      the submission form (it is also a small prize category).
