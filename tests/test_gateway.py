from fastapi.testclient import TestClient

from gateway.interceptors import apply_interceptors
from gateway.knowledge import retrieve
from gateway.main import app


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


def test_ui_and_stub_ask():
    client = TestClient(app)
    home = client.get("/")
    assert home.status_code == 200
    assert "Student Support" in home.text

    mode = client.post("/mode", json={"mode": "stub"})
    assert mode.status_code == 200
    assert mode.json()["mode"] == "stub"

    ask = client.post(
        "/ask",
        json={"question": "Where can I find the academic calendar?", "mode": "stub"},
    )
    assert ask.status_code == 200
    body = ask.json()
    assert body["backend"] == "stub"
    assert body["mode"] == "stub"
    assert "STUB" in body["answer"]
