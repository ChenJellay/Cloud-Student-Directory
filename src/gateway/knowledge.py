"""Minimal local knowledge snippets for the V1 Q&A prototype.

In production this would be replaced by ingested official CMU web pages /
handbooks. For the assignment prototype we keep a tiny static corpus.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeSnippet:
    id: str
    title: str
    text: str
    source_url: str
    keywords: tuple[str, ...]


SNIPPETS: tuple[KnowledgeSnippet, ...] = (
    KnowledgeSnippet(
        id="academic-calendar",
        title="Academic Calendar (general)",
        text=(
            "CMU publishes the official academic calendar with add/drop dates, "
            "semester start/end dates, and university holidays. Always verify "
            "the current term on the Registrar site before making decisions."
        ),
        source_url="https://www.cmu.edu/hub/registrar/academic-calendar.html",
        keywords=("calendar", "deadline", "add/drop", "drop", "add", "holiday", "semester"),
    ),
    KnowledgeSnippet(
        id="financial-aid",
        title="Financial Aid overview",
        text=(
            "The Hub and Student Financial Services publish information about "
            "aid applications, disbursement timing, and general eligibility "
            "resources. Personalized eligibility questions require speaking "
            "with a financial aid counselor."
        ),
        source_url="https://www.cmu.edu/sfs/",
        keywords=("financial aid", "tuition", "scholarship", "fafsa", "billing"),
    ),
    KnowledgeSnippet(
        id="health-insurance",
        title="Student health insurance",
        text=(
            "CMU provides information about student health insurance requirements "
            "and waivers through University Health Services. Check the current "
            "academic year requirements on the official page."
        ),
        source_url="https://www.cmu.edu/health-services/",
        keywords=("health insurance", "insurance", "waiver", "uhs", "health services"),
    ),
    KnowledgeSnippet(
        id="library",
        title="University Libraries",
        text=(
            "CMU Libraries provide study spaces, research help, and access to "
            "databases. Hours and locations are listed on the Libraries website."
        ),
        source_url="https://www.library.cmu.edu/",
        keywords=("library", "libraries", "study space", "hours"),
    ),
)


def retrieve(question: str, limit: int = 2) -> list[KnowledgeSnippet]:
    """Very small keyword overlap retriever for the prototype."""
    q = question.lower()
    scored: list[tuple[int, KnowledgeSnippet]] = []
    for snip in SNIPPETS:
        score = sum(1 for kw in snip.keywords if kw in q)
        if score:
            scored.append((score, snip))
    scored.sort(key=lambda item: item[0], reverse=True)
    if scored:
        return [s for _, s in scored[:limit]]
    # Default: return calendar + library as generic campus context
    return [SNIPPETS[0], SNIPPETS[3]]
