#!/usr/bin/env python3
"""Verify which Nemotron model IDs Nebius Token Factory actually serves.

Why this exists: public sources disagree on the exact casing of model IDs
(for example, "nvidia/Nemotron-3-Ultra-550b-a55b" vs. lowercase forms), so
IDs must be confirmed against the live API, never copied from a blog post.

Usage:
    NEBIUS_API_KEY=... python3 verify_models.py

With no key set, the script prints a clear "cannot verify yet" message and
exits 0, so it is safe to run anywhere. Uses only the Python standard
library (urllib), so it runs with no dependencies installed.
"""

import json
import os
import sys
import urllib.error
import urllib.request

MODELS_URL = "https://api.tokenfactory.nebius.com/v1/models"

# The three Nemotron tiers this project uses — exact ID strings as
# returned by GET /v1/models, live-verified Oct 11, 2026. (The Nano ID's
# casing differs from the lowercase form in most public write-ups.)
# Matching against the API response is case-insensitive; the API's own
# casing is what gets printed and what should go into the app config.
EXPECTED_MODELS = [
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
    "nvidia/nemotron-3-super-120b-a12b",
    "nvidia/Nemotron-3-Ultra-550b-a55b",
]


def main() -> int:
    api_key = os.environ.get("NEBIUS_API_KEY", "").strip()
    if not api_key:
        print("NEBIUS_API_KEY is not set — no key, cannot verify models yet.")
        print("Set NEBIUS_API_KEY and re-run this script to check the live")
        print("model list on Nebius Token Factory.")
        return 0

    request = urllib.request.Request(
        MODELS_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        print(f"Token Factory returned HTTP {exc.code} — key or request rejected.")
        return 1
    except urllib.error.URLError as exc:
        print(f"Could not reach Token Factory: {exc.reason}")
        return 1

    model_ids = [
        entry["id"]
        for entry in payload.get("data", [])
        if isinstance(entry, dict) and "id" in entry
    ]

    print(f"Token Factory returned {len(model_ids)} model(s):")
    for model_id in sorted(model_ids):
        print(f"  {model_id}")

    by_lowercase = {model_id.lower(): model_id for model_id in model_ids}

    print("\nPlanned models check:")
    missing = 0
    for expected in EXPECTED_MODELS:
        actual = by_lowercase.get(expected.lower())
        if actual is not None:
            print(f"  PRESENT  {actual}  (planned as: {expected})")
        else:
            missing += 1
            print(f"  MISSING  {expected}  (not returned by the API)")

    if missing:
        print(
            f"\nResult: {missing} of {len(EXPECTED_MODELS)} planned model(s) "
            "are NOT in the API list. Do not hard-code a missing ID — pick "
            "the closest ID the API actually returned and update the app."
        )
    else:
        print("\nResult: all planned models are available. Use the exact")
        print("casing printed above in the app configuration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
