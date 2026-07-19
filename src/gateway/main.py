"""Stateless Q&A routing gateway (minimal V1 prototype).

Client -> Gateway (interceptors) -> Ollama (or stub) -> Client
No chat history or PII is persisted server-side.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import settings
from .interceptors import apply_interceptors
from .knowledge import retrieve
from .llm_client import OLLAMA_SETUP_HINT, LLMClient

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title=settings.app_name,
    description=(
        "Minimal V1 student-support Q&A gateway. "
        "Safety interceptors run before any model call. "
        "Stub mode works with zero model disk; LLM mode uses local Ollama when available."
    ),
    version="0.1.0",
)
llm = LLMClient(settings)

# Runtime mode for the UI toggle (does not persist across restarts).
_runtime_mode = settings.llm_mode.lower().strip()
if _runtime_mode in {"llm", "ollama"}:
    _runtime_mode = "llm"
elif _runtime_mode != "stub":
    # Prefer stub for constrained lab VMs; UI can still switch to LLM.
    _runtime_mode = "stub"


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    mode: str | None = Field(
        default=None,
        description="Optional per-request override: stub | llm",
    )


class AskResponse(BaseModel):
    answer: str
    intercepted: bool
    interceptor_category: str | None = None
    backend: str
    model: str
    sources: list[str]
    disclaimer: str
    mode: str


class ModeRequest(BaseModel):
    mode: str = Field(..., description="stub or llm")


class ModeResponse(BaseModel):
    mode: str


def _normalize_mode(mode: str) -> str:
    value = mode.lower().strip()
    if value in {"llm", "ollama"}:
        return "llm"
    if value == "stub":
        return "stub"
    raise HTTPException(status_code=400, detail="mode must be 'stub' or 'llm'")


def _backend_mode(ui_mode: str) -> str:
    return "ollama" if ui_mode == "llm" else "stub"


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, object]:
    status = await llm.probe_ollama()
    return {
        "status": "ok",
        "llm_mode": _runtime_mode,
        "ollama_host": settings.ollama_host,
        "ollama_model": settings.ollama_model,
        "ollama_reachable": status.reachable,
        "ollama_model_ready": status.model_ready,
        "ollama_detail": status.detail,
    }


@app.get("/mode", response_model=ModeResponse)
async def get_mode() -> ModeResponse:
    return ModeResponse(mode=_runtime_mode)


@app.post("/mode", response_model=ModeResponse)
async def set_mode(payload: ModeRequest) -> ModeResponse:
    global _runtime_mode
    _runtime_mode = _normalize_mode(payload.mode)
    return ModeResponse(mode=_runtime_mode)


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
    question = payload.question.strip()
    ui_mode = _normalize_mode(payload.mode) if payload.mode else _runtime_mode

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
            mode=ui_mode,
        )

    snippets = retrieve(question)
    context = "\n\n".join(
        f"- {s.title}: {s.text} (source: {s.source_url})" for s in snippets
    )
    try:
        reply = await llm.answer(question, context, mode=_backend_mode(ui_mode))
    except Exception as exc:  # noqa: BLE001
        if ui_mode == "llm":
            return AskResponse(
                answer=(
                    "LLM mode is selected, but the model backend is not ready. "
                    f"{OLLAMA_SETUP_HINT} "
                    f"Details: {exc}"
                ),
                intercepted=False,
                interceptor_category=None,
                backend="error",
                model="none",
                sources=[s.source_url for s in snippets],
                disclaimer=settings.disclaimer,
                mode=ui_mode,
            )
        raise

    return AskResponse(
        answer=reply.answer,
        intercepted=False,
        interceptor_category=None,
        backend=reply.backend,
        model=reply.model,
        sources=[s.source_url for s in snippets],
        disclaimer=settings.disclaimer,
        mode=ui_mode,
    )


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
