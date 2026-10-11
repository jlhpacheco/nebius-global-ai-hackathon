"""Tavily-backed resource verification.

When a navigator verifies a resource, this module checks the resource
against the live web via the Tavily API — but ONLY when a real
``TAVILY_API_KEY`` is set. Honest-labeling rule (Fix #5): the app never
claims Tavily verification it did not perform.

- Key set, Tavily confirms the source -> ``verified_via="tavily"`` with
  ``checked_at`` and an evidence snippet (result title + text).
- Key set, Tavily answers but finds no matching source -> the resource
  stays UNVERIFIED (``verified=False``), with ``verified_via="tavily"``,
  ``checked_at``, and an evidence note. Approval stays blocked, exactly
  as the gate requires.
- Key set, Tavily unreachable (network/HTTP error) -> the navigator's
  manual verification stands, labeled ``verified_via="local_cache"``
  with an evidence note saying the Tavily check was unavailable. The
  demo can never be killed by a Tavily outage, and the label never
  lies about which check actually happened.
- No key (demo mode) -> ``verified_via="local_cache"``: the navigator
  verified the resource against the local sample directory. No network
  call is made.

Why Tavily *search* and not *extract*: verification asks "does this
organization/page exist on the live web, and what does it say?" Search
confirms the source is present in Tavily's live index and returns a
title + snippet — exactly the evidence the verified-referral badge
needs — without fetching and parsing whole pages (extract is heavier
and fails on JS-heavy sites). The query is restricted to the
resource's own domain, so a match means Tavily found that actual
source, not a namesake.

Caching: verdicts from completed Tavily calls are cached in memory per
``source_url``. A case attaches at most 3 resources, so verification
costs at most 3 Tavily calls per case — and repeat verifications of the
same URL (same case or later cases) cost nothing. Transport errors are
NOT cached, so a retry can succeed once Tavily is reachable again.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
_TIMEOUT_SECONDS = 10.0
_MAX_RESULTS = 3

# source_url -> verdict dict (only completed Tavily verdicts are cached)
_cache: dict[str, dict] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def tavily_enabled() -> bool:
    """True when a Tavily API key is configured (checked at call time)."""
    return bool(os.environ.get("TAVILY_API_KEY"))


def clear_cache() -> None:
    """Drop all cached verdicts (used by tests)."""
    _cache.clear()


def _domain(url: str) -> str:
    netloc = urlparse(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _query_for(resource: dict) -> str:
    """Search query from the resource name, minus the sample-directory
    marker the demo directory appends to its entries."""
    name = re.sub(r"\s*\([^)]*\)\s*$", "", resource.get("name", "")).strip()
    return name or resource.get("source_url", "")


def _tavily_search(query: str, domain: str) -> list[dict]:
    """One Tavily search call restricted to the resource's domain.

    Isolated as its own function so tests can monkeypatch it — no test
    ever touches the real network. Raises on transport/HTTP errors;
    the caller decides the fallback.
    """
    response = httpx.post(
        TAVILY_SEARCH_URL,
        headers={
            "Authorization": f"Bearer {os.environ['TAVILY_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "search_depth": "basic",
            "max_results": _MAX_RESULTS,
            "include_domains": [domain] if domain else [],
        },
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("results", []) or []


def _match(results: list[dict], source_url: str) -> dict | None:
    """Return the first result that is actually the resource's source:
    same normalized domain (or the exact URL)."""
    target = _domain(source_url)
    for result in results:
        url = result.get("url", "")
        if url and (url.startswith(source_url) or _domain(url) == target):
            return result
    return None


def verify_resource(resource: dict) -> dict:
    """Verify one resource. Returns::

        {"verified": bool,
         "verified_via": "tavily" | "local_cache",
         "checked_at": ISO timestamp | None,
         "evidence": str | None}

    ``verified`` is the verdict the caller should store: with a Tavily
    key it is Tavily's verdict; without one (or when Tavily is
    unreachable) it is the navigator's own attestation against the
    local directory, and ``verified_via`` says so honestly.
    """
    source_url = resource.get("source_url", "")

    if not tavily_enabled():
        return {
            "verified": True,
            "verified_via": "local_cache",
            "checked_at": None,
            "evidence": None,
        }

    if source_url in _cache:
        return dict(_cache[source_url])

    domain = _domain(source_url)
    try:
        results = _tavily_search(_query_for(resource), domain)
    except Exception as exc:  # Tavily unreachable: never fake its verdict
        return {
            "verified": True,
            "verified_via": "local_cache",
            "checked_at": None,
            "evidence": "Tavily check unavailable "
                        f"({type(exc).__name__}); verified by the "
                        "navigator against the local directory.",
        }

    checked_at = _now()
    hit = _match(results, source_url)
    if hit is not None:
        title = (hit.get("title") or "").strip()
        snippet = (hit.get("content") or "").strip()
        evidence = " — ".join(p for p in (title, snippet) if p)[:300]
        verdict = {
            "verified": True,
            "verified_via": "tavily",
            "checked_at": checked_at,
            "evidence": evidence or hit.get("url", ""),
        }
    else:
        verdict = {
            "verified": False,
            "verified_via": "tavily",
            "checked_at": checked_at,
            "evidence": "Not found: Tavily search returned no result "
                       f"on {domain or source_url} for this resource.",
        }
    if source_url:
        _cache[source_url] = verdict
    return dict(verdict)
