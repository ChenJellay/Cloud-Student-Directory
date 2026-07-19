# CMU Student Support Q&A Gateway (V1 Minimal Prototype)

Minimal **question-answering** prototype for the AI-Powered Student Support Pilot.

This repo implements the **decoupled routing gateway** from ADR 001, with a free/local **Ollama** model backend instead of a paid cloud LLM API. Safety interceptors run *before* any model call.

```
Student question
      │
      ▼
┌─────────────────────┐
│  FastAPI Gateway    │  ← accepts /ask
│  Safety Interceptors│  ← visa / crisis hard-routes
│  Tiny retriever     │  ← static official snippets
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Ollama (local LLM) │  ← free model hosting
│  or stub fallback   │
└─────────────────────┘
```

## Prerequisites

- Docker Desktop (for Dev Containers), **or**
- Python 3.12+ and [Ollama](https://ollama.com/) installed locally
- Git

## Repo layout

```
.
├── .devcontainer/          # Reproducible VS Code / Codespaces environment
├── docs/                   # Architecture diagram, narrative, provenance
├── knowledge/              # Notes on the V1 knowledge boundary
├── src/gateway/            # Stateless Q&A API
├── tests/                  # Unit tests for interceptors / retrieval
├── requirements.txt
└── README.md
```

## Quick start (Devcontainer — recommended)

1. Clone this repository.
2. Open the folder in VS Code / Cursor.
3. Choose **Reopen in Container** when prompted (or Command Palette → “Dev Containers: Reopen in Container”).
4. Wait for `postCreateCommand` to install Python deps and pull `tinyllama`.
5. In a container terminal:

```bash
LLM_MODE=auto uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
```

6. Ask a question:

```bash
curl -s http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Where can I find the academic calendar?"}' | python -m json.tool
```

## Quick start (local, without Devcontainer)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional: real answers via Ollama
ollama serve   # separate terminal
ollama pull tinyllama

# Stub-only (no Ollama required) — proves end-to-end pipeline
LLM_MODE=stub uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
```

## API

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness check |
| `POST` | `/ask` | Submit a student question |

### Example intercepted response (visa)

```bash
curl -s http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Can you help me with OPT timelines?"}' | python -m json.tool
```

Returns a hard-routed OIE message with `intercepted: true` — the LLM is never called.

## Configuration

| Variable | Default | Meaning |
|----------|---------|---------|
| `LLM_MODE` | `auto` | `auto` (Ollama then stub), `ollama`, or `stub` |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama base URL |
| `OLLAMA_MODEL` | `tinyllama` | Small free model for the prototype |

## Tests

```bash
pytest
```

## Assignment deliverables

| Deliverable | Location |
|-------------|----------|
| Working GitHub + Devcontainer | this repo (`.devcontainer/`, `README.md`) |
| Architecture diagram | [`docs/architecture-diagram.md`](docs/architecture-diagram.md) |
| Architecture narrative | [`docs/architecture-narrative.md`](docs/architecture-narrative.md) |
| Code provenance log | [`docs/CODE_PROVENANCE.md`](docs/CODE_PROVENANCE.md) |

Reference scoping / ADR Word docs live in [`docs/reference/`](docs/reference/).

## Design notes (why this shape)

- **Gateway owns policy**: interceptors are deterministic code, not prompt hopes.
- **Stateless**: no chat logs, no AndrewID — aligns with V1 FERPA mitigation.
- **Ollama for the prototype**: free local hosting for the assignment; production ADR targets a managed enterprise LLM API behind the same gateway pattern.
