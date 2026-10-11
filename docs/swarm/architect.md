# TECHNICAL ARCHITECT REPORT — Nebius x NVIDIA Hackathon

Lesson read from the Lyceum and one appended at the end (hosting expiry vs. judging window).

## 0. The reference architecture any winning entry should use

```
Browser (single polished page, no build step)
  → FastAPI app (ONE deploy unit: UI + API in one process)
    → 1. INGEST: extract + chunk locally (free, no LLM tokens)
    → 2. TRIAGE + PER-CHUNK WORK: Nemotron Nano / 3.5-Lightning (cheap, reasoning OFF)
    → 3. TAVILY: max 3 functional searches, results change the output visibly
    → 4. ONE HARD STEP: Nemotron 3 Ultra, fed CONDENSED intermediate results only (never raw input)
    → 5. VERIFY: Super checks output against sources, returns strict JSON
  → Result cache keyed by input hash (repeat runs = $0)
  → "Replay golden sample" is the default demo path; Live mode is rate-limited
```

Five design rules that follow from the constraints: (a) Ultra never sees raw documents — only summaries; (b) every LLM call logs tokens + cost to a visible ledger (this is also judging evidence for Technological Implementation); (c) strict JSON (`response_format: json_schema`) + pydantic validation on every model output, one retry, then degrade a tier instead of failing; (d) the app is **stateless** — no database that can expire mid-judging; (e) day 1 includes a committed `verify_models.py` that calls `GET /v1/models` — model-ID casing in public repos is inconsistent (`nvidia/Nemotron-3-Ultra-550b-a55b` vs lowercase forms), so IDs are confirmed against the live API, never copied from a blog.

## 1. Framework choice

| Option | Build speed | "Complete product" Design score | Verdict |
|---|---|---|---|
| **FastAPI + one static HTML/CSS front end** (Tailwind via CDN, vanilla JS/HTMX, no build step) | Medium — ~30% more code than Streamlit | **Highest.** Full control of branding, layout, loading states, cost ledger, badges. Looks like a SaaS product, not a notebook | **RECOMMENDED** |
| Streamlit | Fastest; upload/chat/widgets built in; secrets built in | Weakest ceiling: rerun model makes multi-step pipelines awkward, default chrome reads as "demo" even skinned. Community Cloud free tier is ~1 GB RAM (secondary sources conflict: 1–2.7 GB) — PDF work can OOM | Fallback only if the build falls behind schedule by day 4 |
| Gradio | Fast for chat/agent UIs | Good for a pure chat agent, poor for a document/product workflow; and its natural host (HF Spaces) is now pay-gated (see §4) | Only for a chat-first Personal AI shape |

## 2. Model routing + token-cost proof

Prices: Ultra **$1.00 in / $3.00 out per 1M** — verified on Nebius's official cookbook page (opened). Super **$0.30 / $0.90** and Nano **$0.06 / $0.24** — reported identically by three independent Token Factory projects' cost ledgers; *not* re-verified in the Nebius console, so the budget below holds even if Nano/Super prices are 3× higher.

Reference run = one 20-page document (~15k tokens of text):

| Step | Model | In / Out tokens | Cost |
|---|---|---|---|
| Triage, routing, query generation | Nano (reasoning off) | 2,000 / 200 | ~$0.0002 |
| Per-chunk summaries (6 chunks) | Super | 20,000 / 3,000 | ~$0.009 |
| Tavily (see §3) | — | 3 basic searches | 3 Tavily credits, $0 |
| **Synthesis (the one hard step)** | **Ultra** | **12,000 / 2,500** | **~$0.020** |
| Citation/claim verification | Super | 8,000 / 800 | ~$0.003 |
| **Total per live run** | | | **≈ $0.03–0.05** |

