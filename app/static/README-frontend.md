# Frontend — Podrá Navega demo UI

One static page: `index.html` + `style.css` + `app.js`. Vanilla JS, no build
step, no framework, no CDN dependency — the page works fully offline so the
demo cannot die because a CDN or the backend is down.

Serve the folder with any static server, or let the FastAPI backend mount it.
Example: `python3 -m http.server -d app/static 8000`

## How the page maps to the 6 red-team fixes

1. **Safety battery + visible guardrails (Fix 1)**
   - The Approve gate is code, not a claim: the button is disabled while any
     cited resource is unverified, while the case is escalated, or when there
     is no draft. The blocking reason is printed next to the button — the
     resource blocker uses the exact line "Approve is off until all resources
     are verified."
   - Crisis cases render with no draft area content ("No AI draft") and the
     patient view shows a red emergency banner in English first (call 911 /
     your care team now), Spanish below, rendered from case state alone.
     Try "Crisis case."
2. **Barrier-catch eval (Fix 2)** — the navigator panel shows the barrier
   checklist as a first-class artifact: each barrier with its evidence quote
   from the patient's own words and who found it (first draft vs. Ultra
   audit). This is the surface the catch-rate number will be read from.
3. **Real navigator evidence (Fix 3)** — the whole left panel is the
   navigator's workspace: edit box, verify checkboxes, and an approval record
   (who / when / what was edited) that fills in as a product artifact after
   approval, ready to be timed and quoted on camera.
4. **Video opens on the navigator's screen (Fix 4)** — layout order and
   visual weight put the navigator panel first (left, accent header); the
   patient chat is the secondary right panel. The page loads with a complete
   case already on the navigator's screen.
5. **English gloss (Fix 5)** — every draft renders with a toggleable English
   gloss block next to it ("Show English gloss / Mostrar traducción al inglés",
   on by default), and all UI chrome is labeled EN/ES (English first), so a judge who
   does not read Spanish can verify fidelity live.
6. **"Fictional patients" on screen (Fix 6)** — the pill "Fictional patient /
   Paciente ficticio" is always visible in the case header, and the label is
   repeated in the patient panel and on the patient's own chat bubble.

## Modes

- **Golden sample (default, fully local):** the biopsy + no-ride case (English
  patient; the live pipeline still drafts in Spanish for Spanish messages),
  with draft, English gloss, three barriers (one found only by the Ultra
  audit), one verified and one unverified resource, and a model/cost ledger.
  The Approve button starts disabled; tick the transport resource to enable
  it. A second golden case shows the crisis path. Golden mode is visually
  identical to live mode.
- **Live:** the case picker and the patient message form call the backend:
  `GET /api/cases`, `GET /api/cases/{id}`, `POST /api/cases`
  `{message, language}`, `POST /api/cases/{id}/edit {reply}`,
  `POST /api/cases/{id}/verify-resource {index}`,
  `POST /api/cases/{id}/approve {navigator_name}`, plus `GET /api/ledger`
  filtered client-side by `case_id`.
  Responses pass through a normalizer that maps the backend's shapes
  (draft object `{reply, reply_en, question_list}`, `barriers_found`,
  `safety`, `approval_record`) onto the same view model the golden cases
  use, so both modes render identically.

## Design notes

- Warm, calm palette matched to Latinas Contra Cancer's brand (cream
  ground, LCC orange #D16616, navy #112F5B, brand green #04723D — verified
  Oct 11, 2026; see LCC-STYLE-TOKENS.md); no default framework skin anywhere.
  The crisis red is deliberately NOT rebranded.
- Large type (17px base), generous spacing, short bilingual labels — built
  for a dyslexic reader and for judges scanning fast.
- The patient view shows only a neutral receipt ("Your message was received")
  before approval — never unapproved AI content — and the approved reply
  appears there only after the navigator approves.
- The footer of the navigator panel is a receipts table: model, task,
  tokens, and estimated cost per call, with totals.
