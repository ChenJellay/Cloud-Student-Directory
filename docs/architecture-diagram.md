# Architecture Diagram — V1 Minimal Q&A Prototype

Labeled starting architecture for the student-support question-answering capability. Every box has a one-line description.

## Component map

```mermaid
flowchart TB
  subgraph Client["Client layer"]
    U["Student / Tester\nOne-liner: Person who submits a plain-English campus question."]
    CLI["curl / HTTP client\nOne-liner: Thin client that POSTs JSON to the gateway /ask endpoint."]
  end

  subgraph Gateway["CMU-owned Routing Gateway (this repo)"]
    API["FastAPI App (src/gateway/main.py)\nOne-liner: Stateless HTTP API that accepts questions and returns answers + sources."]
    INT["Safety Interceptors\nOne-liner: Deterministic keyword/regex rules that hard-route visa and crisis queries before any LLM call."]
    RET["Knowledge Retriever\nOne-liner: Tiny keyword matcher over a static corpus of official CMU policy snippets."]
    CFG["Settings / Env Config\nOne-liner: Selects stub vs Ollama backend and model host without code changes."]
  end

  subgraph Model["Model hosting (prototype vs target)"]
    OLL["Ollama Runtime\nOne-liner: Free local model server used for the assignment prototype."]
    MOD["tinyllama (or similar)\nOne-liner: Small open model that turns question + snippets into a short answer."]
    STUB["Stub Backend\nOne-liner: Mock responder that proves the end-to-end pipeline when Ollama is offline."]
    CLOUD["Managed Cloud LLM API target\nOne-liner: Future Azure OpenAI / AWS Bedrock tenant with BAA and zero-retention for production V1."]
  end

  subgraph Knowledge["Knowledge boundary"]
    KB["Static Knowledge Snippets\nOne-liner: Hand-curated official calendar / aid / health / library blurbs with source URLs."]
  end

  subgraph FutureCloud["Academy / cloud path (documented, not required for local demo)"]
    APIGW["AWS API Gateway\nOne-liner: Managed edge entrypoint that would front the gateway in Learner Lab deployments."]
    LAMBDA["AWS Lambda\nOne-liner: Serverless compute host for the same routing logic without a long-lived server."]
  end

  U --> CLI --> API
  API --> INT
  INT -->|safe question| RET
  INT -->|matched high-risk| API
  RET --> KB
  RET --> CFG
  CFG -->|LLM_MODE=ollama/auto| OLL --> MOD
  CFG -->|LLM_MODE=stub or Ollama down| STUB
  MOD --> API
  STUB --> API
  API -.->|same gateway pattern| APIGW --> LAMBDA
  LAMBDA -.-> CLOUD
```

## Component checklist (label + one-liner)

| Component | One-line description |
|-----------|----------------------|
| Student / Tester | Person who submits a plain-English campus question. |
| curl / HTTP client | Thin client that POSTs JSON to the gateway `/ask` endpoint. |
| FastAPI App | Stateless HTTP API that accepts questions and returns answers + sources. |
| Safety Interceptors | Deterministic keyword/regex rules that hard-route visa and crisis queries before any LLM call. |
| Knowledge Retriever | Tiny keyword matcher over a static corpus of official CMU policy snippets. |
| Settings / Env Config | Selects stub vs Ollama backend and model host without code changes. |
| Static Knowledge Snippets | Hand-curated official calendar / aid / health / library blurbs with source URLs. |
| Ollama Runtime | Free local model server used for the assignment prototype. |
| tinyllama | Small open model that turns question + snippets into a short answer. |
| Stub Backend | Mock responder that proves the end-to-end pipeline when Ollama is offline. |
| Managed Cloud LLM API (target) | Future Azure OpenAI / AWS Bedrock tenant with BAA and zero-retention for production V1. |
| AWS API Gateway (path) | Managed edge entrypoint that would front the gateway in Learner Lab deployments. |
| AWS Lambda (path) | Serverless compute host for the same routing logic without a long-lived server. |

## Request path (happy path)

1. Client `POST /ask` with `{ "question": "..." }`.
2. Interceptors scan for visa/immigration or mental-health crisis language.
3. If matched → return hard-routed official guidance; **no model call**.
4. If safe → retrieve 1–2 knowledge snippets → call Ollama (or stub) → return answer + source URLs + disclaimer.
5. Drop session state (nothing persisted).
