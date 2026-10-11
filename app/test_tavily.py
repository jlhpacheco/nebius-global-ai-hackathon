"""Tests for Tavily-backed resource verification (app/tavily_verify.py).

No real network, no real key: the Tavily search function is
monkeypatched, and TAVILY_API_KEY is set/unset per test.

Run from the repo root:
    python -m pytest app/test_tavily.py -v
"""

import os
import sys

# Demo mode for the Nebius side: deterministic drafting, no live calls.
os.environ.pop("NEBIUS_API_KEY", None)

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import tavily_verify  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)

ROUTINE_MSG = (
    "Me dijeron que necesito una biopsia y no entiendo, "
    "y no tengo transporte."
)


@pytest.fixture(autouse=True)
def _clean_tavily_state(monkeypatch):
    """Each test starts with an empty verdict cache and no key; tests
    opt into a key explicitly. Monkeypatch undoes env changes after."""
    tavily_verify.clear_cache()
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    yield
    tavily_verify.clear_cache()


def _create(message: str = ROUTINE_MSG) -> dict:
    resp = client.post("/api/cases", json={"message": message})
    assert resp.status_code == 201, resp.text
    return resp.json()


def _verify(case_id: str, index: int) -> dict:
    resp = client.post(
        f"/api/cases/{case_id}/verify-resource", json={"index": index}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _fake_search_factory(calls: list):
    """A fake Tavily search that 'finds' every domain it is asked
    about, returning a result on that domain."""
    def fake_search(query: str, domain: str) -> list[dict]:
        calls.append(domain)
        return [
            {
                "title": f"{domain} — official page",
                "url": f"https://{domain}/verified-page",
                "content": "Live listing confirmed by fake Tavily search.",
            }
        ]
    return fake_search


def test_verify_resource_via_tavily(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key-not-real")
    calls: list = []
    monkeypatch.setattr(
        tavily_verify, "_tavily_search", _fake_search_factory(calls)
    )

    case = _create()
    updated = _verify(case["id"], 0)
    resource = updated["resources"][0]
    assert resource["verified"] is True
    assert resource["verified_via"] == "tavily"
    assert resource["checked_at"]  # a real check time was stored
    assert "official page" in resource["evidence"]

    # Cache: verifying the same source URL again (from a second case)
    # costs no additional Tavily call.
    assert len(calls) == 1
    case2 = _create()
    url2 = case2["resources"][0]["source_url"]
    assert url2 == case["resources"][0]["source_url"]
    updated2 = _verify(case2["id"], 0)
    assert updated2["resources"][0]["verified_via"] == "tavily"
    assert len(calls) == 1, "cached verdict must not re-call Tavily"


def test_verify_resource_local_cache_without_key():
    case = _create()
    updated = _verify(case["id"], 0)
    resource = updated["resources"][0]
    assert resource["verified"] is True
    assert resource["verified_via"] == "local_cache"
    assert "checked_at" not in resource  # no live check happened


def test_tavily_not_found_keeps_resource_unverified(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key-not-real")
    monkeypatch.setattr(
        tavily_verify, "_tavily_search", lambda query, domain: []
    )

    case = _create()
    updated = _verify(case["id"], 0)
    resource = updated["resources"][0]
    assert resource["verified"] is False
    assert resource["verified_via"] == "tavily"
    assert resource["checked_at"]
    assert "Not found" in resource["evidence"]
    # And the approval gate still blocks.
    resp = client.post(f"/api/cases/{case['id']}/approve")
    assert resp.status_code == 409


def test_approval_blocked_until_all_verified_with_tavily(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key-not-real")
    calls: list = []
    monkeypatch.setattr(
        tavily_verify, "_tavily_search", _fake_search_factory(calls)
    )

    case = _create()
    # Nothing verified yet -> blocked.
    resp = client.post(f"/api/cases/{case['id']}/approve")
    assert resp.status_code == 409

    # Verify all but one -> still blocked.
    for idx in range(len(case["resources"]) - 1):
        _verify(case["id"], idx)
    resp = client.post(f"/api/cases/{case['id']}/approve")
    assert resp.status_code == 409

    # Verify the last one -> approval goes through.
    _verify(case["id"], len(case["resources"]) - 1)
    resp = client.post(f"/api/cases/{case['id']}/approve")
    assert resp.status_code == 200, resp.text
    assert resp.json()["state"] == "APPROVED_SENT"
