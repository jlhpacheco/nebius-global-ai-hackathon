"""Minimal local safety classifier — FALLBACK ONLY.

The real taxonomy lives in the sibling ``safety`` package
(``safety/classifier.py``, built by the safety front). This module is used
only when that import is unavailable at runtime. It is deliberately small:
a keyword screen for the categories that must never reach drafting
(crisis, medical advice) plus a sensitive flag. It does NOT duplicate the
full taxonomy.
"""

from __future__ import annotations

_CRISIS = [
    "quiero morirme", "no quiero vivir", "suicid", "kill myself",
    "self-harm", "me quiero matar", "sangrando mucho", "bleeding a lot",
    "no puedo respirar", "can't breathe", "cannot breathe",
    "dolor en el pecho", "chest pain", "fiebre alta", "high fever",
    "emergencia", "emergency", "desmayo", "fainted",
]

_MEDICAL_ADVICE = [
    "debo tomar", "should i take", "puedo tomar", "cambiar mi dosis",
    "change my dose", "mi dosis", "dosage", "qué medicina", "que medicina",
    "which medication", "qué tratamiento", "que tratamiento",
    "which treatment", "es cáncer", "es cancer", "do i have cancer",
    "pronóstico", "pronostico", "prognosis", "me va a curar", "will it cure",
]

_SENSITIVE = [
    "deprimid", "depressed", "ansiedad severa", "abuso", "abuse",
    "violencia", "no tengo papeles", "undocumented", "inmigración",
    "immigration status", "me siento muy mal emocionalmente",
]


def _hit(text: str, phrases: list[str]) -> str | None:
    low = text.lower()
    for phrase in phrases:
        if phrase in low:
            return phrase
    return None


def classify_message_fallback(text: str) -> dict:
    """Same return shape as safety.classifier.classify_message."""
    hit = _hit(text, _CRISIS)
    if hit:
        return {
            "category": "crisis",
            "escalate": True,
            "reason": f"Crisis keyword matched (fallback classifier): '{hit}'. "
                      "Escalated before any drafting.",
        }
    hit = _hit(text, _MEDICAL_ADVICE)
    if hit:
        return {
            "category": "medical_advice",
            "escalate": True,
            "reason": f"Medical-advice keyword matched (fallback classifier): "
                      f"'{hit}'. Podrá Navega never drafts medical advice; "
                      "escalated to the navigator.",
        }
    hit = _hit(text, _SENSITIVE)
    if hit:
        return {
            "category": "sensitive",
            "escalate": True,
            "reason": f"Sensitive topic matched (fallback classifier): '{hit}'. "
                      "Escalated to the navigator.",
        }
    return {
        "category": "routine",
        "escalate": False,
        "reason": "No crisis/medical/sensitive keywords matched "
                  "(fallback classifier).",
    }
