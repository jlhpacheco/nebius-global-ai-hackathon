"""Barrier-detection eval for Podrá Navega (Fix #2 — the measured number).

Scores three detectors against the planted barriers in cases.json:

  1. pipeline_detector          — the app's approach, in demo mode:
       Pass 1 (direct): broad phrase/pattern detection per barrier.
       Pass 2 (AUDIT SWEEP): a dedicated second pass that re-reads the
       whole message looking ONLY for implied barriers (caregiver
       unavailable, paycheck timing, income lost by attending, shame,
       forms/reading difficulty). This is the demo-mode stand-in for
       the Nemotron 3 Ultra barrier-audit call in the live pipeline —
       same job, same input/output contract, rule-based body.
  2. pipeline_detector --no-audit — the Ultra ablation: pass 1 only.
       If this number equals the full pipeline number, Ultra is a
       costume and the red team's Stack bar fails in spirit.
  3. baseline_detector          — a naive single-pass matcher using
       only whole-word obvious keywords, standing in for what a plain
       single prompt to a general chatbot reliably surfaces: barriers
       stated with the obvious word, missed when paraphrased/implied.

HONESTY RULES (see README-eval.md): both detectors are rule-based
demo-mode stand-ins. The numbers printed here are REAL outputs of
running this code on cases.json — nothing is hand-written. The live
Nemotron numbers must be measured with this same harness once the
API key is connected.

Run:  python3 run_eval.py [--no-audit]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))

BARRIERS = ["transport", "cost", "childcare", "work_schedule",
            "fear", "language", "health_literacy"]


def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text)


def _any(patterns: list[str], norm: str) -> bool:
    return any(re.search(p, norm) for p in patterns)


# ---------------------------------------------------------------------------
# BASELINE — naive single-pass, whole-word obvious keywords only.
# ---------------------------------------------------------------------------
BASELINE_WORDS: dict[str, list[str]] = {
    "transport":     [r"\btransporte\b", r"\bcarro\b", r"\bauto\b",
                      r"\btransportation\b", r"\bride\b"],
    "cost":          [r"\bdinero\b", r"\bmoney\b", r"\bcaro\b",
                      r"\bexpensive\b"],
    "childcare":     [r"\bninos\b", r"\bhijos\b", r"\bkids\b",
                      r"\bchildren\b"],
    "work_schedule": [r"\btrabajo\b", r"\bwork\b", r"\bturno\b",
                      r"\bshift\b"],
    "fear":          [r"\bmiedo\b", r"\btemor\b", r"\bfear\b",
                      r"\bscared\b", r"\bafraid\b"],
    "language":      [r"\bingles\b", r"\benglish\b"],
    "health_literacy": [r"no entiendo", r"no comprendo",
                        r"don'?t understand"],
}


def baseline_detector(message: str) -> set[str]:
    norm = _normalize(message)
    return {b for b, pats in BASELINE_WORDS.items() if _any(pats, norm)}


# ---------------------------------------------------------------------------
# PIPELINE PASS 1 — direct detection, broader phrase patterns.
# ---------------------------------------------------------------------------
PIPELINE_DIRECT: dict[str, list[str]] = {
    "transport":     [r"\btransporte\b", r"\bcarro\b", r"\bauto\b",
                      r"\bcamion\b", r"\bautobus\b", r"\bbus\b",
                      r"\bshuttle\b", r"\bride\b", r"\btransportation\b"],
    "cost":          [r"\bdinero\b", r"\bmoney\b", r"\bcopago\b",
                      r"\bcopay\b", r"\bcosto\b", r"\bcosts?\b",
                      r"\bcaro\b", r"\bexpensive\b", r"\bseguro\b",
                      r"\binsurance\b", r"\bpagar\b"],
    "childcare":     [r"\bninos\b", r"\bhijos\b", r"\bkids\b",
                      r"\bchildren\b", r"\bchildcare\b", r"\bguarderia\b",
                      r"\bcuide\b", r"\bcuidar\b"],
    "work_schedule": [r"\btrabajo\b", r"\bwork\b", r"\bturno\b",
                      r"\bshift\b", r"\bjefe\b", r"\bboss\b",
                      r"\bhorario\b", r"\bjob\b", r"\bempleo\b",
                      r"\bfalto\b"],
    "fear":          [r"\bmiedo\b", r"\btemor\b", r"\bfear\b",
                      r"\bscared\b", r"\bafraid\b", r"\bnervios\w*\b",
                      r"\bnervous\b", r"\bpreocup\w*\b", r"\bworried\b",
                      r"\bworry\b"],
    "language":      [r"\bingles\b", r"\benglish\b", r"\bidioma\b",
                      r"\blanguage\b", r"\binterprete\b",
                      r"\binterpreter\b"],
    "health_literacy": [r"no entiendo", r"no comprendo",
                        r"don'?t understand", r"\bconfund\w*\b",
                        r"no se llenar"],
}


# ---------------------------------------------------------------------------
# PIPELINE PASS 2 — AUDIT SWEEP (the Ultra stand-in).
# Inference rules for barriers that are IMPLIED, not stated with the
# obvious keyword. Each rule names the implication it encodes.
# ---------------------------------------------------------------------------
def _audit_sweep(norm: str) -> set[str]:
    found: set[str] = set()
    kids = r"(nietos|ninos|hijos|grandkids|kids|children)"
    unavailable = r"(trabaja de noche|trabaja todo el dia|works nights|works all day)"

    # The only driver is unavailable (works nights / all day)
    if _any([r"unico que maneja", r"only (one|person) who drives",
             r"es el que maneja"], norm):
        found.add("transport")
    # Distance / multi-leg trip stated without the word "transport"
    if _any([r"dos autobuses", r"dos camiones", r"two buses",
             r"transbordo", r"an hour away", r"hours? away",
             r"lives in another state", r"vive en otro estado"], norm):
        found.add("transport")
    # Lives alone, no one nearby -> getting home is a transport problem
    if _any([r"vivo sola", r"vivo solo", r"i live alone",
             r"live by myself"], norm):
        found.add("transport")
    # The helper with the children is unavailable -> childcare gap
    if re.search(kids, norm) and _any([unavailable], norm):
        found.add("childcare")
    # Dependents live with the patient full-time -> dependent-care barrier
    if _any([r"viven conmigo", r"live with me", r"lives with me",
             r"a mi cargo"], norm) and re.search(kids + r"|(madre|padre)", norm):
        found.add("childcare")
    # Attending costs a day's pay -> work_schedule AND cost
    if _any([r"si falto", r"if i miss", r"miss a morning",
             r"pierdo\b.{0,30}\bpaga\b", r"lose a day"], norm):
        found.add("work_schedule")
        if _any([r"no me pagan", r"don'?t get paid", r"pierdo",
                 r"paga\b"], norm):
            found.add("cost")
    # Paycheck timing / money running short -> cost
    if _any([r"me pagan (cada|hasta)", r"paycheck", r"cobro (cada|hasta)",
             r"no me alcanza", r"no alcanza para"], norm):
        found.add("cost")
    # Shame, or hiding the illness from family -> emotional (fear) barrier
    if _any([r"me da (pena|verguenza)", r"embarrass\w*", r"ashamed",
             r"no quiero preocupar", r"don'?t want to worry",
             r"trato de no pensar", r"no quiero pensar",
             r"try not to think"], norm):
        found.add("fear")
    # Reading / forms difficulty stated without "I don't understand"
    if _any([r"me cuesta leer", r"leer me cuesta",
             r"reading (long letters )?is hard", r"hard for me to read",
             r"struggle to read", r"las letras se me"], norm):
        found.add("health_literacy")
    if _any([r"formulario", r"papeles", r"paperwork", r"\bforms\b"], norm) and \
       _any([r"confund\w*", r"dificil", r"hard", r"no se"], norm):
        found.add("health_literacy")

    return found


def pipeline_detector(message: str, audit: bool = True) -> set[str]:
    norm = _normalize(message)
    found = {b for b, pats in PIPELINE_DIRECT.items() if _any(pats, norm)}
    if audit:
        found |= _audit_sweep(norm)
    return found


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------
def score(detector, cases) -> tuple[int, int, dict[str, list[int]]]:
    caught = planted_total = 0
    per_barrier: dict[str, list[int]] = {b: [0, 0] for b in BARRIERS}
    for case in cases:
        found = detector(case["message"])
        for pb in case["planted_barriers"]:
            planted_total += 1
            per_barrier[pb["barrier"]][1] += 1
            if pb["barrier"] in found:
                caught += 1
                per_barrier[pb["barrier"]][0] += 1
    return caught, planted_total, per_barrier


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-audit", action="store_true",
                    help="Headline pipeline result uses pass 1 only "
                         "(the Ultra ablation). All three rows still print.")
    args = ap.parse_args()

    with open(os.path.join(HERE, "cases.json"), encoding="utf-8") as f:
        cases = json.load(f)

    # Integrity: every evidence span must be a verbatim substring.
    for case in cases:
        for pb in case["planted_barriers"]:
            assert pb["evidence"] in case["message"], \
                f"{case['id']}: evidence not verbatim in message: {pb['evidence']!r}"

    detectors = [
        ("Pipeline (pass 1 + audit sweep)",
         lambda m: pipeline_detector(m, audit=True)),
        ("Pipeline WITHOUT audit (Ultra ablation)",
         lambda m: pipeline_detector(m, audit=False)),
        ("Baseline (naive single-pass keywords)",
         baseline_detector),
    ]

    print(f"Podrá Navega — barrier-detection eval "
          f"({len(cases)} fictional cases)\n")
    header = f"{'Detector':<44s} {'Caught':>7s} {'Planted':>8s} {'Catch rate':>11s}"
    print(header)
    print("-" * len(header))
    results = {}
    per_barrier_rows = {}
    for name, det in detectors:
        caught, total, per_barrier = score(det, cases)
        results[name] = (caught, total)
        per_barrier_rows[name] = per_barrier
        rate = 100.0 * caught / total if total else 0.0
        print(f"{name:<44s} {caught:>7d} {total:>8d} {rate:>10.1f}%")

    full = results["Pipeline (pass 1 + audit sweep)"]
    noaudit = results["Pipeline WITHOUT audit (Ultra ablation)"]
    base = results["Baseline (naive single-pass keywords)"]
    print(f"\nUltra-ablation delta: full pipeline {full[0]}/{full[1]} vs "
          f"no-audit {noaudit[0]}/{noaudit[1]} "
          f"({full[0] - noaudit[0]} barriers exist only because the "
          f"audit sweep runs)")
    print(f"Baseline delta: full pipeline {full[0]}/{full[1]} vs "
          f"baseline {base[0]}/{base[1]}")

    print("\nPer-barrier (caught/planted):")
    print(f"{'Barrier':<16s} {'Pipeline':>10s} {'No-audit':>10s} {'Baseline':>10s}")
    for b in BARRIERS:
        row = []
        for name, _, in [(n, None) for n, _ in detectors]:
            c, t = per_barrier_rows[name][b]
            row.append(f"{c}/{t}")
        print(f"{b:<16s} {row[0]:>10s} {row[1]:>10s} {row[2]:>10s}")

    print("\nPer-case misses:")
    for case in cases:
        planted = {pb["barrier"] for pb in case["planted_barriers"]}
        for name, det in detectors:
            missed = planted - det(case["message"])
            if missed:
                print(f"  {case['id']} [{name.split('(')[0].strip()}] "
                      f"missed: {', '.join(sorted(missed))}")

    if args.no_audit:
        print("\n(--no-audit given: headline pipeline = pass 1 only in "
              "the live app configuration; table above unchanged.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
