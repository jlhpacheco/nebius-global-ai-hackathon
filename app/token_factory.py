"""Nebius Token Factory client + token/cost ledger for Podrá Navega.

Design rules (from ARCHITECTURE.md and the red-team fixes):

- Token Factory only. OpenAI-compatible API at
  https://api.tokenfactory.nebius.com/v1/ with the key in env NEBIUS_API_KEY.
- Model routing: Nano / Super do the volume work (drafts, glosses);
  Ultra is rationed to ONE hard pass per case (the barrier audit).
- EVERY call appends to the ledger: model, tokens in/out, estimated cost.
  Prices (per 1M tokens, in/out): Ultra $1.00/$3.00, Super $0.30/$0.90,
  Nano $0.06/$0.24.
- DEMO MODE: if NEBIUS_API_KEY is not set, no network call is made. The
  caller supplies a deterministic rule-based ``demo_response`` which is
  used verbatim, and the ledger entry is recorded with model="demo-mode"
  and estimated token counts. The full flow therefore runs at $0 with no
  key and never crashes for a missing key.
"""

from __future__ import annotations

import os
import threading
from datetime import datetime, timezone

BASE_URL = "https://api.tokenfactory.nebius.com/v1/"

# Exact IDs as returned by GET /v1/models — live-verified Oct 11, 2026.
# Casing matters: the Nano ID is NOT the lowercase form used in blogs.
MODELS = {
    "nano": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
    "super": "nvidia/nemotron-3-super-120b-a12b",
    "ultra": "nvidia/Nemotron-3-Ultra-550b-a55b",
}

# USD per 1M tokens: (input, output)
PRICES = {
    MODELS["nano"]: (0.06, 0.24),
    MODELS["super"]: (0.30, 0.90),
    MODELS["ultra"]: (1.00, 3.00),
    "demo-mode": (0.0, 0.0),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def estimate_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token) used only in demo mode."""
    return max(1, len(text) // 4)


def est_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    price_in, price_out = PRICES.get(model, (0.0, 0.0))
    return round(tokens_in / 1_000_000 * price_in + tokens_out / 1_000_000 * price_out, 6)


class Ledger:
    """In-memory token/cost ledger. Every model call appends one entry."""

    def __init__(self) -> None:
        self._entries: list[dict] = []
        self._lock = threading.Lock()

    def append(
        self,
        *,
        case_id: str,
        stage: str,
        model: str,
        tokens_in: int,
        tokens_out: int,
        demo_mode: bool,
    ) -> dict:
        entry = {
            "ts": _now(),
            "case_id": case_id,
            "stage": stage,
            "model": model,
            "tokens_in": int(tokens_in),
            "tokens_out": int(tokens_out),
            "est_cost_usd": est_cost(model, tokens_in, tokens_out),
            "demo_mode": bool(demo_mode),
        }
        with self._lock:
            self._entries.append(entry)
        return entry

    def entries(self) -> list[dict]:
        with self._lock:
            return list(self._entries)

    def totals(self) -> dict:
        entries = self.entries()
        return {
            "calls": len(entries),
            "tokens_in": sum(e["tokens_in"] for e in entries),
            "tokens_out": sum(e["tokens_out"] for e in entries),
            "est_cost_usd": round(sum(e["est_cost_usd"] for e in entries), 6),
        }


LEDGER = Ledger()

_client = None
_client_lock = threading.Lock()


def is_demo_mode() -> bool:
    """Demo mode is ON whenever no Token Factory key is configured."""
    return not os.environ.get("NEBIUS_API_KEY")


def transport_mode() -> str:
    """Optional alternate transport, env-gated (default: off).

    "surrogate" routes chat() through app.surrogate_transport — the
    vault-backed path used by the headless live eval, where the key
    exists only as a Secure Vault connector and no raw NEBIUS_API_KEY
    is available. Any other value (including unset) keeps the standard
    behavior: demo mode with no key, OpenAI client with one.
    """
    return os.environ.get("PODRA_TF_TRANSPORT", "").strip().lower()


def _get_client():
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                from openai import OpenAI  # imported lazily; not needed in demo mode

                _client = OpenAI(
                    base_url=BASE_URL,
                    api_key=os.environ["NEBIUS_API_KEY"],
                )
    return _client


def chat(
    *,
    stage: str,
    model_key: str,
    messages: list[dict],
    case_id: str,
    demo_response: str,
    temperature: float = 0.2,
    max_tokens: int = 900,
) -> str:
    """Run one chat completion through Token Factory, or demo mode.

    In demo mode (no key) — or if the live call fails for any reason —
    ``demo_response`` (deterministic, rule-based, produced by the caller)
    is returned and the ledger entry is recorded with model="demo-mode".
    A missing key NEVER raises.
    """
    prompt_text = "\n".join(m.get("content", "") for m in messages)

    if transport_mode() == "surrogate":
        # Vault-surrogate transport (headless eval path). Same ledger
        # contract as the live client path; same degrade-to-demo
        # behavior on any failure.
        model = MODELS[model_key]
        try:
            from . import surrogate_transport

            text, s_tokens_in, s_tokens_out = surrogate_transport.surrogate_chat(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            LEDGER.append(
                case_id=case_id,
                stage=stage,
                model=model,
                tokens_in=s_tokens_in or estimate_tokens(prompt_text),
                tokens_out=s_tokens_out or estimate_tokens(text),
                demo_mode=False,
            )
            return text or demo_response
        except Exception:
            LEDGER.append(
                case_id=case_id,
                stage=stage + ":fallback",
                model="demo-mode",
                tokens_in=estimate_tokens(prompt_text),
                tokens_out=estimate_tokens(demo_response),
                demo_mode=True,
            )
            return demo_response

    if is_demo_mode():
        LEDGER.append(
            case_id=case_id,
            stage=stage,
            model="demo-mode",
            tokens_in=estimate_tokens(prompt_text),
            tokens_out=estimate_tokens(demo_response),
            demo_mode=True,
        )
        return demo_response

    model = MODELS[model_key]
    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = (resp.choices[0].message.content or "").strip()
        usage = getattr(resp, "usage", None)
        tokens_in = getattr(usage, "prompt_tokens", None) or estimate_tokens(prompt_text)
        tokens_out = getattr(usage, "completion_tokens", None) or estimate_tokens(text)
        LEDGER.append(
            case_id=case_id,
            stage=stage,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            demo_mode=False,
        )
        return text or demo_response
    except Exception:
        # Live call failed (network, bad key, model id). Degrade to the
        # deterministic response rather than failing the case workflow.
        LEDGER.append(
            case_id=case_id,
            stage=stage + ":fallback",
            model="demo-mode",
            tokens_in=estimate_tokens(prompt_text),
            tokens_out=estimate_tokens(demo_response),
            demo_mode=True,
        )
        return demo_response
