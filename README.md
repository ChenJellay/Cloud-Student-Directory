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
- **Python 3.9+** (3.10+ preferred) and [Ollama](https://ollama.com/) installed locally
- Git

> FastAPI / Pydantic v2 need Python ≥ 3.8. AWS Cloud9 often defaults to **Python 3.7** — that will fail `pip install`. See [Learner Lab / Cloud9](#learner-lab--cloud9) below.

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
python3 --version   # must be 3.9+
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Optional: real answers via Ollama
ollama serve   # separate terminal
ollama pull tinyllama

# Stub-only (no Ollama required) — proves end-to-end pipeline
LLM_MODE=stub uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
```

## Learner Lab / Cloud9

Cloud9’s default `python3` is often **3.7**. Recreate the venv with a newer interpreter:

```bash
# 1) See what you have
python3 --version
ls /usr/bin/python3*

# 2) Install Python 3.9 on Amazon Linux 2 Cloud9 (typical Learner Lab image)
sudo yum install -y python39 python39-devel

# (Amazon Linux 2023 instead:)
# sudo dnf install -y python3.9 python3.9-devel

# 3) Blow away the old 3.7 venv and recreate
deactivate 2>/dev/null || true
rm -rf .venv
python3.9 -m venv .venv
source .venv/bin/activate
python --version          # confirm 3.9.x
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4) Run (stub mode — no Ollama needed on Cloud9)
LLM_MODE=stub uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8080
```

If `yum`/`dnf` has no `python39`, try `python3.11` / `python311`, or:

```bash
sudo amazon-linux-extras enable python3.8
sudo yum install -y python3.8 python3.8-devel
python3.8 -m venv .venv
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
