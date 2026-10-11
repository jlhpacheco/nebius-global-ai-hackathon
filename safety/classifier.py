"""Pre-draft safety classifier for Podrá Navega.

DETERMINISTIC, rule/keyword based. No LLM call. This MUST run on every
patient message BEFORE any model drafting happens:

  - crisis         -> NO draft. Red banner (call 911 / care team now),
                      case jumps the navigator queue. escalate=True
  - medical_advice -> NO draft. Routed to a human navigator. escalate=True
  - sensitive      -> NO AI draft sent; routed to a human. escalate=True
  - routine        -> Drafting allowed (a human still reviews + approves
                      every draft before anything reaches the patient).

Design rules that matter (see taxonomy.md for the full taxonomy):

  1. A medication NAME alone never escalates. Medical-advice detection
     requires advice-seeking intent (should/can I take it, stop it, dose,
     side effects, interactions, personal result interpretation,
     prognosis, procedure-prep instructions).
  2. General education is routine: "¿qué es una biopsia?" (what is a
     biopsy) is exactly the plain-language explanation the product is
     allowed to draft. Asking what MY result means is medical_advice.
  3. Precedence: crisis > medical_advice > sensitive > routine.
     A message is classified by its most dangerous matching category.

Matching is done on normalized text (lowercase, accents stripped), so
"quimioterapia"/"quimio", "inglés"/"ingles" etc. match the same rules.
"""

from __future__ import annotations

import re
import unicodedata


def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text)


# ---------------------------------------------------------------------------
# CRISIS — symptoms / emergencies / self-harm / immediate danger.
# Any match: no draft, red banner, queue jump.
# ---------------------------------------------------------------------------
CRISIS_RULES: list[tuple[str, str]] = [
    # (rule name, regex on normalized text)
    ("fever_during_treatment",
     r"\bfiebre\b|\bfever\b|\btemperatura de (38|39|40)\b"),
    ("bleeding",
     r"\bsangrando\b|\bsangrado\b|\bbleeding\b|\bsangre (en|por)\b|"
     r"\bvomit\w* sangre\b|\bblood in\b"),
    ("chest_pain_or_breathing",
     r"\bdolor (en|del|de) (el )?pecho\b|\bchest pain\b|"
     r"\bme duele (mucho |fuerte |el |mucho el )?pecho\b|"
     r"\bno puedo respirar\b|\bcan'?t breathe\b|\bcannot breathe\b|"
     r"\bme cuesta respirar\b|\bdificultad para respirar\b|"
     r"\btrouble breathing\b|\bshort(ness)? of breath\b"),
    ("self_harm",
     r"\bno quiero vivir\b|\bquiero morir\b|\bquitarme la vida\b|"
     r"\bsuicid\w*\b|\bkill myself\b|\bend my life\b|"
     r"\bno vale la pena vivir\b|\bhacerme dano\b"),
    ("emergency_state",
     r"\bemergencia\b|\bemergency\b|\bme (estoy )?desmay\w*\b|"
     r"\bfaint\w*\b|\bconvulsion\w*\b|\bseizure\b|\binconsciente\b|"
     r"\bunconscious\b|\bllamen al 911\b|\bcall 911\b"),
    ("uncontrolled_symptoms",
     r"\bdolor (insoportable|que no aguanto|intenso que)\b|"
     r"\bvomitos? que no paran?\b|\bcan'?t stop vomiting\b|"
     r"\bvomitando sin parar\b|\bunbearable pain\b"),
    ("immediate_danger",
     r"\bme esta (golpeando|pegando) ahora\b|"
     r"\btengo miedo de que me mate\b|\bhe is going to kill me\b"),
]

