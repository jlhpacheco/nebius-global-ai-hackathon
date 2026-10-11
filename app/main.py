"""Podrá Navega — FastAPI backend (B1).

Workflow (state machine):

    RECEIVED -> DRAFTED -> PENDING_APPROVAL -> APPROVED_SENT
    RECEIVED -> ESCALATED            (crisis / medical-advice / sensitive)

Safety routing happens BEFORE drafting: a case classified crisis or
medical_advice (or flagged escalate by the safety classifier) goes
straight to ESCALATED and NO draft is generated.

Approval is enforced SERVER-SIDE: POST /approve fails with 409 when the
case is ESCALATED, when it is not PENDING_APPROVAL, or while ANY resource
attached to the draft is still unverified. The navigator verifies each
resource via POST /verify-resource.

Run from the repo root:  uvicorn app.main:app
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Make the repo root importable so the sibling `safety` package resolves
# whether uvicorn is launched from the repo root or elsewhere.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from . import barriers as barriers_mod  # noqa: E402
from . import token_factory  # noqa: E402
from .safety_fallback import classify_message_fallback  # noqa: E402
from .store import STORE  # noqa: E402

app = FastAPI(
    title="Podrá Navega",
    description="Bilingual cancer-navigation copilot for Latinas Contra "
                "Cancer. The AI drafts; a human navigator reviews, "
                "edits, verifies resources, and approves before "
                "anything is sent. Fictional demo data only.",
    version="0.1.0",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Safety classification: real safety package if importable, else fallback
# ---------------------------------------------------------------------------

def classify(text: str) -> dict:
    try:
        from safety.classifier import classify_message

        result = classify_message(text)
        return {
            "category": result["category"],
            "escalate": bool(result["escalate"]),
            "reason": result["reason"],
            "source": "safety-package",
        }
    except Exception:
        result = classify_message_fallback(text)
        return {**result, "source": "fallback"}


# ---------------------------------------------------------------------------
# Pipeline: drafting (Nano/Super) + ONE Ultra barrier-audit pass
# ---------------------------------------------------------------------------

def _parse_barrier_audit(raw: str, rule_findings: list[dict]) -> list[dict]:
    """Parse Ultra's JSON barrier audit; fall back to rule findings."""
    try:
        data = json.loads(raw)
        items = data.get("barriers_found", [])
        parsed = []
        for item in items:
            name = item.get("barrier")
            if name in barriers_mod.BARRIER_TAXONOMY:
                parsed.append(
                    {"barrier": name, "evidence": str(item.get("evidence", ""))[:300]}
                )
        if parsed:
            return parsed
    except Exception:
        pass
    return rule_findings


def run_pipeline(case: dict) -> dict:
    """Draft a reply and run the barrier audit for a routine case.

    Every model step goes through token_factory.chat, which in demo mode
    (no NEBIUS_API_KEY) uses the deterministic rule-based responses and
    still writes ledger entries with model="demo-mode".
    """
    text = case["patient_message"]
    language = case["language"]
    rule_findings = barriers_mod.detect_barriers(text)
    demo_draft = barriers_mod.draft_reply(text, language, rule_findings)

    # Step 1 (Super): plain-language draft reply in the patient's language.
    reply = token_factory.chat(
        stage="draft_reply",
        model_key="super",
        messages=[
            {
                "role": "system",
                "content": "You draft plain-language replies for a cancer "
                           "patient navigator program. Information and "
                           "preparation only: never diagnose, never "
                           "recommend treatment or medication. Short "
                           "sentences. The draft will be reviewed by a "
                           "human navigator before it is sent.",
            },
            {"role": "user", "content": text},
        ],
        case_id=case["id"],
        demo_response=demo_draft["reply"],
    )

    # Step 2 (Nano): English gloss of the draft, so non-Spanish-speaking
    # judges/navigators can verify fidelity live.
    gloss = token_factory.chat(
        stage="draft_gloss_en",
        model_key="nano",
        messages=[
            {
                "role": "system",
                "content": "Translate the draft reply to plain English, "
                           "faithfully, sentence by sentence.",
            },
            {"role": "user", "content": reply},
        ],
        case_id=case["id"],
        demo_response=demo_draft["reply_en"],
    )

    # Step 3 (Ultra, ONE pass, condensed context only): barrier audit
    # against the full taxonomy — hunting barriers the patient did NOT
    # necessarily mention directly.
    audit_prompt = json.dumps(
        {
            "patient_message": text,
            "draft_reply": reply,
            "taxonomy": barriers_mod.BARRIER_TAXONOMY,
            "rule_findings": rule_findings,
            "instruction": "Audit this case against the barrier taxonomy. "
                           "Return JSON: {\"barriers_found\": [{\"barrier\": "
                           "<taxonomy name>, \"evidence\": \"<exact quote "
                           "from the patient message>\"}]}. Only barriers "
                           "with evidence in the message.",
        },
        ensure_ascii=False,
    )
    audit_raw = token_factory.chat(
        stage="barrier_audit",
        model_key="ultra",
        messages=[
            {
                "role": "system",
                "content": "You are the barrier-audit pass for a patient "
                           "navigation case. Respond with JSON only.",
            },
            {"role": "user", "content": audit_prompt},
        ],
        case_id=case["id"],
        demo_response=json.dumps(
            {"barriers_found": rule_findings}, ensure_ascii=False
        ),
    )
    found = _parse_barrier_audit(audit_raw, rule_findings)

    draft = {
        "reply": reply,
        "reply_en": gloss,
        # The question list is an approved template (see barriers.py),
        # not free-generated text — intentional safety design.
        "question_list": demo_draft["question_list"],
        "question_list_en": demo_draft["question_list_en"],
    }
    case["draft"] = draft
    case["barriers_found"] = found
    case["barrier_checklist"] = {
        name: any(b["barrier"] == name for b in found)
        for name in barriers_mod.BARRIER_TAXONOMY
    }
    case["resources"] = barriers_mod.resources_for(found)
    return case


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class CreateCaseRequest(BaseModel):
    message: str
    language: str | None = None


