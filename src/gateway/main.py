"""Stateless Q&A routing gateway (minimal V1 prototype).

Client -> Gateway (interceptors) -> Ollama (or stub) -> Client
No chat history or PII is persisted.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .config import settings
from .interceptors import apply_interceptors
from .knowledge import retrieve
from .llm_client import LLMClient

app = FastAPI(
    title=settings.app_name,
    description=(
        "Minimal V1 student-support Q&A gateway. "
        "Safety interceptors run before any model call. "
        "Default model backend is free/local Ollama."
    ),
    version="0.1.0",
)
llm = LLMClient(settings)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class AskResponse(BaseModel):
    answer: str
    intercepted: bool
    interceptor_category: str | None = None
    backend: str
    model: str
    sources: list[str]
    disclaimer: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "llm_mode": settings.llm_mode}


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    question = payload.question.strip()
    hit = apply_interceptors(question)
    if hit.matched:
        return AskResponse(
            answer=hit.message or "",
            intercepted=True,
            interceptor_category=hit.category,
            backend="interceptor",
            model="none",
            sources=list(hit.sources),
            disclaimer=settings.disclaimer,
        )

    snippets = retrieve(question)
    context = "\n\n".join(
        f"- {s.title}: {s.text} (source: {s.source_url})" for s in snippets
    )
    reply = await llm.answer(question, context)
    return AskResponse(
        answer=reply.answer,
        intercepted=False,
        interceptor_category=None,
        backend=reply.backend,
        model=reply.model,
        sources=[s.source_url for s in snippets],
        disclaimer=settings.disclaimer,
    )
