# Architecture Narrative — Current State (Implemented Prototype)

**Course:** Cloud AI / Academy Learner Lab  
**Scope:** What is built and runnable in this repository today  
**Date:** July 19, 2026

## What we built

We built a **stateless routing gateway** that accepts a student’s plain-English campus question and returns either (a) a hard-routed safety response or (b) a short answer. The runnable system is a Python **FastAPI** service with:

- **HTTP API:** `POST /ask` accepts `{ "question": "...", "mode": "stub"|"llm" }`.
- **Browser UI:** `GET /` serves a simple chat page with a Stub/LLM toggle, question textbox, and continuing transcript (browser-side only).
- **Safety interceptors:** deterministic regex/keyword rules for visa/immigration (route to OIE) and mental-health crisis language (emergency / CaPS resources). Matched queries never reach a model.
- **Minimal retrieval:** keyword overlap against static snippets (academic calendar, financial aid overview, health insurance, libraries), each with a source URL.
- **Model step:**
  - **Stub (default in lab):** returns a clear mock answer proving the pipeline.
  - **LLM (optional):** calls local **Ollama** (`tinyllama` by default) when the daemon is up and the model is pulled.
- **Health probe:** `GET /health` reports whether Ollama is reachable and whether the configured model is ready.
- **Stateless server:** no AndrewID, no persisted chat logs.

This is the **smallest complete slice** of the larger student-support pilot: question in → policy gate → answer out.

## What is running where

| Environment | What we use it for |
|-------------|--------------------|
| **AWS Academy Learner Lab / Cloud9** | Run and demo the gateway (typically Stub mode on small disks). |
| **GitHub** | Source of truth, submission link, teammate onboarding. |
| **Devcontainer** | Reproducible local/Codespaces engineering environment. |
| **Ollama (local, optional)** | Free model hosting when the machine has enough disk (~2GB+). |

We are **not** currently deploying API Gateway, Lambda, or a managed cloud LLM for this checkpoint. Those belong to the future-state narrative.

## Cloud / platform choices in the current build (and why)

| Choice | Why |
|--------|-----|
| **FastAPI gateway we own** | Keeps “code as policy” (interceptors) in CMU-controlled code, matching ADR 001’s decoupling idea even before cloud packaging. |
| **Stub backend** | Guarantees a runnable demo on constrained Cloud9 disks without GPU or large model downloads. |
| **Ollama as optional LLM** | Free local hosting for teammates with capacity; same `/ask` contract as a future managed API. |
| **Devcontainer + README** | A new teammate can clone and run without guessing versions or ports. |
| **GitHub** | Required delivery surface for code, diagram, narrative, and provenance. |

## What this current system deliberately does not include

- Portal-embedded production chat chrome  
- AWS API Gateway / Lambda packaging  
- Azure OpenAI / AWS Bedrock tenants  
- Live crawl of CMU handbooks  
- Personalized SIS / financial-aid eligibility  
- CPT/OPT interpretation (hard-blocked by interceptors)

## Assumptions and limitations

This prototype intentionally prioritizes demonstrating the overall architecture over implementing a production-ready system. Several simplifying assumptions were made to keep the scope appropriate for an initial cloud prototype.

- The knowledge base consists of a small, manually curated set of official CMU information rather than a continuously updated corpus.
- Retrieval is implemented using simple keyword matching instead of semantic vector search.
- Users remain anonymous, with no authentication, personalization, or persistent chat history.
- Stub mode is the recommended deployment option within the AWS Academy Learner Lab due to storage and compute constraints, while Ollama support is provided as an optional enhancement.
- The safety interceptors illustrate the policy enforcement pattern but are not intended to provide comprehensive moderation or institutional policy coverage.

These design decisions allow the team to validate the end-to-end gateway architecture while minimizing operational complexity during the initial development phase.

## How to verify current state

```bash
LLM_MODE=stub uvicorn gateway.main:app --app-dir src --host 0.0.0.0 --port 8080
curl -s http://127.0.0.1:8080/health
curl -s http://127.0.0.1:8080/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Where can I find the academic calendar?","mode":"stub"}'
```

Open `http://127.0.0.1:8080/` (Cloud9 Preview on port 8080) for the UI.

See also: `docs/architecture-diagram-current.md` and `docs/LLM_SETUP.md` (optional LLM).