# ---------------------------------------------------------------------------
# MEDICAL ADVICE — diagnosis / treatment / medication / prognosis /
# personal-result interpretation / procedure-prep instructions.
# Requires advice-seeking INTENT; a drug name mentioned in passing
# (e.g. in a transport question) does NOT match any rule here.
# ---------------------------------------------------------------------------
MEDICAL_RULES: list[tuple[str, str]] = [
    ("personal_result_interpretation",
     r"\bque significa (este|mi|el) resultado\b|"
     r"\bque significa\w* (mi )?(analisis|estudio|resultado)\b|"
     r"\b(resultado|analisis|estudio|informe)\b[^.]{0,80}\bque significa\b|"
     r"\bque significa (esto|eso|este valor|este numero)\b|"
     r"\bwhat does (this|my) (result|scan|test|report) mean\b|"
     r"\binterpret\w* (mi|este|my|this) (resultado|result|analisis)\b|"
     r"\bes cancer\?|\bis (it|this) cancer\b|"
     r"\b(es|es un) (tumor )?(maligno|benigno)\b|"
     r"\bsalio (alto|positivo|anormal)\w* (en|mi) (analisis|resultado|estudio)\b|"
     r"\bmi (analisis|resultado) (salio|dice|marca)\b"),
    ("prognosis",
     r"\bcuanto tiempo me queda\b|\bhow long do i have\b|"
     r"\bme voy a morir\b|\bvoy a sobrevivir\b|"
     r"\bprobabilidades de (curarme|sobrevivir|vivir)\b|"
     r"\bchances of (surviving|being cured)\b|\besperanza de vida\b|"
     r"\blife expectancy\b"),
    ("medication_advice_intent",
     r"\b(debo|puedo|podria|quiero) (tomar|dejar|suspender|seguir tomando|cambiar|tomarme)\b|"
     r"\bshould i (take|stop|keep taking|change|continue)\b|"
     r"\bcan i take\b|\bdo i (take|stop)\b|"
     r"\bdejar de tomar\b|\bstop taking\b|\bstopping (my|the) medication\b|"
     r"\bsuspender (mi|el|la) (medicamento|tratamiento|pastilla)\b|"
     r"\binteract\w* (con|with) (mi|my|el) (tratamiento|medication)\b|"
     r"\b(es|sera) (seguro|peligroso) tomar\b|\bsafe to take\b"),
    ("dosage",
     r"\b(dosis|dosage|dose) de\b|\bcuantos? (mg|miligramos|pastillas) (debo|puedo|tomo)\b|"
     r"\bhow (much|many milligrams)\b|\b\d+\s?mg (debo|puedo|should)\b"),
    ("side_effect_management",
     r"\b(como (manejo|controlo|alivio)|que hago con) (los |las |mis )?(efectos secundarios|nauseas|vomitos|malestares)\b|"
     r"\bhow do i (manage|handle|relieve) (the )?(side effects|nausea)\b|"
     r"\bes normal (tener|sentir|que me|que tenga)\b|"
     r"\bis it normal to (feel|have|be)\b"),
    ("treatment_decision",
     r"\bdebo (hacerme|hacer|aceptar|seguir con) (la |el )?(quimioterapia|cirugia|tratamiento|radiacion)\b|"
     r"\bshould i (do|get|have|accept) (chemo|chemotherapy|surgery|radiation|the treatment)\b|"
     r"\bque tratamiento es mejor\b|\bwhich treatment is (best|better)\b|"
     r"\bnecesito (cirugia|operarme|quimioterapia)\?\b|"
     r"\bdo i need (surgery|chemo|chemotherapy|radiation)\b|"
     r"\balternativas? de tratamiento\b|\btreatment options for me\b"),
    ("procedure_prep_instruction",
     r"\bnecesito ayunar\b|\bayunar antes de\b|\bayuno antes de\b|"
     r"\bdo i need to fast\b|\bfasting before\b|"
     r"\bpuedo comer antes de (la|el|mi)\b|\bcan i eat before\b|"
     r"\bque (debo|tengo que) hacer antes de (la|el|mi) (biopsia|cirugia|estudio|operacion)\b|"
     r"\bwhat should i do before (the|my) (biopsy|surgery|scan|procedure)\b|"
     r"\b(prepararme|preparacion) para (la|el|mi) (biopsia|cirugia|operacion)\b.*\?$"),
]

