"""Vault-surrogate transport for Nebius Token Factory (headless use).

Why this exists: the live app path (token_factory._get_client) needs the
raw key in env NEBIUS_API_KEY. On this machine the key lives ONLY in the
Secure Vault as the connector `custom.nebius-token-factory` — no raw
value exists to put in an env var, by design. This module performs the
same chat-completion call through the vault's dynamic-credential
surrogate helper (the same mechanism as the nebius-token-factory skill
CLI): the request carries only an `hsurr:*` surrogate, swapped for the
real key on egress, and only to api.tokenfactory.nebius.com.

token_factory.chat() uses this transport ONLY when the env flag
PODRA_TF_TRANSPORT=surrogate is set. With the flag unset, behavior is
exactly as before (demo mode / OpenAI client). Nothing here prints,
logs, or persists any credential or surrogate value.
"""

from __future__ import annotations

import json
import sys
import urllib.request

_HELPER_DIR = "/opt/hatch/skills/skill-creator/bin"
if _HELPER_DIR not in sys.path:
    sys.path.insert(0, _HELPER_DIR)

from dynamic_credentials import (  # noqa: E402
    add_surrogate_to_request,
    read_json_response,
)

CREDENTIAL_NAME = "custom.nebius-token-factory"
ALLOWED_HOSTS = ["api.tokenfactory.nebius.com"]
CHAT_URL = "https://api.tokenfactory.nebius.com/v1/chat/completions"


def surrogate_chat(
    *,
    model: str,
    messages: list[dict],
    temperature: float = 0.2,
    max_tokens: int = 900,
) -> tuple[str, int, int]:
    """One chat completion via the vault surrogate.

    Returns (text, prompt_tokens, completion_tokens) with token counts
    taken from the response usage block (0 when absent). Raises on any
    transport/auth failure — the caller (token_factory.chat) degrades to
    its deterministic fallback and records a fallback ledger entry.
    """
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        CHAT_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "podra-navega-eval",
        },
        method="POST",
    )
    add_surrogate_to_request(
        req, CREDENTIAL_NAME, allowed_hosts=ALLOWED_HOSTS
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = read_json_response(resp)
    choices = payload.get("choices") or []
    text = ""
    if choices:
        text = (choices[0].get("message", {}).get("content") or "").strip()
    usage = payload.get("usage") or {}
    return (
        text,
        int(usage.get("prompt_tokens") or 0),
        int(usage.get("completion_tokens") or 0),
    )
