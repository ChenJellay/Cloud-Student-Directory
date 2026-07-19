# CMU Student Support Q&A Gateway (V1 Minimal Prototype)

Minimal **question-answering** prototype for the AI-Powered Student Support Pilot.

This repo implements the **decoupled routing gateway** from ADR 001, with a free/local **Ollama** model backend instead of a paid cloud LLM API. Safety interceptors run *before* any model call.

Open the browser UI at `/` — toggle **Stub** / **LLM**, type a question, and read the continuing chat transcript.

## Prerequisites

- Docker Desktop (for Dev Containers), **or**
- **Python 3.9+** (3.10+ preferred) and optional [Ollama](https://ollama.com/)
- Git

> FastAPI / Pydantic v2 need Python ≥ 3.8. AWS Cloud9 often defaults to **Python 3.7**. If you lack `sudo`, install a user-space Python with `uv` (commands below).

---

## Launch from scratch (Learner Lab / Cloud9, no sudo)

Use **port 8080** for Cloud9 Preview (ports 8080–8082). Use **8000** locally if you prefer. Run every step in the **same** Cloud9 environment.

**Cloud9 note:** Stub mode is the supported demo path on small disks. LLM/Ollama needs ~2GB+ free — see [`docs/LLM_SETUP.md`](docs/LLM_SETUP.md).

```bash
# 0) Go home and clone (skip clone if the repo already exists)
cd ~
git clone https://github.com/ChenJellay/Cloud-Student-Directory.git
cd Cloud-Student-Directory
# If you already cloned earlier:
# cd ~/Cloud-Student-Directory && git pull origin main

# 1) Install uv (user-space; no sudo) and a modern Python
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"
uv python install 3.12

# 2) Create venv + install deps
rm -rf .venv
uv venv --python 3.12 .venv
source .venv/bin/activate
python --version
uv pip install -r requirements.txt

# 3) Start the gateway (stub works with no Ollama / no extra disk)
LLM_MODE=stub uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8080
```

Then, **in a second terminal in the same IDE**:

```bash
curl -s http://127.0.0.1:8080/health
# expect status=ok, llm_mode=stub; ollama_reachable may be false on Cloud9 — that is fine
```

**Open the UI**

- Cloud9: **Preview → Preview Running Application** (app must be on **8080**)
- Locally: http://127.0.0.1:8080/

In the UI: leave **Stub** selected on small disks. **LLM** works when Ollama is installed and has disk (status shows `ollama: ready`).

Optional API check:

```bash
curl -s http://127.0.0.1:8080/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Where can I find the academic calendar?","mode":"stub"}'
```

### Optional — real LLM answers (Ollama)

Requires ~2GB+ free disk. Full steps: [`docs/LLM_SETUP.md`](docs/LLM_SETUP.md).

```bash
# after ollama serve + ollama pull tinyllama
curl -s http://127.0.0.1:8080/health   # ollama_model_ready should be true
curl -s http://127.0.0.1:8080/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Where can I find the academic calendar?","mode":"llm"}'
```

---

## Launch from scratch (local Mac / Linux)

```bash
git clone https://github.com/ChenJellay/Cloud-Student-Directory.git
cd Cloud-Student-Directory

python3 --version   # must be 3.9+
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

LLM_MODE=stub uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/

---

## Devcontainer

1. Clone and open in VS Code / Cursor → **Reopen in Container**
2. After setup:

```bash
LLM_MODE=auto uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
```

3. Open http://127.0.0.1:8000/

---

## Repo layout

```
.
├── .devcontainer/
├── docs/
├── knowledge/
├── src/gateway/
│   ├── main.py              # API + mode toggle
│   ├── static/index.html    # Chat UI
│   └── ...
├── tests/
├── requirements.txt
└── README.md
```

## API

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | Chat UI |
| `GET` | `/health` | Liveness + current mode |
| `GET`/`POST` | `/mode` | Read/set `stub` or `llm` |
| `POST` | `/ask` | `{ "question": "...", "mode": "stub"\|"llm" }` |

## Configuration

| Variable | Default | Meaning |
|----------|---------|---------|
| `LLM_MODE` | `auto` | Startup default (`stub`, `llm`/`ollama`, or `auto`) |
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama base URL |
| `OLLAMA_MODEL` | `tinyllama` | Small free model for the prototype |

## Tests

```bash
pytest
```

## Assignment deliverables

| Deliverable | Location |
|-------------|----------|
| Working GitHub + Devcontainer | this repo |
| Architecture diagram | [`docs/architecture-diagram.md`](docs/architecture-diagram.md) |
| Architecture narrative | [`docs/architecture-narrative.md`](docs/architecture-narrative.md) |
| Code provenance log | [`docs/CODE_PROVENANCE.md`](docs/CODE_PROVENANCE.md) |

Reference docs: [`docs/reference/`](docs/reference/).

## Design notes

- **Gateway owns policy**: interceptors are deterministic code, not prompt hopes.
- **Stateless server**: browser keeps the chat transcript; the API does not store it.
- **Ollama for the prototype**: free local hosting; production ADR targets a managed enterprise LLM API behind the same gateway pattern.
