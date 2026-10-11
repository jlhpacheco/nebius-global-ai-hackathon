# Podrá Navega — Safety Escalation Taxonomy

This taxonomy is enforced by `safety/classifier.py` **before any AI draft
is generated**. The classifier is deterministic (rules and keywords in
Spanish and English). No model call decides safety. A human navigator
reviews and approves every routine draft — the classifier's job is to
make sure the wrong kind of message never becomes a draft at all.

Order of checks (first match wins):
**crisis → medical_advice → sensitive → routine**

---

## 1. CRISIS — stop everything

**What the system does:** NO draft. The patient immediately sees a red
banner in Spanish telling her to call 911 or her care team now. The
case jumps to the front of the navigator queue, flagged red.

**Categories:** symptoms that can be emergencies during cancer
treatment, uncontrolled symptoms, self-harm, immediate danger.

Example phrases:

- «Tengo fiebre de 39 y estoy en quimioterapia» (fever during chemo)
- «Estoy sangrando y no para» / "I am bleeding and it won't stop"
- «Me duele el pecho, me cuesta respirar» / "chest pain, can't breathe"
- «Ya no quiero vivir» / "I think I should end my life"
- «Estoy vomitando sin parar», «un dolor insoportable»
- «Me está golpeando ahora» (violence happening right now = crisis;
  abuse in the past = sensitive, below)

**Why first:** minutes matter. A chat draft is the wrong artifact for
an emergency — the red-team review requires this path to be visible in
the demo video, in Spanish, before any drafting happens.

## 2. MEDICAL ADVICE — a human answers, the AI does not draft

**What the system does:** NO draft. The message is routed to a human
navigator, who answers only from pre-approved source material
(shown with its source) — or refers the patient to her care team.

**Categories** (advice-seeking *intent* is required — see the edge
rules at the bottom):

- **Diagnosis / personal result interpretation:** «¿Qué significa este
  resultado? ¿Es cáncer?», "What does my scan result mean?", a lab
  value from *her own* analysis.
- **Treatment decisions:** «¿Debo hacerme la cirugía o la
  quimioterapia?», "Should I stop the treatment?", «¿Qué tratamiento
  es mejor para mí?»
- **Medication advice:** «¿Debo dejar de tomar…?», "Can I take
  ibuprofen with my treatment?", stopping/changing/continuing a drug.
- **Dosage:** «¿Cuántos mg debo tomar?», "How much should I take?"
- **Side-effect management:** «¿Cómo manejo los efectos
  secundarios?», "Is it normal to feel this nauseous after chemo?"
- **Prognosis:** «¿Cuánto tiempo me queda?», "What are my chances of
  surviving?"
- **Procedure-prep instructions:** «¿Necesito ayunar antes de la
  biopsia?», "What should I do before my surgery?" — a wrong invented
  instruction can cancel a procedure or cause harm, so a human answers
  from the approved source for that procedure.

## 3. SENSITIVE — a human takes the case

**What the system does:** NO AI draft is sent. The case is routed to a
human navigator. These are not emergencies and not medical questions —
they are situations where a drafted template is the wrong response.

- **Acute distress:** «No puedo parar de llorar», "panic attack",
  «Estoy desesperada», «No aguanto más».
  *(Plain fear is different — see routine.)*
- **Financial desperation:** «No tengo ni para comer», "we are being
  evicted", «No puedo pagar la renta». *(A plain cost barrier — "the
  copay is expensive" — is routine navigation; desperation markers are
  what escalate.)*
- **Abuse:** «Mi esposo me pega», "domestic violence". (If it is
  happening *right now* or she fears for her life, it is crisis.)
- **Grief:** «Mi esposo falleció el mes pasado», "my mother just died".
- **Immigration fear:** «Soy indocumentada y tengo miedo», "afraid of
  being deported". A human who knows safe resources responds.

## 4. ROUTINE — drafting allowed (human still approves)

**What the system does:** the AI may draft (plain-language explanation,
question list for the doctor, resource referrals). A human navigator
reviews, edits, and must approve before anything reaches the patient.
Resource referrals stay un-sendable until the navigator verifies each
resource (the Approve button is disabled until then).

Examples: appointment times and changes, transport and shuttle
questions, interpreter requests, support-group locations, childcare and
work-schedule *barriers*, requests for written/plain-language material,
and **general education**:

- «¿Qué es una biopsia?» — "What is a biopsy?" is the product's core
  allowed draft. It explains a procedure in general. It does NOT
  interpret *her* result (that is medical advice, §2).

---

## Edge rules — the distinctions the classifier must hold

1. **A medication name is not a medical question.** «El camión pasa
   por la farmacia donde recojo mi metformina, ¿a qué hora sale?»
   mentions a drug inside a *transport* question. No advice-seeking
   intent → **routine**. A classifier that escalates on drug nouns
   would block normal navigation.
2. **Logistics about medication is not advice about medication.**
   «¿Dónde renuevo mi receta?» (where do I renew) is **routine**.
   «¿Debo seguir tomándola?» (should I keep taking it) is
   **medical_advice**.
3. **General education ≠ personal interpretation.** «¿Qué es…?»
   about a procedure = routine. «¿Qué significa *mi* resultado?» =
   medical_advice.
4. **Fear has two levels.** «Tengo miedo de la biopsia» = a routine
   **fear barrier** the workflow answers with a calm drafted
   explanation. «No puedo parar de llorar / estoy desesperada» =
   acute distress = **sensitive**.
5. **Cost has two levels.** A cost barrier ("I can't afford the
   copay") = routine navigation. Desperation (no food money, eviction)
   = **sensitive**.
6. When two categories match, the more dangerous one wins
   (crisis > medical_advice > sensitive > routine).

## Proof

`safety/battery.py` runs `safety/battery_cases.json` (31 adversarial
cases: 7 crisis, 9 medical_advice, 5 sensitive, 10 routine including
the documented edges above) through the classifier. Target: **100% on
crisis + medical_advice (zero tolerance)**, and routine cases must not
over-escalate. Current result is printed by the script — run it; do
not trust this file for the number.
