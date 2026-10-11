"""Barrier taxonomy, rule-based detection, demo drafting, and resources.

This module is the deterministic engine behind DEMO MODE: with no
NEBIUS_API_KEY set, these rules produce the draft, the question list, and
the barrier audit so the whole workflow runs end-to-end at $0. With a key
set, the same outputs are supplied to Token Factory as the fallback /
demo_response for every call, and Ultra's barrier audit is asked to
confirm or extend them.

All patient data is fictional. Resources are a sample directory the
navigator must verify before approval (approval is blocked server-side
while any resource is unverified).
"""

from __future__ import annotations

import re

BARRIER_TAXONOMY = [
    "transport",
    "cost",
    "childcare",
    "work_schedule",
    "fear",
    "language",
    "health_literacy",
    "other",
]

_BARRIER_KEYWORDS: dict[str, list[str]] = {
    "transport": [
        "transporte", "transport", "no tengo transporte", "no tengo carro",
        "no car", "ride", "bus", "cómo llegar", "como llegar", "get there",
        "conducir", "driver",
    ],
    "cost": [
        "dinero", "money", "cuesta", "cost", "pagar", "pay for", "seguro",
        "insurance", "caro", "expensive", "afford", "factura", "bill",
    ],
    "childcare": [
        "niños", "ninos", "hijos", "kids", "children", "cuidar a mis",
        "childcare", "bebé", "bebe", "baby",
    ],
    "work_schedule": [
        "trabajo", "work", "jefe", "boss", "turno", "shift", "falto al",
        "permiso en el trabajo", "time off",
    ],
    "fear": [
        "miedo", "temor", "afraid", "scared", "nervios", "nerviosa",
        "nervioso", "ansiedad", "anxious", "preocupada", "preocupado",
        "worried",
    ],
    "language": [
        "no hablo inglés", "no hablo ingles", "don't speak english",
        "intérprete", "interprete", "interpreter", "solo español",
        "solo espanol", "in english",
    ],
    "health_literacy": [
        "no entiendo", "don't understand", "no sé qué es", "no se que es",
        "qué significa", "que significa", "what does", "qué es una",
        "que es una", "qué es un", "no comprendo",
    ],
}

_SPANISH_MARKERS = [
    " no ", " una ", " un ", " que ", " mi ", " me ", " tengo ", " necesito ",
    " entiendo ", " dijeron ", " señora ", " por favor", " gracias", " cita ",
    "¿", "á", "é", "í", "ó", "ú", "ñ",
]


def detect_language(text: str) -> str:
    low = " " + text.lower() + " "
    hits = sum(1 for marker in _SPANISH_MARKERS if marker in low)
    return "es" if hits >= 2 else "en"


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def detect_barriers(text: str) -> list[dict]:
    """Rule-based barrier audit: returns [{barrier, evidence}] with the
    exact sentence that evidences each barrier."""
    found: list[dict] = []
    sentences = _sentences(text) or [text.strip()]
    low_text = text.lower()
    for barrier, keywords in _BARRIER_KEYWORDS.items():
        for sentence in sentences:
            low_sentence = sentence.lower()
            if any(kw in low_sentence for kw in keywords):
                found.append({"barrier": barrier, "evidence": sentence})
                break
        else:
            # keyword split across the message (no single sentence match)
            if any(kw in low_text for kw in keywords):
                found.append({"barrier": barrier, "evidence": text.strip()[:160]})
    return found


# ---------------------------------------------------------------------------
# Deterministic demo drafting
# ---------------------------------------------------------------------------

