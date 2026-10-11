"""LIVE barrier-detection eval for Podrá Navega — real Nemotron calls.

Same cases, same scorer semantics as run_eval.py (demo mode), but the
detectors are the real models, reached through the vault-surrogate
transport (app/surrogate_transport.py; no raw API key exists on this
machine — the key lives only in the Secure Vault connector).

Arms:
  1. live pipeline   — app.main.run_pipeline verbatim: Super draft +
                       Nano gloss + ONE Ultra barrier audit per case,
                       the app's own JSON parse + rule fallback.
  2. no-audit ablation — barriers.detect_barriers only: exactly what
                       the pipeline surfaces with the Ultra step
                       removed (the audit's input/fallback). 0 calls.
  3. baseline        — a plain chatbot: ONE Nano call per case with a
                       plain prompt; a planted barrier counts as caught
                       when the reply itself names it (aliases below).

Usage:
  python3 run_live_eval.py --project   # cost projection only, $0
  python3 run_live_eval.py --dry-run   # stubbed transport, $0, no network
  PODRA_TF_TRANSPORT=surrogate python3 run_live_eval.py   # LIVE — spends

Kill bar (pre-registered, see LIVE-RUN-PLAN.md): live pipeline barrier
recall < 50% (fewer than 13 of 25 planted barriers) = STOP and rethink.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
for _p in (REPO, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# The surrogate transport flag must be set before token_factory is used.
os.environ["PODRA_TF_TRANSPORT"] = "surrogate"

from run_eval import BARRIERS, _normalize  # noqa: E402

BASELINE_PROMPT = (
    "You are a helpful assistant. A patient sent the message below to a "
    "cancer-care clinic. List the barriers or difficulties the patient "
    "mentions or implies that could make it hard for them to get care.\n\n"
    "Patient message: "
)

# A baseline catch = the chatbot's own reply names the barrier.
BASELINE_ALIASES: dict[str, list[str]] = {
    "transport": [r"transport\w*", r"transporte", r"\bride\b", r"\bbus\b",
                  r"\bcar\b", r"carro", r"travel"],
    "cost": [r"cost\w*", r"costo", r"money", r"dinero", r"afford\w*",
             r"\bpay\b", r"payment", r"insurance", r"seguro", r"financial"],
    "childcare": [r"childcare", r"child care", r"children", r"\bkids\b",
                  r"ninos", r"hijos", r"babysit\w*", r"cuidad\w*"],
    "work_schedule": [r"\bwork\b", r"trabajo", r"\bjob\b", r"empleo",
                      r"schedule", r"horario", r"\bshift\b", r"turno",
                      r"employer", r"\bboss\b", r"jefe"],
    "fear": [r"\bfear\b", r"miedo", r"afraid", r"scared", r"anxious",
             r"anxiety", r"ansiedad", r"worried", r"nervous", r"nervios",
             r"emotional"],
    "language": [r"language", r"idioma", r"english", r"ingles",
                 r"spanish", r"espanol", r"interpreter", r"interprete",
                 r"translat\w*"],
    "health_literacy": [r"literacy", r"understand\w*", r"entiende",
                        r"comprehension", r"reading", r"\bleer\b",
                        r"lectura", r"\bforms?\b", r"formulario",
                        r"confus\w*"],
}


def parse_baseline_reply(reply: str) -> set[str]:
    norm = _normalize(reply)
    return {
        b for b, pats in BASELINE_ALIASES.items()
        if any(re.search(p, norm) for p in pats)
    }


# ---------------------------------------------------------------------------
# Stubbed transport for --dry-run: NO network. Returns canned text shaped
# like each stage expects, so all 12 cases flow through every arm.
# ---------------------------------------------------------------------------
def install_stub() -> None:
    from app import barriers, surrogate_transport

    def stub_chat(*, model, messages, temperature=0.2, max_tokens=900):
        joined = "\n".join(m.get("content", "") for m in messages)
        if "List the barriers or difficulties" in joined:
            return ("The patient mentions transportation problems and "
                    "cost worries.", 90, 20)
        sysmsg = messages[0].get("content", "") if messages else ""
        if "barrier-audit" in sysmsg:
            payload = json.loads(messages[-1]["content"])
            findings = barriers.detect_barriers(payload["patient_message"])
            return (json.dumps({"barriers_found": findings}), 300, 50)
        return ("Stub draft text for plumbing verification.", 110, 30)

    surrogate_transport.surrogate_chat = stub_chat


# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------
def arm_pipeline(case: dict) -> set[str]:
    from app import main as app_main

    case_dict = {
        "id": case["id"],
        "patient_message": case["message"],
        "language": case["lang"],
    }
    result = app_main.run_pipeline(case_dict)
    return {b["barrier"] for b in result["barriers_found"]}


def arm_no_audit(case: dict) -> set[str]:
    from app import barriers

    return {b["barrier"] for b in barriers.detect_barriers(case["message"])}


def arm_baseline(case: dict) -> set[str]:
    from app import token_factory

    reply = token_factory.chat(
        stage="baseline_chatbot",
        model_key="nano",
        messages=[{"role": "user",
                   "content": BASELINE_PROMPT + case["message"]}],
        case_id=case["id"],
        demo_response="",
        max_tokens=300,
    )
    return parse_baseline_reply(reply)


# ---------------------------------------------------------------------------
# Scoring — same semantics as run_eval.score (caught per planted barrier)
# ---------------------------------------------------------------------------
def score_arm(found_by_case: dict[str, set[str]], cases) -> tuple[int, int, dict]:
    caught = planted_total = 0
    per_barrier = {b: [0, 0] for b in BARRIERS}
    for case in cases:
        found = found_by_case[case["id"]]
        for pb in case["planted_barriers"]:
            planted_total += 1
            per_barrier[pb["barrier"]][1] += 1
            if pb["barrier"] in found:
                caught += 1
                per_barrier[pb["barrier"]][0] += 1
    return caught, planted_total, per_barrier


def projection() -> None:
    """Cost projection from measured demo-mode prompt sizes (Oct 11,
    2026) with reasoning-model headroom on outputs, at ledger rates."""
    rows = [
        # stage, model, price in/out per 1M, est in, est out, cap out
        ("draft_reply (pipeline)", "Super", 0.30, 0.90, 110, 300, 900),
        ("draft_gloss_en (pipeline)", "Nano", 0.06, 0.24, 120, 300, 900),
        ("barrier_audit (pipeline)", "Ultra", 1.00, 3.00, 300, 400, 900),
        ("baseline_chatbot (baseline)", "Nano", 0.06, 0.24, 95, 200, 300),
    ]
    print("Cost projection — 12 cases, per-case call sizes measured in "
          "demo mode\n")
    exp_total = cap_total = 0.0
    for name, model, pin, pout, tin, tout, cap in rows:
        exp = (tin * pin + tout * pout) / 1_000_000
        worst = (tin * pin + cap * pout) / 1_000_000
        exp_total += exp
        cap_total += worst
        print(f"  {name:<30s} {model:<6s} expected ${exp:.6f}/case   "
              f"output-capped worst ${worst:.6f}/case")
    print(f"  {'no-audit ablation':<30s} {'—':<6s} 0 model calls, $0")
    print(f"\n  Expected total (12 cases):  ${exp_total * 12:.4f}")
    print(f"  Hard-cap worst case:        ${cap_total * 12:.4f}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", action="store_true",
                    help="Print the cost projection and exit ($0).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Stubbed transport: no network, $0.")
    args = ap.parse_args()

    if args.project:
        projection()
        return 0

    if args.dry_run:
        install_stub()

    with open(os.path.join(HERE, "cases.json"), encoding="utf-8") as f:
        cases = json.load(f)
    for case in cases:
        for pb in case["planted_barriers"]:
            assert pb["evidence"] in case["message"], case["id"]

    from app import token_factory

    arms = [
        ("Live pipeline (Super+gloss+Ultra audit)", arm_pipeline),
        ("No-audit ablation (rules only)", arm_no_audit),
        ("Baseline (plain chatbot, 1 Nano call)", arm_baseline),
    ]
    mode = "DRY RUN (stubbed, $0)" if args.dry_run else "LIVE"
    print(f"Podrá Navega — LIVE barrier eval [{mode}] "
          f"({len(cases)} fictional cases)\n")

    results = {}
    for name, arm in arms:
        found_by_case = {c["id"]: arm(c) for c in cases}
        results[name] = (found_by_case, *score_arm(found_by_case, cases))

    header = f"{'Arm':<44s} {'Caught':>7s} {'Planted':>8s} {'Recall':>8s}"
    print(header)
    print("-" * len(header))
    for name, (_, caught, total, _) in results.items():
        print(f"{name:<44s} {caught:>7d} {total:>8d} "
              f"{100.0 * caught / total:>7.1f}%")

    print("\nPer-barrier (caught/planted):")
    print(f"{'Barrier':<16s} {'Pipeline':>10s} {'No-audit':>10s} "
          f"{'Baseline':>10s}")
    for b in BARRIERS:
        row = [f"{results[n][3][b][0]}/{results[n][3][b][1]}"
               for n, *_ in [(k, None) for k in results]]
        print(f"{b:<16s} {row[0]:>10s} {row[1]:>10s} {row[2]:>10s}")

    print("\nPer-case misses (pipeline):")
    pipe_found = results["Live pipeline (Super+gloss+Ultra audit)"][0]
    for case in cases:
        planted = {pb["barrier"] for pb in case["planted_barriers"]}
        missed = planted - pipe_found[case["id"]]
        if missed:
            print(f"  {case['id']} missed: {', '.join(sorted(missed))}")

    entries = token_factory.LEDGER.entries()
    live = [e for e in entries if not e["demo_mode"]]
    fallbacks = [e for e in entries if e["demo_mode"] and e["tokens_in"] > 0]
    actual = round(sum(e["est_cost_usd"] for e in live), 6)
    print(f"\nModel calls: {len(live)} live, {len(fallbacks)} fell back "
          f"to demo responses")
    print(f"Actual spend at ledger rates (from response usage): "
          f"${actual:.6f}")

    pipe_caught, pipe_total = results[
        "Live pipeline (Super+gloss+Ultra audit)"][1:3]
    if not args.dry_run:
        if pipe_caught / pipe_total < 0.50:
            print(f"\nKILL BAR HIT: live pipeline recall "
                  f"{pipe_caught}/{pipe_total} "
                  f"({100.0 * pipe_caught / pipe_total:.1f}%) < 50%. "
                  f"STOP and rethink — do not tune and re-run.")
            return 3
        print(f"\nKill bar cleared: live pipeline recall "
              f"{pipe_caught}/{pipe_total} >= 50%.")
    else:
        print("\nDRY RUN OK — all cases flowed through all arms; "
              "scorer produced numbers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
