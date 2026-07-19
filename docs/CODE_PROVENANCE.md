# Code Provenance Log

Active log of human vs. agent-generated code for the V1 Q&A gateway prototype.  
Update this file whenever substantial new code or docs are added.

**Project:** CMU Student Support Q&A Gateway (minimal)  
**Primary tools:** Cursor (Composer / agent), human review by course team member(s)  
**Convention:** Paths are relative to the repository root.

---

## Summary

| Origin | Approximate share of this initial scaffold | Notes |
|--------|--------------------------------------------|-------|
| Agent-generated | ~95% of first commit scaffold | Application code, Devcontainer, docs drafts, tests |
| Human-validated | Scoping Document + ADR 001 (`.docx`) | Authored earlier; used as architectural source of truth |
| Human-validated | All agent output below | Reviewed for scope fit, safety wording, and run instructions |
| Human-written | Review logs & validations | Running tests, deploying the systems, testing the system on AWS, working with Git, etc. |

---

## File-by-file provenance

| Path | Origin | Generated / authored by | Human validation performed |
|------|--------|-------------------------|----------------------------|
| `Scoping Document_ AI-Powered Student Support Pilot.docx` | Human-written (prior) | Team / course authoring (with noted Gemini assistance in appendix) | Accepted as V1 scope baseline |
| `ADR 001_ Model Hosting and Routing Architecture.docx` | Human-written (prior) | Team technical lead | Accepted architectural decision |
| `.gitignore` | Agent-generated | Cursor agent | Reviewed — standard Python/Docker ignores |
| `requirements.txt` | Agent-generated | Cursor agent | Reviewed — pinned loosely for classroom installs |
| `pytest.ini` | Agent-generated | Cursor agent | Reviewed |
| `README.md` | Agent-generated | Cursor agent | Human must confirm commands after Learner Lab setup |
| `.devcontainer/Dockerfile` | Agent-generated | Cursor agent | Validate Ollama install on first container build |
| `.devcontainer/devcontainer.json` | Agent-generated | Cursor agent | Validate ports 8000 / 11434 forward correctly |
| `src/gateway/__init__.py` | Agent-generated | Cursor agent | N/A (package marker) |
| `src/gateway/config.py` | Agent-generated | Cursor agent | Reviewed env defaults (`LLM_MODE`, Ollama host/model) |
| `src/gateway/interceptors.py` | Agent-generated | Cursor agent | **Critical review:** keyword lists for visa + crisis routes |
| `src/gateway/knowledge.py` | Agent-generated | Cursor agent | Reviewed snippet accuracy / source URLs |
| `src/gateway/llm_client.py` | Agent-generated | Cursor agent | Reviewed stub fallback + Ollama `/api/generate` usage |
| `src/gateway/main.py` | Agent-generated | Cursor agent | Reviewed `/health`, `/ask`, `/mode`, UI static mount |
| `src/gateway/static/index.html` | Agent-generated | Cursor agent | Reviewed Stub/LLM toggle + chat transcript UX |
| `docs/LLM_SETUP.md` | Agent-generated | Cursor agent | Optional Ollama path for machines with enough disk |
| `src/__init__.py` | Agent-generated | Cursor agent | N/A |
| `tests/test_gateway.py` | Agent-generated | Cursor agent | Run `pytest`; extend if interceptors change |
| `docs/architecture-diagram.md` | Agent-generated (legacy stub) | Cursor agent | Redirects to current/future split |
| `docs/architecture-diagram-current.md` | Agent-generated | Cursor agent | Current-state only diagram |
| `docs/architecture-diagram-future.md` | Agent-generated | Cursor agent | Future/ADR-target diagram |
| `docs/architecture-narrative.md` | Agent-generated (legacy stub) | Cursor agent | Redirects to current/future split |
| `docs/architecture-narrative-current.md` | Agent-generated | Cursor agent | Current-state only narrative |
| `docs/architecture-narrative-future.md` | Agent-generated | Cursor agent | Future/ADR-target narrative |
| `docs/README.md` | Agent-generated | Cursor agent | Index of architecture docs |
| `docs/CODE_PROVENANCE.md` | Agent-generated (this file) | Cursor agent | Maintain on every subsequent change |
| `knowledge/README.md` | Agent-generated | Cursor agent | Reviewed |

---

## Peer review / validation process (team)

Use this checklist for agent-generated code before considering it submission-ready:

1. **Scope check:** Does the change stay within “minimal Q&A + gateway + Ollama/stub”?  
2. **Safety check:** Do interceptors still block OPT/CPT/visa and crisis language without calling the LLM?  
3. **Run check:** `pytest` passes; `LLM_MODE=stub` `/ask` returns a stub answer; with Ollama up, backend is `ollama`.  
4. **Docs check:** README commands match reality; diagram labels still accurate.  
5. **Provenance check:** New/changed files are added to the table above with origin + reviewer initials/date.

### Review log

| Date | Reviewer | What was reviewed | Outcome |
|------|----------|-------------------|---------|
| 2026-07-19 | Jerry Chen | Initial agent scaffold (gateway, devcontainer, docs) | Pending teammate sign-off after local/Learner Lab run |
| 2026-07-19 | Jerry Chen | Code deployability on AWS (ran on Cloud9) | Bare-minimum repo working as intended, code deploys on Cloud9 perfectly|
| 2026-07-19 | Jerry Chen | Architectural Mechanics (whether the backend & UX work as intended) | Code runs on Cloud9 stub mode works perfectly & LLM mode requires large disk space to run with Ollama |
| 2026-07-19 | Jerry Chen | Documentation Review | Looked through docs and all files produced by agent & made corrections manually, and provided additional instructions as needed |
| | | | |

---

## Rules going forward

- **Human-written:** code or prose typed/edited substantially by a teammate without AI drafting.  
- **Agent-generated:** produced primarily by an LLM assistant (Cursor, ChatGPT, Gemini, etc.), even if lightly edited.  
- **Hybrid:** note both — e.g. “Agent draft; human rewrote interceptor patterns.”  
- Never commit secrets. Never weaken interceptors without an explicit team decision recorded here.
