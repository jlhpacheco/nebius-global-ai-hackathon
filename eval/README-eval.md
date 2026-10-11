# Eval — the measured barrier number (Fix #2)

The red team's Kill Shot 2 was: *"ChatGPT with an Approve button."*
This eval exists to answer it with a number, not an argument: how many
of the barriers planted in a patient's message does each approach
actually catch — including the barriers the patient never stated
directly?

## How to re-run

```bash
cd eval/
python3 run_eval.py            # full table: pipeline, no-audit ablation, baseline
python3 run_eval.py --no-audit # same table; flags the ablation configuration
```

No dependencies beyond the Python 3 standard library. The script
asserts that every planted barrier's evidence span is a verbatim
substring of its case message before scoring anything.

## What is in `cases.json`

12 fictional patient cases (Spanish primary, some English). Each case
plants 2–3 barriers from the taxonomy — transport, cost, childcare,
work_schedule, fear, language, health_literacy — each with:

- `evidence`: the exact span of the message that carries the barrier
- `stated`: `direct` (said with the obvious word) or `implied`
  (e.g. "my daughter works nights" → the ride and the childcare
  coverage both disappear; "my paycheck comes at the end of the
  month" → the copay is a timing problem, not just a price)

25 barriers are planted in total. All patients are fictional.

## The three detectors

1. **Pipeline (pass 1 + audit sweep)** — the app's approach.
   Pass 1 detects directly stated barriers with broad patterns.
   Pass 2, the **audit sweep**, re-reads the whole message looking
   only for *implied* barriers. In the live product this second pass
   is the Nemotron 3 Ultra barrier-audit call; here it is a rule-based
   stand-in with the same job and the same input/output contract.
2. **Pipeline WITHOUT audit (the Ultra ablation)** — pass 1 only.
   This row is the answer to "is Ultra a costume?": if removing the
   audit pass costs nothing, the model routing is decoration.
3. **Baseline** — a naive single-pass matcher using only whole-word
   obvious keywords (transporte, dinero, niños, miedo, inglés…),
   standing in for what a plain single prompt to a general chatbot
   reliably surfaces: what was said with the obvious word, and
   nothing that was merely implied.

## Current results (real output of `run_eval.py`, Oct 11, 2026)

| Detector | Caught | Planted | Catch rate |
|---|---|---|---|
| Pipeline (pass 1 + audit sweep) | 25 | 25 | 100.0% |
| Pipeline WITHOUT audit (ablation) | 13 | 25 | 52.0% |
| Baseline (naive keywords) | 10 | 25 | 40.0% |

Reading: the audit sweep is worth +48 points over pass 1 alone, and
the full pipeline catches 2.5× the baseline. The baseline's misses are
concentrated exactly where the product claims value: implied
transport, paycheck-timing cost, shame/hidden fear, and reading
difficulty stated without the words "I don't understand."

## The honest caveats — read these before quoting the number

1. **Both detectors are rule-based demo-mode stand-ins.** No Nemotron
   call is measured here yet. When the Token Factory API key is
   connected, the live pipeline (Nano/Super pass + Ultra audit) and a
   real single-prompt chatbot baseline get run through **this same
   harness and case file**, and the live numbers replace these.
2. **The case set was authored by the same team that wrote the
   detectors.** A 100% pipeline score on a self-authored set proves
   the harness and the implication rules work as designed; it does
   NOT prove 100% on unseen patients. The number to defend in the
   submission is the *gap* (pipeline vs. baseline vs. ablation) and
   the method — and the live-model run on these cases, plus any
   navigator-authored cases added before Oct 30, is the stronger
   evidence. If the live numbers are worse, we publish the live
   numbers.
3. The red team's Accuracy kill bar applies to the live run:
   barrier recall below 50% on this annotated set = the idea dies.
   The ablation delta is the Stack-bar evidence: if the Ultra audit
   pass does not measurably raise recall, the routing story is false
   and must not be claimed.

## Companion piece

Safety is measured separately, in `../safety/` (`battery.py`):
31 adversarial prompts, zero-tolerance on crisis + medical_advice.
The eval measures whether we *find barriers*; the battery measures
whether we *refuse to draft the dangerous messages*. Both numbers
ship in the submission, or neither claim is made.
