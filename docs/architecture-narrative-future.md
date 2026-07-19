# Architecture Narrative — Future State (ADR / Production Target)

**Course:** Cloud AI / Academy Learner Lab  
**Scope:** Intended production architecture from ADR 001 and the V1 scoping document  
**Date:** July 19, 2026  
**Status:** Target design — not fully deployed in this checkpoint

## What we intend to build next

The long-term V1 pilot is a **decoupled gateway architecture**: students never call an LLM directly. A CMU-owned routing layer enforces institutional policy, grounds answers in official sources, calls a **managed enterprise LLM API**, and remains **stateless / anonymous by default** to limit FERPA exposure.

Compared with today’s FastAPI + Stub/Ollama prototype, the future system packages the same control plane onto AWS and swaps the model backend to a BAA-backed cloud LLM.

## Target components

| Component | Role |
|-----------|------|
| **Embedded portal chat** | Student-facing UI inside existing campus surfaces (accessible, mobile-friendly). |
| **AWS API Gateway** | Managed HTTPS edge: throttling, routing, operational controls. |
| **AWS Lambda** | Hosts the gateway logic (interceptors, retrieval client, model client) without a long-lived app server. |
| **Safety interceptors** | Same “code as policy” idea as the prototype: visa/immigration and crisis topics never reach the model. |
| **Official knowledge ingest** | Approved CMU pages/handbooks/FAQs become the only grounding corpus; every answer cites a source URL. |
| **Managed LLM API** | Azure OpenAI or AWS Bedrock with enterprise terms, BAA where required, and zero-data-retention configuration. |
| **Human handoff** | Explicit path to Hub / OIE / emergency resources when the system must not answer. |

## Cloud services (future) and why those choices

| Cloud service | Why |
|---------------|-----|
| **AWS API Gateway** | Standard Academy/AWS pattern; edge controls without operating custom reverse proxies. |
| **AWS Lambda** | Fits short-lived, stateless requests; matches “no dedicated MLOps staff” and unknown pilot traffic. |
| **Azure OpenAI or AWS Bedrock** | ADR 001 rejected self-hosted GPUs for V1 CapEx/MLOps cost; managed APIs provide retention and compliance levers the university needs. |

Ollama in the current prototype is a **development stand-in**, not the production host. The gateway interface stays the same so the backend can be swapped without redesigning policy enforcement.

## Alternatives considered (from ADR 001)

1. **Self-hosted open-source model on EC2/GPU** — strong data sovereignty, but capital cost and MLOps headcount we do not have for V1.  
2. **Direct SaaS chatbot wrapper** — fast, but opaque routing and inherent logging conflict with anonymous/stateless FERPA mitigation.  
3. **Chosen path: CMU gateway + managed LLM API** — trade infrastructure ownership for policy control where institutional risk lives.

## Continuity with the current prototype

| Concern | Current prototype | Future state |
|---------|-------------------|--------------|
| Policy enforcement | Regex/keyword interceptors in FastAPI | Same rules in Lambda gateway |
| Model call | Stub or Ollama | Managed cloud LLM API |
| Hosting | Cloud9 / Devcontainer process | API Gateway + Lambda |
| Knowledge | Static snippets | Ingested official corpus |
| Privacy | No server-side chat store | Anonymous by default; scrubbed retention only if mandated |

## Triggers to revisit (ADR)

- Token spend exceeds amortized self-hosting + MLOps cost  
- V2 requires stateful SIS personalization (may force on-prem / private model hosting)  
- Open-source serving cost/performance becomes trivially cheap  

## Out of scope even in future V1 (per scoping doc)

- Personalized advising (“Am I eligible…?”)  
- Interpreting CPT/OPT / immigration law  
- Mental-health triage beyond emergency routing  
- Generative actions (registering a student, sending mail on their behalf)

See also: `docs/architecture-diagram-future.md` and `docs/reference/ADR 001_ Model Hosting and Routing Architecture.docx`.
