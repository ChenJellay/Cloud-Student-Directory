# Optional LLM setup (Ollama)

Stub mode is enough for the assignment demo on small Cloud9 disks.  
LLM mode is fully supported when the machine has **~2GB+ free disk** and can run Ollama.

## Quick check

With the gateway running:

```bash
curl -s http://127.0.0.1:8080/health
```

Look for:

- `"ollama_reachable": true` — `ollama serve` is up
- `"ollama_model_ready": true` — `tinyllama` (or `OLLAMA_MODEL`) is pulled

If either is false, the UI **LLM** toggle still works, but `/ask` returns a clear setup error instead of crashing.

## Install Ollama (machine with enough disk)

Official Linux package is now `.tar.zst` (not `.tgz`).

```bash
df -h ~   # need ~2GB+ free

curl -L --fail -o /tmp/ollama-linux-amd64.tar.zst \
  "https://github.com/ollama/ollama/releases/download/v0.32.1/ollama-linux-amd64.tar.zst"
ls -lh /tmp/ollama-linux-amd64.tar.zst
file /tmp/ollama-linux-amd64.tar.zst   # must say Zstandard, not HTML

# Decompress (uv venv example)
cd /path/to/Cloud-Student-Directory
source .venv/bin/activate
source "$HOME/.local/bin/env" 2>/dev/null || true
uv pip install zstandard

python - <<'PY'
import zstandard as zstd
from pathlib import Path
src = Path("/tmp/ollama-linux-amd64.tar.zst")
dst = Path("/tmp/ollama-linux-amd64.tar")
with src.open("rb") as f_in, dst.open("wb") as f_out:
    zstd.ZstdDecompressor().copy_stream(f_in, f_out)
print("ok", dst.stat().st_size)
PY

mkdir -p "$HOME/.local"
tar -xf /tmp/ollama-linux-amd64.tar -C "$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
export LD_LIBRARY_PATH="$HOME/.local/lib/ollama:${LD_LIBRARY_PATH:-}"
ollama --version
```

On a normal laptop with Docker/Devcontainer, prefer the Devcontainer Ollama install or https://ollama.com/download.

## Run LLM mode

Terminal A:

```bash
export PATH="$HOME/.local/bin:$PATH"
export LD_LIBRARY_PATH="$HOME/.local/lib/ollama:${LD_LIBRARY_PATH:-}"
ollama serve
```

Terminal B:

```bash
export PATH="$HOME/.local/bin:$PATH"
export LD_LIBRARY_PATH="$HOME/.local/lib/ollama:${LD_LIBRARY_PATH:-}"
ollama pull tinyllama
curl -s http://127.0.0.1:11434/api/tags
```

Terminal C (gateway — Cloud9 Preview likes **8080**):

```bash
cd /path/to/Cloud-Student-Directory
source .venv/bin/activate
LLM_MODE=stub uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8080
```

Test:

```bash
curl -s http://127.0.0.1:8080/health
curl -s http://127.0.0.1:8080/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Where can I find the academic calendar?","mode":"llm"}'
```

Expect `"backend":"ollama"`. Or open the UI and toggle **LLM**.

## Config

| Variable | Default | Meaning |
|----------|---------|---------|
| `OLLAMA_HOST` | `http://127.0.0.1:11434` | Ollama API |
| `OLLAMA_MODEL` | `tinyllama` | Small model for demos |
| `LLM_MODE` | `stub` recommended in lab | Startup UI default; toggle can still switch |

## Disk-constrained labs (Cloud9)

Stay on **Stub**. The Q&A pipeline, interceptors, UI, and docs remain valid. LLM is an optional backend behind the same gateway.
