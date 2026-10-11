# Podrá Navega — Backend (app/)

FastAPI backend. The AI drafts; a human navigator reviews, edits,
verifies every resource, and approves before anything is sent.

## Run

From the **repo root**:

```bash
pip install -r requirements.txt   # managed at repo root
uvicorn app.main:app --reload --port 8000
```

- No `NEBIUS_API_KEY` set → **demo mode**: the whole flow runs
  end-to-end with deterministic rule-based drafting, every response is
  flagged `demo_mode: true`, and ledger entries use model `"demo-mode"`.
  Nothing crashes for a missing key.
- With `NEBIUS_API_KEY` set → live Nebius Token Factory calls
  (OpenAI-compatible API, `https://api.tokenfactory.nebius.com/v1/`).
  If a live call fails, that step degrades to the deterministic response
  and the ledger records the fallback.

Static frontend (built by another front) belongs in `app/static/` and is
not part of this backend package.

## Model routing (token_factory.py)

Model IDs below are the exact strings returned by `GET /v1/models` —
live-verified Oct 11, 2026. Casing matters (notably the Nano ID).

| Step | Model | Job |
|---|---|---|
| Draft reply | Super `nvidia/nemotron-3-super-120b-a12b` | Plain-language reply in the patient's language |
| English gloss | Nano `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | Faithful English rendering so non-Spanish judges can verify |
| Barrier audit | Ultra `nvidia/Nemotron-3-Ultra-550b-a55b` | ONE pass on condensed context: audit the case against the barrier taxonomy |

Every call appends to the cost ledger (model, tokens in/out, estimated
USD at Ultra $1/$3, Super $0.30/$0.90, Nano $0.06/$0.24 per 1M tokens).

The question list is an **approved template**, not free-generated text —
deliberate safety design. Medical content in drafts is information /
preparation only, from fixed approved templates in `barriers.py`.

## Workflow

```
RECEIVED -> DRAFTED -> PENDING_APPROVAL -> APPROVED_SENT
RECEIVED -> ESCALATED     (crisis / medical_advice / sensitive)
```

Safety routing happens **before** drafting. Classification comes from
the sibling `safety` package (`safety/classifier.py`,
`classify_message(text) -> {category, escalate, reason}`) when
importable; otherwise a minimal keyword fallback in
`app/safety_fallback.py` is used. Crisis / medical-advice cases go
straight to ESCALATED and **no draft is generated**.

Approval is enforced server-side (not just in the UI):

- ESCALATED case → `409`
- Case not in `PENDING_APPROVAL` → `409`
- Any attached resource still `verified: false` → `409`

## Resource verification (Tavily) — `tavily_verify.py`

Verifying a resource is a real check, not a checkbox ritual, and the
app labels honestly which check actually ran:

- **`TAVILY_API_KEY` set** → the verify call runs a Tavily *search*
  restricted to the resource's own domain. A matching result marks the
  resource verified and stores `verified_via: "tavily"`, a `checked_at`
  timestamp, and an `evidence` snippet (result title + text) on the
  resource. If Tavily answers but finds no matching source, the
  resource stays **unverified** with the "Not found" evidence stored —
  approval stays blocked. Search (not extract) is used because the
  question is "does this source exist on the live web and what does it
  say?" — search confirms it in Tavily's live index and returns the
  evidence snippet without fetching whole pages.
- **Tavily unreachable** (network/HTTP error) → the navigator's manual
  verification stands, labeled `verified_via: "local_cache"` with an
  evidence note saying the Tavily check was unavailable. An outage can
  never kill the demo, and the label never fakes a Tavily verdict.
- **No key (demo mode)** → no network call; the navigator's manual
  verification against the local directory is labeled
  `verified_via: "local_cache"`.

Verdicts from completed Tavily calls are cached in memory per
`source_url`: a case attaches at most 3 resources, so verification
costs **at most 3 Tavily calls per case**, and repeat verifications of
the same URL — in this case or later ones — are free. Transport errors
are not cached, so a retry can succeed. `GET /api/health` reports
`tavily_enabled`. The frontend badge shows the source ("Verified via
Tavily · <time>" vs. "Verified · Local list").

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Status, demo_mode flag, model IDs |
| POST | `/api/cases` | Create a case from a patient message (ES or EN): `{message, language?}` |
| GET | `/api/cases` | List all cases |
| GET | `/api/cases/{id}` | One case (draft, barriers, resources, history) |
| POST | `/api/cases/{id}/edit` | Navigator edits the draft: `{reply?, reply_en?, question_list?}` |
| POST | `/api/cases/{id}/verify-resource` | Verify one resource: `{index}` — Tavily check when a key is set (a "not found" leaves it unverified), else navigator verification labeled `local_cache` |
| POST | `/api/cases/{id}/approve` | Approve + send (409 while anything is unverified or case is escalated) |
| GET | `/api/ledger` | All token/cost ledger entries + totals |

## Data

- In-memory store (`store.py`), seeded with ONE golden fictional case
  (`CASE-0001`, the biopsy/transport example) whose ledger entry is a
  $0 replay (`model="demo-mode"`, 0 tokens).
- All patient data is fictional; cases use case IDs, never names.
- Barrier taxonomy (`barriers.py`): transport, cost, childcare,
  work_schedule, fear, language, health_literacy, other — each finding
  carries an evidence quote from the patient's message.
- Resources come from a sample directory and start **unverified**;
  approval stays blocked until the navigator verifies each one.

## Tests

```bash
python -m pytest app/test_main.py app/test_tavily.py -v
```

`test_main.py` covers: health, golden-case seed, crisis → ESCALATED
with no draft, medical-advice → ESCALATED with no draft, routine →
draft + barriers, approve blocked (409) with an unverified resource,
approve succeeds after verifying all resources, edit, and ledger
entries.

`test_tavily.py` covers resource verification with the Tavily HTTP
call mocked (no network, no real key): a mocked Tavily hit marks
`verified_via: "tavily"` and stores `checked_at` (and repeat verifies
hit the cache, not the API); with no key the label is `local_cache`;
a Tavily "not found" keeps the resource unverified; and approval
stays blocked until every resource is verified.