# ---------------------------------------------------------------------------
# SENSITIVE — routed to a human, no AI draft: acute distress, financial
# desperation, abuse, grief, immigration fear. Distinct from routine
# barrier mentions (e.g. "tengo miedo de la biopsia" is a ROUTINE fear
# barrier the navigator workflow handles with a draft).
# ---------------------------------------------------------------------------
SENSITIVE_RULES: list[tuple[str, str]] = [
    ("acute_distress",
     r"\bno puedo parar de llorar\b|\bcan'?t stop crying\b|"
     r"\bcrisis de ansiedad\b|\bataque de panico\b|\bpanic attack\b|"
     r"\bestoy desesperad[oa]\b|\bi am desperate\b|"
     r"\bno aguanto mas\b|\bi can'?t take (it|this) anymore\b|"
     r"\bme siento (sola y )?abandonad[oa]\b|\bi feel abandoned\b"),
    ("financial_desperation",
     r"\bno tengo ni para\b|\bno tengo (dinero )?para comer\b|"
     r"\bno puedo pagar (la renta|el alquiler|el rent)\b|"
     r"\bcan'?t afford (rent|food|to eat)\b|"
     r"\b(me van a|van a) desalojar\b|\bbeing evicted\b|\beviction\b|"
     r"\bsin hogar\b|\bhomeless\b|\bno tengo para (el|la|los|las|pagar)\b"),
    ("abuse",
     r"\bme pega\b|\bme golpea\b|\bme maltrata\b|\babuso (de|domestico)\b|"
     r"\bdomestic violence\b|\bhits me\b|\bbeats me\b|\babuse[sd]?\b"),
    ("grief",
     r"\b(mi )?(esposo|esposa|madre|padre|hijo|hija|marido) (fallecio|murio|acaba de morir)\b|"
     r"\bmy (husband|wife|mother|father|son|daughter) (died|just died|passed away)\b|"
     r"\bestoy de luto\b|\bi am grieving\b"),
    ("immigration_fear",
     r"\bmiedo de que me deporten\b|\bafraid of (being )?deport\w*\b|"
     r"\bsoy indocumentad[oa]\b|\bi am undocumented\b|"
     r"\bmiedo de (ir|acudir) (por|porque) (mis papeles|no tengo papeles)\b"),
]


def _match_any(rules: list[tuple[str, str]], normalized: str):
    for name, pattern in rules:
        if re.search(pattern, normalized):
            return name
    return None


def classify_message(text: str) -> dict:
    """Classify one patient message BEFORE any drafting.

    Returns {"category": "crisis"|"medical_advice"|"sensitive"|"routine",
             "escalate": bool, "reason": str}
    """
    if not text or not text.strip():
        return {
            "category": "routine",
            "escalate": False,
            "reason": "Empty message — nothing to draft; navigator workflow handles it as routine intake.",
        }

    normalized = _normalize(text)

    rule = _match_any(CRISIS_RULES, normalized)
    if rule:
        return {
            "category": "crisis",
            "escalate": True,
            "reason": (
                f"Crisis rule '{rule}' matched. NO draft is generated. "
                "Show the red banner (call 911 / the care team now) and "
                "jump this case to the front of the navigator queue."
            ),
        }

    rule = _match_any(MEDICAL_RULES, normalized)
    if rule:
        return {
            "category": "medical_advice",
            "escalate": True,
            "reason": (
                f"Medical-advice rule '{rule}' matched (advice-seeking intent "
                "about diagnosis, treatment, medication, prognosis, personal "
                "results, or procedure prep). NO draft is generated. A human "
                "navigator answers using approved sources only."
            ),
        }

    rule = _match_any(SENSITIVE_RULES, normalized)
    if rule:
        return {
            "category": "sensitive",
            "escalate": True,
            "reason": (
                f"Sensitive rule '{rule}' matched (acute distress, financial "
                "desperation, abuse, grief, or immigration fear). Routed to a "
                "human navigator; no AI draft is sent."
            ),
        }

    return {
        "category": "routine",
        "escalate": False,
        "reason": (
            "No crisis, medical-advice, or sensitive rule matched. Drafting "
            "is allowed; a human navigator still reviews, edits, and "
            "approves the draft before anything reaches the patient."
        ),
    }


if __name__ == "__main__":
    import sys

    msg = " ".join(sys.argv[1:]) or "Me dijeron que necesito una biopsia y no entiendo, y no tengo transporte."
    print(classify_message(msg))
