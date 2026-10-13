"""In-memory case store for Podrá Navega, seeded with ONE golden
fictional case (the biopsy/transport example) so the demo replays at $0:
the seeded case is pre-computed and its ledger entry records 0 tokens /
$0 cost under model="demo-mode".

All patient data is fictional. Cases are identified by case IDs, never
by patient names.
"""

from __future__ import annotations

import copy
import threading
from datetime import datetime, timezone

from . import barriers as barriers_mod
from .token_factory import LEDGER

GOLDEN_MESSAGE = (
    "They told me I need a biopsy and I don't understand, "
    "and I don't have a ride."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class CaseStore:
    def __init__(self) -> None:
        self._cases: dict[str, dict] = {}
        self._seq = 0
        self._lock = threading.Lock()
        self._seed_golden()

    # -- internals ---------------------------------------------------------
    def _next_id(self) -> str:
        self._seq += 1
        return f"CASE-{self._seq:04d}"

    def _seed_golden(self) -> None:
        case_id = self._next_id()  # CASE-0001
        language = barriers_mod.detect_language(GOLDEN_MESSAGE)
        found = barriers_mod.detect_barriers(GOLDEN_MESSAGE)
        draft = barriers_mod.draft_reply(GOLDEN_MESSAGE, language, found)
        now = _now()
        case = {
            "id": case_id,
            "created_at": now,
            "updated_at": now,
            "fictional": True,
            "language": language,
            "patient_message": GOLDEN_MESSAGE,
            "safety": {
                "category": "routine",
                "escalate": False,
                "reason": "Seeded golden case (fictional).",
                "source": "seed",
            },
            "state": "PENDING_APPROVAL",
            "state_history": [
                {"state": "RECEIVED", "at": now},
                {"state": "DRAFTED", "at": now},
                {"state": "PENDING_APPROVAL", "at": now},
            ],
            "draft": draft,
            "barriers_found": found,
            "barrier_checklist": {
                name: any(b["barrier"] == name for b in found)
                for name in barriers_mod.BARRIER_TAXONOMY
            },
            "resources": barriers_mod.resources_for(found),
            "approval_record": None,
            "navigator_edited": False,
            "demo_mode": True,
        }
        self._cases[case_id] = case
        LEDGER.append(
            case_id=case_id,
            stage="seed_golden_case:replay",
            model="demo-mode",
            tokens_in=0,
            tokens_out=0,
            demo_mode=True,
        )

    # -- public API --------------------------------------------------------
    def next_id(self) -> str:
        with self._lock:
            return self._next_id()

    def add(self, case: dict) -> dict:
        with self._lock:
            self._cases[case["id"]] = case
        return copy.deepcopy(case)

    def get(self, case_id: str) -> dict | None:
        with self._lock:
            case = self._cases.get(case_id)
        return copy.deepcopy(case) if case else None

    def update(self, case: dict) -> dict:
        case["updated_at"] = _now()
        with self._lock:
            self._cases[case["id"]] = case
        return copy.deepcopy(case)

    def list(self) -> list[dict]:
        with self._lock:
            return [copy.deepcopy(c) for c in self._cases.values()]


STORE = CaseStore()
