"""Tests for the Podrá Navega backend (run in demo mode: no API key).

Run from the repo root:
    python -m pytest app/test_main.py -v
"""

import os
import sys

# Demo mode is required for deterministic tests: no Token Factory key.
os.environ.pop("NEBIUS_API_KEY", None)

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)

ROUTINE_MSG = (
    "Me dijeron que necesito una biopsia y no entiendo, "
    "y no tengo transporte."
)
CRISIS_MSG = "Tengo fiebre alta y estoy sangrando, no puedo respirar bien."
MEDICAL_MSG = "¿Debo tomar otra medicina para el dolor? ¿Puedo cambiar mi dosis?"


def _create(message: str) -> dict:
    resp = client.post("/api/cases", json={"message": message})
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["demo_mode"] is True


def test_golden_case_seeded():
    resp = client.get("/api/cases/CASE-0001")
    assert resp.status_code == 200
    case = resp.json()
    assert case["fictional"] is True
    assert case["state"] == "PENDING_APPROVAL"
    assert case["draft"] is not None
    barriers = {b["barrier"] for b in case["barriers_found"]}
    assert "transport" in barriers


def test_crisis_escalated_no_draft():
    case = _create(CRISIS_MSG)
    assert case["state"] == "ESCALATED"
    assert case["safety"]["category"] == "crisis"
    assert case["draft"] is None


def test_medical_advice_escalated_no_draft():
    case = _create(MEDICAL_MSG)
    assert case["state"] == "ESCALATED"
    assert case["safety"]["category"] == "medical_advice"
    assert case["draft"] is None


def test_routine_creates_draft_and_barriers():
    case = _create(ROUTINE_MSG)
    assert case["state"] == "PENDING_APPROVAL"
    assert case["draft"] is not None
    assert case["draft"]["reply"]
    assert case["draft"]["reply_en"]
    assert case["draft"]["question_list"]
    barriers = {b["barrier"] for b in case["barriers_found"]}
    assert "transport" in barriers
    transport = [b for b in case["barriers_found"] if b["barrier"] == "transport"]
    assert transport[0]["evidence"]  # evidence quote required
    states = [h["state"] for h in case["state_history"]]
    assert states == ["RECEIVED", "DRAFTED", "PENDING_APPROVAL"]


def test_approve_blocked_with_unverified_resource():
    case = _create(ROUTINE_MSG)
    assert any(not r["verified"] for r in case["resources"])
    resp = client.post(f"/api/cases/{case['id']}/approve")
    assert resp.status_code == 409


def test_approve_succeeds_after_verify_all_resources():
    case = _create(ROUTINE_MSG)
    for idx in range(len(case["resources"])):
        resp = client.post(
            f"/api/cases/{case['id']}/verify-resource", json={"index": idx}
        )
        assert resp.status_code == 200, resp.text
    resp = client.post(f"/api/cases/{case['id']}/approve")
    assert resp.status_code == 200, resp.text
    approved = resp.json()
    assert approved["state"] == "APPROVED_SENT"
    assert approved["approval_record"]["by"] == "navigator"
    # Second approve must fail.
    resp = client.post(f"/api/cases/{case['id']}/approve")
    assert resp.status_code == 409


def test_approve_escalated_fails_409():
    case = _create(CRISIS_MSG)
    resp = client.post(f"/api/cases/{case['id']}/approve")
    assert resp.status_code == 409


def test_edit_draft():
    case = _create(ROUTINE_MSG)
    resp = client.post(
        f"/api/cases/{case['id']}/edit",
        json={"reply": "Mensaje editado por la navegadora."},
    )
    assert resp.status_code == 200
    edited = resp.json()
    assert edited["draft"]["reply"] == "Mensaje editado por la navegadora."
    assert edited["navigator_edited"] is True


def test_ledger_has_demo_mode_entries():
    _create(ROUTINE_MSG)
    resp = client.get("/api/ledger")
    assert resp.status_code == 200
    body = resp.json()
    assert body["entries"], "ledger must not be empty"
    assert body["totals"]["calls"] >= 1
    demo_entries = [e for e in body["entries"] if e["model"] == "demo-mode"]
    assert demo_entries, "demo-mode runs must be flagged in the ledger"
    for entry in body["entries"]:
        for key in ("model", "tokens_in", "tokens_out", "est_cost_usd"):
            assert key in entry
