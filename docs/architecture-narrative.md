# Architecture Narrative — V1 Student Support Q&A Prototype

**Course:** Cloud AI / Academy Learner Lab  
**System:** Minimal question-answering gateway for the CMU AI-Powered Student Support Pilot  
**Date:** July 19, 2026  
**Length target:** 1–2 pages

## What we built

We built a **stateless routing gateway** that accepts a student’s plain-English campus question and returns either (a) a hard-routed safety response or (b) a short answer grounded in a tiny set of official CMU knowledge snippets. The runnable prototype is a Python **FastAPI** service (`POST /ask`) with:

- **Input handling:** JSON body `{ "question": "..." }`.
- **Safety interceptors:** deterministic regex/keyword rules for visa/immigration topics (route to OIE) and mental-health crisis language (route to emergency / CaPS resources). Matched queries never reach a model.
- **Minimal retrieval:** keyword overlap against static snippets (academic calendar, financial aid overview, health insurance, libraries), each carrying a source URL.
- **Model step:** free local hosting via **Ollama** (`tinyllama` by default), with an automatic **stub** fallback so the end-to-end pipeline still works when no model daemon is available.
- **Stateless execution:** no chat history, no AndrewID, no persisted transcripts — matching the V1 “anonymous by default” FERPA mitigation from the scoping document.

This is intentionally the **smallest complete slice** of the larger pilot: question in → policy gate → answer out. We are not building the embedded portal chat UI, human-handoff ticket packaging, or admin analytics dashboard in this assignment cut.

## How this maps to the accepted architecture (ADR 001)

ADR 001 chose a **Decoupled Gateway Architecture**: clients never talk to the LLM directly; a CMU-owned gateway enforces “code as policy,” then calls a hosted model API and drops the session.

| ADR 001 element | Prototype implementation |
|-----------------|--------------------------|
| Custom routing gateway | FastAPI app in `src/gateway/` |
| Safety interceptors before LLM | `interceptors.py` |
| Managed enterprise LLM API | **Substituted** with Ollama for free local hosting |
| Stateless / no PII retention | No datastore; request-scoped only |
| Future edge hosting | Documented path: AWS API Gateway + Lambda in Learner Lab |

The substitution of Ollama for Azure OpenAI / AWS Bedrock is deliberate for the assignment: we need a working Q&A capability without paid model spend, while preserving the same control plane (gateway + interceptors + pluggable backend). Swapping `LLM_MODE` / the client adapter is enough to point the identical gateway at a managed API later.

## Cloud services integrated (and why)

### Used in the local / Devcontainer prototype

| Service / component | Role | Why this choice |
|---------------------|------|-----------------|
| **Ollama** (local) | Free model hosting | Zero token cost; reproducible in a Devcontainer; enough for a demo Q&A path. |
| **Dev Container (Docker)** | Reproducible engineering environment | Teammates clone → reopen in container → same Python + tooling without “works on my machine.” |
| **GitHub** | Source of truth + submission link | Required delivery surface for the working environment, docs, and provenance. |

### Target / Learner Lab path (aligned with ADR, not required to demo locally)

| Cloud service | Role | Why this choice |
|---------------|------|-----------------|
| **AWS API Gateway** | Managed HTTPS front door | Standard Academy/AWS pattern; throttling and auth hooks without operating a fleet of reverse proxies. |
| **AWS Lambda** | Host the gateway logic serverless | Fits a short-lived, stateless request model; matches “no dedicated MLOps staff” and unknown pilot traffic. |
| **Managed LLM API (Azure OpenAI or AWS Bedrock)** | Production model hosting | BAA / enterprise terms and zero-data-retention options the ADR requires; removes GPU CapEx and MLOps burden for V1. |

We are **not** self-hosting a GPU cluster for the pilot. ADR 001 rejected that path because of capital cost and missing MLOps headcount. Ollama in this repo is a **development stand-in**, not a contradiction of the ADR: it keeps the gateway contract identical while the assignment runs on free compute.

## Technical justification (summary)

1. **Risk lives in the gateway, not the model.** Visa and crisis topics must be computationally blocked. Prompt-only controls are insufficient; interceptors enforce institutional policy before generation.
2. **Stateless beats personalized for V1.** Skipping login and storage avoids a FERPA-heavy build and still answers high-volume logistics questions.
3. **Pluggable model backend.** Stub proves the pipeline in CI/classrooms without GPUs; Ollama proves real generation for free; managed cloud LLM is the production target behind the same interface.
4. **Devcontainer first.** The assignment grades a reproducible teammate experience as much as the demo itself — Dockerfile + `devcontainer.json` + explicit README commands close that loop.

## What is explicitly out of scope for this cut

- Portal-embedded chat UI and WCAG chrome  
- Ticket / human-handoff packaging  
- Daily web crawl of CMU handbooks  
- Personalized SIS / financial-aid eligibility  
- CPT/OPT interpretation (hard-blocked by design)

Those remain future increments on top of this gateway skeleton.
