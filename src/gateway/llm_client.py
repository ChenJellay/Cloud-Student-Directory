"""LLM backends: Ollama (free/local) with stub fallback."""

from __future__ import annotations

import logging
from dataclasses import dataclass

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


@dataclass
class ModelReply:
    answer: str
    backend: str
    model: str


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def answer(self, question: str, context: str) -> ModelReply:
        mode = self.settings.llm_mode.lower().strip()
        if mode == "stub":
            return self._stub(question)
        if mode == "ollama":
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
                "Connect Ollama (LLM_MODE=ollama or auto with ollama serve) "
                "to generate a real answer from the local knowledge snippets."
            ),
            backend="stub",
            model="none",
        )

    async def _ollama(self, question: str, context: str) -> ModelReply:
        host = self.settings.ollama_host.rstrip("/")
        model = self.settings.ollama_model
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
            # Fail fast if the daemon is down
            tags = await client.get(f"{host}/api/tags")
            tags.raise_for_status()
            response = await client.post(f"{host}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
        text = (data.get("response") or "").strip() or (
            "I could not generate an answer. Please try again or contact the Hub."
        )
        return ModelReply(answer=text, backend="ollama", model=model)