**$50 survival proof:** budget split enforced in code — dev/testing $15 (~300+ full runs at reference cost; in practice dev uses Super in Ultra's slot, ~$0.01/run, so 1,000+ runs), golden/video runs $5, **judging reserve $30 locked** behind rate limits. Even a hostile judging scenario — 200 live judge runs — costs ~$10. The real burn risk is not price, it's loops: hard caps on `max_tokens`, chunk count, Tavily calls/run, and a daily spend ceiling in the app itself. One observed trap from a public cost ledger: Super spends reasoning tokens on every call (median ~98, max hitting the 4,096 cap) — set reasoning off for routine calls or output budgets silently blow up.

## 3. Tavily — functional, not decorative

Verified from Tavily's official docs (opened): free Researcher tier = **1,000 credits/month, no card**; basic search = 1 credit, advanced = 2. Judging falls in December = a fresh 1,000.

The integration point that earns the $3,000 bonus honestly: **claim verification.** After synthesis, the app extracts externally checkable claims (organizations, regulations, deadlines, figures attributed outside the document) → fires ≤3 basic Tavily searches → Super compares returned snippets against the claims → the UI renders **Verified / Not found / Contradicted badges with source links**. Tavily output materially changes the product's output and is visible on camera in the video. Degrades gracefully (badges read "unverified") if Tavily is down or quota is spent. Cache results by query hash.

## 4. Hosting — verified vs. assumed

Requirement: free, and alive through **Dec 15** (end of judging), not just Oct 30.

| Host | Status | Facts |
|---|---|---|
| **Render Free — PRIMARY** | Verified from Render's official free-tier docs (via search summaries of render.com/docs/free) | 750 free instance-hours/month, 512 MB / 0.1 CPU, spins down after 15 min idle, ~1 min wake. **No persistent disk. Free Postgres expires 30 days after creation + 14-day grace, then deleted** — a DB created Oct 30 dies during judging. Hence: stateless design, no Render Postgres. |
| **Streamlit Community Cloud — MIRROR** | Secondary sources only, conflicting on RAM/sleep details | Free public apps, sleeps when idle, wakes on visit. Use as a backup URL in the README, not the primary. |
| **HF Spaces — DO NOT PLAN ON** | **Verified on HF's official docs (opened)** | Static Spaces are free, but Gradio/Docker Spaces now require a paid plan (PRO for personal accounts); free accounts get only up to 2 ZeroGPU Gradio Spaces. The old "free CPU Space" advice is stale. |
| **Fly.io — EXCLUDED as free** | Secondary sources, consistent | No free tier for new orgs (trial = 2 VM hours); cheapest always-on ≈ $2–5/mo. Only if the principal explicitly approves spend. |
| Nebius Serverless Endpoints | Not priced in this pass | Track text encourages it, but AI Cloud signup carries the known $25 card-charge gotcha from the earlier scout. Deprioritized; Token Factory API calls alone satisfy "runs on Nebius" per the rules. |

Survival tactics for the judging window: a free external uptime-ping (e.g., cron ping every ~10 min, Dec 1–15 only) to blunt spin-down; an honest "waking up — ~60 seconds" loading state so a cold start doesn't read as broken; two live URLs (Render + Streamlit mirror) in the Devpost submission.

## 5. PDF / document ingestion — cheapest reliable path

- **pypdf** (pure Python, permissive license) for text extraction; **pdfplumber** where table/layout structure matters. Both free, both fit in 512 MB for sane documents.
- Chunk by detected headings, else ~2,500-token windows with overlap; **retain page numbers through every chunk** — page-cited output is the cheapest Design/Impact differentiator available.
- Cap uploads (e.g., 50 pages / 10 MB) and state the cap in the UI.
- **Scanned PDFs are the kill path:** no OCR in the stack. Detect low-text pages, warn the user plainly, process what's extractable. (One project priced NVIDIA Nemotron-Parse on Token Factory at $0.002/page — single-source, unverified; treat as an optional upgrade, never a dependency.)
- Also accept paste-text and URL input (URL fetched via Tavily Extract, 1 credit per 5 URLs) — this rescues judges whose sample PDF is awkward.

## 6. Persistent memory (Personal AI track) — simplest credible approach

Skip vector databases entirely at demo scale. **Memory = Markdown files in a Git repo** (one file per memory/skill, YAML frontmatter: date, tags, source), read/written via the GitHub API:
- Survives every free-host wipe, is user-owned and inspectable (on-theme for "your data under your control"), versioned for free.
- Retrieval under ~500 memories: keyword/tag filter → Nano reranks candidates → top items enter context. No embeddings infrastructure to break.
- Skills are just Markdown instruction files the agent loads by name — exactly demonstrable in a 3-minute video.
- Ship the demo pre-seeded with sample memories so judges see recall in the first run, plus an export button (download the whole memory as a zip) to make the ownership claim concrete.
- On a sleeping free host, never claim "always-on": the honest, judge-safe framing is "wakes on demand, memory persists."

## 7. Candidate shapes rated against this architecture

| Shape | Fit | One-line verdict |
|---|---|---|
| **Document → cited brief (e.g., BoardBrief)** | ★★★★★ | Exercises every layer (ingest, routing, Tavily verification, Ultra synthesis, citations); cheapest to make look like a finished product |
| Personal AI assistant | ★★★★ | Needs the §6 memory layer; strong track fit, but differentiation is harder — every entrant has a chatbot; memory-as-files + skills is the edge |
| Research/verification agent | ★★★ | Tavily-native but the most crowded, generic shape; wins only with a narrow, named audience |
| Multi-agent debate/committee | ★★★ | Great video, weak impact story; token-hungry unless routing is brutal (Nano analysts, one Ultra call) |
| Coding agent | ★★ | Highest risk: safe code execution/sandboxing doesn't exist on a 512 MB free host; slow runs make bad demos. Avoid in 8–10 days |

## 8. Top 3 technical kill risks

1. **Public-demo credit drain (Nebius $50 + Tavily 1,000/mo).** Unauthenticated demo + bots + judge retries. *Mitigations:* golden-replay is the default path ($0/run), live mode rate-limited per IP/session, daily spend cap in code, Ultra fed condensed input only, Tavily capped at 3 cached searches/run.
2. **Dead or cold demo during Dec 1–15 judging.** Render spin-down (~1 min wake reads as "broken"), free-Postgres 30-day expiry, HF pay-gate surprises. *Mitigations:* stateless app (nothing to expire), judging-window ping schedule, explicit waking-up UI state, second-host mirror URL in the submission, calendar health-checks Dec 1, 8, 15.
3. **Model-layer instability.** Exact model-ID casing varies across public sources; structured outputs fail; reasoning tokens eat output budgets; Ultra latency on fat inputs. *Mitigations:* day-1 `GET /v1/models` verification script in the repo, JSON-schema + pydantic validation with one retry, automatic fallback Ultra → Super for the synthesis step (quality dip, not outage), Ultra input capped ≈15k tokens, reasoning off except on the Ultra step.

## 9. THE recommended stack — day-1 start list

1. **Python 3.12 + FastAPI + uvicorn**, one repo, one process.
2. **Front end:** single `index.html` + Tailwind CDN + vanilla JS (no Node, no build step).
3. **Models via `openai` Python SDK** pointed at Token Factory: Nano `nvidia/nemotron-3-nano-30b-a3b` (triage/chunks), Super `nvidia/nemotron-3-super-120b-a12b` (verify), Ultra `nvidia/Nemotron-3-Ultra-550b-a55b` (one synthesis call) — IDs confirmed day 1 by `verify_models.py` against `GET /v1/models`.
4. **Ingestion:** `pypdf` (+ `pdfplumber` if tables matter), heading-aware chunking, page numbers preserved.
5. **Tavily:** `tavily-python`, basic search only, ≤3 calls/run, query-hash cache, claim-verification badges in UI.
6. **State:** none on the server. Result cache = in-memory + input-hash; Personal AI memory (if that track) = Markdown files via GitHub API.
7. **Guards in code from day 1:** per-IP rate limit, daily spend ceiling, per-call token/cost ledger (shown in the UI footer — judges love it), replay mode serving a pre-computed golden run at $0.
8. **Deploy:** Render Free (primary) + Streamlit Community Cloud mirror; secrets as host env vars; README carries both URLs, the wake-up warning, and the cost-per-run figure (~$0.03–0.05, reserves proven above).
9. **Repo hygiene:** MIT license file at root, README with setup + "how Token Factory is used" section, `.env.example` with `NEBIUS_API_KEY` / `TAVILY_API_KEY` only.

**Verification honesty note:** Ultra pricing and HF's paid-plan gate were verified on opened official pages; Tavily pricing on opened official docs. Super/Nano prices, Render limits, Streamlit limits, and Fly's no-free-tier status come from search-result summaries of official docs / multiple consistent project ledgers — solid enough to architect on, and every load-bearing number has ≥10× headroom in the budget math if it moves.