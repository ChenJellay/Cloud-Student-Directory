"""Deterministic safety interceptors (code-as-policy).

These rules run BEFORE any LLM call. High-risk topics never reach the model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class InterceptorResult:
    matched: bool
    category: str | None = None
    message: str | None = None
    sources: tuple[str, ...] = ()


# Keyword / regex interceptors aligned with the V1 scoping document.
_INTERCEPTORS: list[tuple[str, re.Pattern[str], str, tuple[str, ...]]] = [
    (
        "mental_health_crisis",
        re.compile(
            r"\b(suicid(e|al)|self[-\s]?harm|kill\s+myself|want\s+to\s+die|"
            r"overdose|crisis\s+hotline)\b",
            re.IGNORECASE,
        ),
        (
            "If you are in crisis or experiencing a mental health emergency, "
            "please contact Campus Police / University Police immediately, "
            "or call/text 988 (Suicide & Crisis Lifeline). "
            "Counseling and Psychological Services (CaPS) can also help: "
            "https://www.cmu.edu/counseling/"
        ),
        ("https://www.cmu.edu/counseling/", "https://988lifeline.org/"),
    ),
    (
        "visa_immigration",
        re.compile(
            r"\b(opt|cpt|f-?1|j-?1|visa|i-?20|immigration|uscis|work\s+authorization|"
            r"stem\s+opt|sevis)\b",
            re.IGNORECASE,
        ),
        (
            "I cannot advise on immigration, visa, CPT/OPT, or work-authorization "
            "questions. Please contact the Office of International Education (OIE) "
            "directly: https://www.cmu.edu/oie/"
        ),
        ("https://www.cmu.edu/oie/",),
    ),
]


def apply_interceptors(question: str) -> InterceptorResult:
    """Return a hard-routed response if the question matches a safety rule."""
    text = question.strip()
    if not text:
        return InterceptorResult(matched=False)

    for category, pattern, message, sources in _INTERCEPTORS:
        if pattern.search(text):
            return InterceptorResult(
                matched=True,
                category=category,
                message=message,
                sources=sources,
            )
    return InterceptorResult(matched=False)