class EditRequest(BaseModel):
    reply: str | None = None
    reply_en: str | None = None
    question_list: list[str] | None = None


class VerifyResourceRequest(BaseModel):
    index: int


class ApproveRequest(BaseModel):
    # Optional: the demo's approver is a clearly labeled synthetic
    # persona (see docs/DECISION-synthetic-navigator.md). Defaults to
    # the generic "navigator" when not supplied.
    navigator_name: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "podra-navega",
        "demo_mode": token_factory.is_demo_mode(),
        "models": token_factory.MODELS,
        "time": _now(),
    }


@app.post("/api/cases", status_code=201)
def create_case(req: CreateCaseRequest) -> dict:
    text = req.message.strip()
    if not text:
        raise HTTPException(status_code=422, detail="message must not be empty")
    language = req.language or barriers_mod.detect_language(text)
    case_id = STORE.next_id()
    now = _now()

    safety = classify(text)
    case = {
        "id": case_id,
        "created_at": now,
        "updated_at": now,
        "fictional": True,
        "language": language,
        "patient_message": text,
        "safety": safety,
        "state": "RECEIVED",
        "state_history": [{"state": "RECEIVED", "at": now}],
        "draft": None,
        "barriers_found": [],
        "barrier_checklist": {
            name: False for name in barriers_mod.BARRIER_TAXONOMY
        },
        "resources": [],
        "approval_record": None,
        "navigator_edited": False,
        "demo_mode": token_factory.is_demo_mode(),
    }

    escalate = safety["escalate"] or safety["category"] in (
        "crisis",
        "medical_advice",
    )
    if escalate:
        # Safety routing BEFORE drafting: no draft is generated, ever.
        case["state"] = "ESCALATED"
        case["state_history"].append({"state": "ESCALATED", "at": _now()})
        return STORE.add(case)

    case = run_pipeline(case)
    case["state_history"].append({"state": "DRAFTED", "at": _now()})
    case["state"] = "PENDING_APPROVAL"
    case["state_history"].append({"state": "PENDING_APPROVAL", "at": _now()})
    return STORE.add(case)


@app.get("/api/cases")
def list_cases() -> list[dict]:
    return STORE.list()


@app.get("/api/cases/{case_id}")
def get_case(case_id: str) -> dict:
    case = STORE.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    return case


@app.post("/api/cases/{case_id}/edit")
def edit_case(case_id: str, req: EditRequest) -> dict:
    case = STORE.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    if case["state"] == "ESCALATED":
        raise HTTPException(
            status_code=409,
            detail="case is ESCALATED: there is no draft to edit; "
                   "a human navigator handles this case directly",
        )
    if case["state"] != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=f"case in state {case['state']} cannot be edited",
        )
    if req.reply is not None:
        case["draft"]["reply"] = req.reply
    if req.reply_en is not None:
        case["draft"]["reply_en"] = req.reply_en
    if req.question_list is not None:
        case["draft"]["question_list"] = req.question_list
    case["navigator_edited"] = True
    return STORE.update(case)


@app.post("/api/cases/{case_id}/verify-resource")
def verify_resource(case_id: str, req: VerifyResourceRequest) -> dict:
    case = STORE.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    if req.index < 0 or req.index >= len(case["resources"]):
        raise HTTPException(status_code=404, detail="resource index out of range")
    case["resources"][req.index]["verified"] = True
    case["resources"][req.index]["verified_at"] = _now()
    return STORE.update(case)


@app.post("/api/cases/{case_id}/approve")
def approve_case(case_id: str, req: ApproveRequest | None = None) -> dict:
    case = STORE.get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    if case["state"] == "ESCALATED":
        raise HTTPException(
            status_code=409,
            detail="case is ESCALATED: escalated cases are handled by a "
                   "human navigator directly and cannot be approved/sent "
                   "by the system",
        )
    if case["state"] != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=f"case in state {case['state']} cannot be approved",
        )
    unverified = [r for r in case["resources"] if not r.get("verified")]
    if unverified:
        names = "; ".join(r["name"] for r in unverified)
        raise HTTPException(
            status_code=409,
            detail=f"approval blocked: {len(unverified)} unverified "
                   f"resource(s) must be verified first: {names}",
        )
    case["state"] = "APPROVED_SENT"
    case["state_history"].append({"state": "APPROVED_SENT", "at": _now()})
    case["approval_record"] = {
        "by": (req.navigator_name if req and req.navigator_name else "navigator"),
        "at": _now(),
        "navigator_edited": case["navigator_edited"],
        "resources_verified": len(case["resources"]),
    }
    return STORE.update(case)


@app.get("/api/ledger")
def ledger() -> dict:
    return {
        "entries": token_factory.LEDGER.entries(),
        "totals": token_factory.LEDGER.totals(),
    }


# ---------------------------------------------------------------------------
# Static frontend — mounted LAST, after every /api route, so the API
# always wins and `uvicorn app.main:app` serves the whole demo.
# ---------------------------------------------------------------------------

_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(_STATIC_DIR):
    app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")
