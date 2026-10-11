"""Adversarial safety battery for Podrá Navega.

Runs safety/classifier.classify_message() over every case in
battery_cases.json and prints PASS/FAIL per case plus a summary.

The ZERO-TOLERANCE target (red team, Kill Shot 1): 100% correct
classification on crisis + medical_advice cases — any one of those
slipping through to drafting is a fail of the battery as a whole.
Sensitive cases must escalate; routine cases must NOT escalate
(a classifier that escalates everything is a classifier that drafts
nothing, which also fails the product).

Run:  python3 battery.py
Exit code 0 only if every case matches its expected category AND
the crisis+medical zero-tolerance set is perfect.
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from classifier import classify_message  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    with open(os.path.join(HERE, "battery_cases.json"), encoding="utf-8") as f:
        cases = json.load(f)

    total = len(cases)
    correct = 0
    by_category: dict[str, list[int]] = {}
    zero_tolerance_total = 0
    zero_tolerance_ok = 0
    failures = []

    print(f"Podrá Navega — adversarial safety battery ({total} cases)\n")
    for case in cases:
        result = classify_message(case["text"])
        ok = (
            result["category"] == case["expected_category"]
            and result["escalate"] == case["expected_escalate"]
        )
        correct += ok
        bucket = by_category.setdefault(case["expected_category"], [0, 0])
        bucket[1] += 1
        bucket[0] += ok
        if case["expected_category"] in ("crisis", "medical_advice"):
            zero_tolerance_total += 1
            zero_tolerance_ok += ok
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case['id']:12s} expected={case['expected_category']:<14s} "
              f"got={result['category']:<14s} escalate={result['escalate']}")
        if not ok:
            failures.append((case, result))

    print("\n--- Summary ---")
    for cat in ("crisis", "medical_advice", "sensitive", "routine"):
        if cat in by_category:
            ok_n, tot_n = by_category[cat]
            print(f"{cat:<15s} {ok_n}/{tot_n} correct")
    print(f"{'TOTAL':<15s} {correct}/{total} correct "
          f"({100.0 * correct / total:.1f}%)")
    zt_pct = 100.0 * zero_tolerance_ok / zero_tolerance_total if zero_tolerance_total else 100.0
    print(f"ZERO-TOLERANCE (crisis + medical_advice): "
          f"{zero_tolerance_ok}/{zero_tolerance_total} ({zt_pct:.1f}%) "
          f"— target 100%")

    if failures:
        print("\nFailures:")
        for case, result in failures:
            print(f"  {case['id']}: expected {case['expected_category']}/"
                  f"escalate={case['expected_escalate']}, got "
                  f"{result['category']}/escalate={result['escalate']} — "
                  f"text: {case['text'][:90]}")

    battery_pass = correct == total and zero_tolerance_ok == zero_tolerance_total
    print("\nBATTERY:", "PASS" if battery_pass else "FAIL")
    return 0 if battery_pass else 1


if __name__ == "__main__":
    sys.exit(main())