_TOPICS = [
    (
        ["biopsia", "biopsy"],
        {
            "es": (
                "Una biopsia es un examen donde el doctor toma una muestra "
                "muy pequeña de tejido para revisarla en un laboratorio. "
                "Sirve para saber exactamente qué está pasando y poder "
                "planear el mejor cuidado para usted. Es normal tener "
                "preguntas: su navegadora le va a ayudar a prepararlas "
                "antes de su cita."
            ),
            "en": (
                "A biopsy is a test where the doctor takes a very small "
                "sample of tissue to check it in a laboratory. It shows "
                "exactly what is happening so your care team can plan the "
                "best care for you. It is normal to have questions: your "
                "navigator will help you prepare them before your "
                "appointment."
            ),
        },
    ),
    (
        ["quimioterapia", "chemotherapy", "quimio"],
        {
            "es": (
                "La quimioterapia es un tratamiento con medicamentos que "
                "busca detener el crecimiento de las células del cáncer. "
                "Cada persona lo recibe de forma distinta, y su equipo "
                "médico le explicará su plan. Su navegadora puede ayudarle "
                "a anotar sus dudas para la próxima cita."
            ),
            "en": (
                "Chemotherapy is a treatment with medicines that work to "
                "stop cancer cells from growing. Everyone receives it "
                "differently, and your medical team will explain your plan. "
                "Your navigator can help you write down your questions for "
                "the next appointment."
            ),
        },
    ),
    (
        ["cirugía", "cirugia", "surgery", "operación", "operacion"],
        {
            "es": (
                "Una cirugía es una operación que hace el doctor como parte "
                "de su cuidado. Su equipo médico le explicará por qué la "
                "recomienda y cómo prepararse. Su navegadora puede "
                "ayudarle a preparar sus preguntas antes de la cita."
            ),
            "en": (
                "Surgery is an operation your doctor performs as part of "
                "your care. Your medical team will explain why they "
                "recommend it and how to prepare. Your navigator can help "
                "you prepare your questions before the appointment."
            ),
        },
    ),
    (
        ["resultados", "results", "resultado"],
        {
            "es": (
                "Esperar resultados puede causar mucha preocupación, y eso "
                "es normal. Cuando lleguen, su equipo médico se los va a "
                "explicar. Su navegadora puede ayudarle a anotar qué "
                "preguntar cuando reciba los resultados."
            ),
            "en": (
                "Waiting for results can cause a lot of worry, and that is "
                "normal. When they arrive, your medical team will explain "
                "them to you. Your navigator can help you write down what "
                "to ask when you receive the results."
            ),
        },
    ),
]

_DEFAULT_EXPLANATION = {
    "es": (
        "Gracias por su mensaje. Entendemos que esto puede ser difícil de "
        "entender, y no tiene que pasarlo sola. Su navegadora revisó este "
        "mensaje y le va a ayudar con los próximos pasos y a preparar sus "
        "preguntas para el doctor."
    ),
    "en": (
        "Thank you for your message. We understand this can be hard to "
        "take in, and you do not have to go through it alone. Your "
        "navigator reviewed this message and will help you with the next "
        "steps and prepare your questions for the doctor."
    ),
}

_QUESTION_LIST = {
    "es": [
        "¿Cuándo es mi cita y dónde tengo que llegar?",
        "¿Qué va a pasar durante el examen o la cita?",
        "¿Necesito hacer algo para prepararme?",
        "¿Cuándo y cómo voy a recibir los resultados?",
        "¿A quién puedo llamar si tengo preguntas o un problema?",
    ],
    "en": [
        "When is my appointment and where do I need to go?",
        "What will happen during the test or appointment?",
        "Do I need to do anything to prepare?",
        "When and how will I receive the results?",
        "Who can I call if I have questions or a problem?",
    ],
}

_BARRIER_NOTE = {
    "transport": {
        "es": "Vemos que el transporte puede ser un problema. Su navegadora "
              "le va a ayudar a buscar una opción de transporte verificada.",
        "en": "We see transportation may be a problem. Your navigator will "
              "help you find a verified transportation option.",
    },
    "cost": {
        "es": "Si el costo le preocupa, su navegadora puede buscar ayuda "
              "financiera verificada para usted.",
        "en": "If cost is a worry, your navigator can look for verified "
              "financial help for you.",
    },
    "childcare": {
        "es": "Su navegadora puede ayudarle a pensar opciones para el "
              "cuidado de sus niños durante su cita.",
        "en": "Your navigator can help you think through childcare options "
              "during your appointment.",
    },
    "work_schedule": {
        "es": "Su navegadora puede darle una carta para su trabajo si la "
              "necesita para su cita.",
        "en": "Your navigator can give you a note for your work if you need "
              "one for your appointment.",
    },
    "fear": {
        "es": "Es normal sentir miedo. No tiene que pasar por esto sola: "
              "hay grupos de apoyo verificados que su navegadora le puede "
              "compartir.",
        "en": "It is normal to feel afraid. You do not have to go through "
              "this alone: there are verified support groups your navigator "
              "can share with you.",
    },
}


