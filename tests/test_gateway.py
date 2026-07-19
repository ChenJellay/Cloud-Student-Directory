from gateway.interceptors import apply_interceptors
from gateway.knowledge import retrieve


def test_visa_interceptor_blocks_opt_question():
    result = apply_interceptors("When can I apply for OPT?")
    assert result.matched is True
    assert result.category == "visa_immigration"
    assert "OIE" in (result.message or "")


def test_mental_health_interceptor():
    result = apply_interceptors("I am having suicidal thoughts")
    assert result.matched is True
    assert result.category == "mental_health_crisis"


def test_safe_question_passes_interceptors():
    result = apply_interceptors("Where can I find the academic calendar?")
    assert result.matched is False


def test_knowledge_retrieval_for_calendar():
    hits = retrieve("What is the add/drop deadline?")
    assert hits
    assert any("calendar" in h.id for h in hits)
