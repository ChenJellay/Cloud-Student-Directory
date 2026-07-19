"""LLM backends: Ollama (free/local) with stub fallback."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from .config import Settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful CMU student support assistant for Version 1.
Answer ONLY general administrative questions about published university policies,
deadlines, and campus resources. Be concise and factual.
If you are unsure, say you do not know and suggest contacting the Hub or the
relevant office. Do not provide personalized advising, grade estimates, or
immigration advice.
"""

OLLAMA_SETUP_HINT = (
    "LLM mode needs a local Ollama daemon and model. "
    "Install Ollama, run `ollama serve`, then `ollama pull tinyllama` "
    "(~2GB+ free disk). On small Cloud9 disks, stay on Stub mode."
)


@dataclass
class ModelReply:
    answer: str
    backend: str
    model: str


@dataclass
class OllamaStatus:
    reachable: bool
    model_ready: bool
    model: str
    models: list[str]
    detail: str = ""


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def probe_ollama(self) -> OllamaStatus:
        """Report whether Ollama is up and the configured model is pulled."""
        host = self.settings.ollama_host.rstrip("/")
        wanted = self.settings.ollama_model
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{host}/api/tags")
                response.raise_for_status()
                payload: dict[str, Any] = response.json()
        except Exception as exc:  # noqa: BLE001
            return OllamaStatus(
                reachable=False,
                model_ready=False,
                model=wanted,
                models=[],
                detail=str(exc),
            )

        names = [m.get("name", "") for m in payload.get("models", []) if isinstance(m, dict)]
        ready = any(
            name == wanted or name.startswith(f"{wanted}:") or name.startswith(wanted)
            for name in names
        )
        return OllamaStatus(
            reachable=True,
            model_ready=ready,
            model=wanted,
            models=names,
            detail="" if ready else f"model '{wanted}' not pulled yet",
        )

    async def answer(
        self, question: str, context: str, mode: str | None = None
    ) -> ModelReply:
        resolved = (mode or self.settings.llm_mode).lower().strip()
        if resolved in {"llm", "ollama"}:
            resolved = "ollama"
        if resolved == "stub":
            return self._stub(question)
        if resolved == "ollama":
            return await self._ollama(question, context)
        # auto: try Ollama, fall back to stub
        try:
            return await self._ollama(question, context)
        except Exception as exc:  # noqa: BLE001 — intentional soft fallback
            logger.warning("Ollama unavailable (%s); using stub response.", exc)
            return self._stub(question)

    def _stub(self, question: str) -> ModelReply:
        return ModelReply(
            answer=(
                "[STUB] Pipeline OK. Received your question: "
                f"“{question.strip()}”. "
                "Switch the UI to LLM mode (with Ollama running) "
                "to generate a real answer from the local knowledge snippets."
            ),
            backend="stub",
            model="none",
        )

    async def _ollama(self, question: str, context: str) -> ModelReply:
        host = self.settings.ollama_host.rstrip("/")
        model = self.settings.ollama_model
        status = await self.probe_ollama()
        if not status.reachable:
            raise RuntimeError(
                f"Ollama is not reachable at {host}. {OLLAMA_SETUP_HINT} "
                f"Details: {status.detail}"
            )
        if not status.model_ready:
            raise RuntimeError(
                f"Ollama is up, but model '{model}' is missing. "
                f"Run: ollama pull {model}. "
                "That needs roughly 2GB+ free disk. "
                f"Available models: {status.models or '[]'}"
            )

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Official context snippets:\n{context}\n\n"
            f"Student question: {question.strip()}\n\n"
            "Answer:"
        )
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.post(f"{host}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
        text = (data.get("response") or "").strip() or (
            "I could not generate an answer. Please try again or contact the Hub."
        )
        return ModelReply(answer=text, backend="ollama", model=model)