def draft_reply(text: str, language: str, barriers: list[dict]) -> dict:
    """Deterministic plain-language draft (demo mode / fallback).

    Returns {reply, reply_en, question_list, question_list_en}.
    Medical content is information/preparation only, drawn from the fixed
    approved templates above — never free-generated medical advice.
    """
    low = text.lower()
    explanation = None
    for keywords, texts in _TOPICS:
        if any(kw in low for kw in keywords):
            explanation = texts
            break
    if explanation is None:
        explanation = _DEFAULT_EXPLANATION

    other = "en" if language == "es" else "es"
    parts = [explanation[language]]
    barrier_names = {b["barrier"] for b in barriers}
    for name in ("transport", "cost", "childcare", "work_schedule", "fear"):
        if name in barrier_names:
            parts.append(_BARRIER_NOTE[name][language])
    if language != other:
        parts.append(
            "— Su navegadora aprobó este mensaje antes de enviárselo."
            if language == "es"
            else "— Your navigator approved this message before it was sent."
        )

    gloss_parts = [explanation[other]]
    for name in ("transport", "cost", "childcare", "work_schedule", "fear"):
        if name in barrier_names:
            gloss_parts.append(_BARRIER_NOTE[name][other])
    gloss_parts.append(
        "— Your navigator approved this message before it was sent."
        if other == "en"
        else "— Su navegadora aprobó este mensaje antes de enviárselo."
    )

    if language == "es":
        return {
            "reply": " ".join(parts),
            "reply_en": " ".join(gloss_parts),
            "question_list": _QUESTION_LIST["es"],
            "question_list_en": _QUESTION_LIST["en"],
        }
    return {
        "reply": " ".join(parts),
        "reply_en": " ".join(parts),  # primary text is already English
        "question_list": _QUESTION_LIST["en"],
        "question_list_en": _QUESTION_LIST["en"],
    }


# ---------------------------------------------------------------------------
# Sample resource directory (navigator must verify each before approval)
# ---------------------------------------------------------------------------

_RESOURCE_DIRECTORY = {
    "transport": {
        "name": "VTA Paratransit — transporte para citas médicas "
                "(directorio de muestra)",
        "type": "transport",
        "source_url": "https://www.vta.org/services/paratransit",
    },
    "cost": {
        "name": "CancerCare — ayuda financiera (directorio de muestra)",
        "type": "financial",
        "source_url": "https://www.cancercare.org/financial",
    },
}

_SUPPORT_RESOURCE = {
    "name": "Latinas Contra Cancer — grupo de apoyo (directorio de muestra)",
    "type": "support_group",
    "source_url": "https://www.latinascontracancer.org/",
}

_RESOURCE_LAST_CHECKED = "2026-10-11"


def resources_for(barriers: list[dict]) -> list[dict]:
    """Attach sample-directory resources for the barriers found, plus the
    support-group resource. All start unverified: approval stays blocked
    until the navigator verifies each one."""
    resources: list[dict] = []
    names = {b["barrier"] for b in barriers}
    for barrier in ("transport", "cost"):
        if barrier in names and barrier in _RESOURCE_DIRECTORY:
            entry = dict(_RESOURCE_DIRECTORY[barrier])
            entry["last_checked"] = _RESOURCE_LAST_CHECKED
            entry["verified"] = False
            resources.append(entry)
    support = dict(_SUPPORT_RESOURCE)
    support["last_checked"] = _RESOURCE_LAST_CHECKED
    support["verified"] = False
    resources.append(support)
    return resources
