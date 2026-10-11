# Live Barrier Eval — Run Plan

Date: Oct 11, 2026. Status: prepped, dry-run clean, authorized by the
principal ("yes, whatever the contest say to use" — Nebius Token
Factory + Nemotron only).

## Why this run exists

The demo-mode eval (run_eval.py) scores rule-based stand-ins: pipeline
25/25, naive baseline 10/25, no-audit ablation 13/25. Those numbers are
honest for what they are, but the submission needs the REAL Nemotron
numbers through the same cases and the same scorer semantics. This is
that run.

## The bridge (how live calls happen without a raw key)

The API key lives only in the Secure Vault (connector
`custom.nebius-token-factory`); no raw value exists on this machine.

- `app/surrogate_transport.py` — performs chat completions via the
  vault's dynamic-credential surrogate helper (same mechanism as the
  nebius-token-factory skill CLI). Only `hsurr:*` surrogates leave the
  process, only to api.tokenfactory.nebius.com.
- `app/token_factory.py` — `chat()` routes through the surrogate
  transport ONLY when env `PODRA_TF_TRANSPORT=surrogate` is set.
  Default behavior (demo mode / OpenAI client) is unchanged; the 14
  backend tests pass with the flag unset.
- `eval/run_live_eval.py` — the runner. Every model call lands in the
  app ledger with real response usage, so spend is computed from actual
  tokens at ledger rates, not estimates.

## Arms (12 fictional cases, 25 planted barriers)

| Arm | What runs | Model calls/case |
|---|---|---|
| Live pipeline | `app.main.run_pipeline` verbatim: Super draft + Nano gloss + ONE Ultra barrier audit; app's own JSON parse with rule fallback | 3 (Super, Nano, Ultra) |
| No-audit ablation | `barriers.detect_barriers` only — what the pipeline surfaces with the Ultra step removed (the audit's input/fallback) | 0 |
| Baseline | Plain chatbot: one unadorned prompt, barrier counted caught when the reply itself names it | 1 (Nano) |

Total model calls for the full run: 48 (36 pipeline + 12 baseline).
The gloss call is kept because the audit consumes the draft the app
actually produces — the pipeline arm is the app, not a re-implementation.

Model IDs (live-verified Oct 11, 2026, exact casing):
Nano `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` ·
Super `nvidia/nemotron-3-super-120b-a12b` ·
Ultra `nvidia/Nemotron-3-Ultra-550b-a55b`

## Cost projection

Per-case prompt sizes measured in demo mode (draft in ≈110 tok, gloss
in ≈120, audit in ≈300, baseline in ≈95), outputs estimated with
reasoning-model headroom, at ledger rates (Nano $0.06/$0.24, Super
$0.30/$0.90, Ultra $1/$3 per 1M):

- Expected total (12 cases, all arms): **$0.0232**
- Hard-cap worst case (every output hits its max_tokens cap): **$0.0497**

Both are far under the $3.00 fire gate. Nothing in the design is
wasteful: the ablation is free, the baseline is a single cheap Nano
call per case, and Ultra — the only expensive model — runs exactly
once per case, as the app design rations it. Reproduce with:
`python3 eval/run_live_eval.py --project`

## Fire command

```
cd ~/workspace/nebius-hackathon/repo
PODRA_TF_TRANSPORT=surrogate ~/workspace/nebius-hackathon/venv/bin/python eval/run_live_eval.py
```

## Pre-flight record

- pytest app/test_main.py app/test_tavily.py: **14/14 pass** (flag unset).
- Stubbed dry-run (`--dry-run`, zero network): all 12 cases flowed
  through all 3 arms, 48 stubbed calls, scorer produced full tables.
  (Dry-run scores are plumbing artifacts — the stub audit echoes the
  rule findings — and are NOT results.)

## Kill bar (pre-registered)

Live pipeline barrier recall < 50% (fewer than 13 of 25 planted
barriers) = STOP and rethink. No tuning and re-running on the same
cases after seeing a failing score.
