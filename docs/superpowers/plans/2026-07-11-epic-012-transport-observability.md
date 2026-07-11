# Epic-012 Transport & Observability Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Provide a standard-library application transport, safe execution observation, pre-call operational limits, rollback validation, and an opt-in live validation hook.

**Architecture:** Keep concrete transport, observation, limits, and validation wrappers inside `skill.ai.application`. Preserve the existing provider and runtime contracts; translate urllib failures into existing provider errors and keep all business content outside metadata.

**Tech Stack:** Python standard library (`urllib`, `json`, `time`, `unittest`).

## Global Constraints

- Do not modify Skill Core, Agent, backend, or frontend modules.
- Do not add providers, SDKs, HTTP dependencies, MCP, LangChain, RAG, embeddings, vector databases, or multi-agent workflows.
- Do not read credentials or endpoints from production code environment variables.
- Preserve all existing uncommitted Epic changes.

---

### Task 1: Standard-library Transport

**Files:**
- Create: `skill/ai/application/transports/__init__.py`
- Create: `skill/ai/application/transports/urllib_transport.py`
- Modify: `skill/ai/providers/openai/provider.py`
- Modify: `skill/ai/application/__init__.py`
- Modify: `skill/ai/__init__.py`
- Test: `tests/test_ai_application_transport.py`

**Interfaces:**
- `UrllibHTTPTransport(base_url: str, opener=None)` implements `post(path, headers, body, timeout) -> dict`.
- Provider timeout, unavailable, and response errors pass through `OpenAICompatibleProvider` unchanged.

- [ ] Write tests for POST method, JSON body, headers, timeout, dict decoding, timeout/HTTP/connection/invalid-JSON mappings, and transport instance reuse.
- [ ] Run focused tests and confirm missing implementation failure.
- [ ] Implement urllib transport and provider-error pass-through.
- [ ] Run focused tests and existing OpenAI provider tests.

### Task 2: Observer and Operational Limits

**Files:**
- Create: `skill/ai/application/observability.py`
- Create: `skill/ai/application/limits.py`
- Create: `skill/ai/application/service.py`
- Modify: `skill/ai/application/adapters/runtime.py`
- Modify: `skill/ai/application/__init__.py`
- Modify: `skill/ai/__init__.py`
- Test: `tests/test_ai_application_operations.py`
- Test: `tests/test_ai_application_runtime.py`

**Interfaces:**
- `AIExecutionObserver.observe(request_context, started_at, ended_at, result) -> AIExecutionMetadata`.
- `AIApplicationLimits(max_prompt_characters=12000, max_context_items=100, allow_live_requests=False)` validates before delegation without mutating content.
- `ApplicationEnhancementService` validates and delegates while preserving `AIEnhancementResult`.

- [ ] Write tests for safe metadata, latency/status, prompt/context/live limits, non-mutation, structured rejection, and rollback without dependency access.
- [ ] Run focused tests and confirm missing types and behavior fail.
- [ ] Implement observer, limits, wrapper, and optional adapter limits injection.
- [ ] Run focused and application runtime tests.

### Task 3: Opt-in Live Hook and Documentation

**Files:**
- Create: `tests/live/test_openai_transport_live.py`
- Modify: `docs/provider-integration.md`
- Modify: `docs/credential-boundary.md`
- Modify: `docs/ai-architecture.md`
- Modify: `CHANGELOG.md`
- Modify: `PROJECT.md`
- Modify: `NEXT_TASK.md`

**Interfaces:**
- Live hook requires `RUN_LIVE_AI_TEST=true` and an external `NEXTMOVE_LIVE_TRANSPORT_FACTORY` import path; missing configuration skips safely.

- [ ] Add a default-skipped external live validation hook without endpoint or credential data.
- [ ] Document transport ownership, safe metadata, limits, rollback, and no-network default tests.
- [ ] Update Epic status and recommend AI enhancement quality validation or v0.6.0 release preparation for Epic-013.
- [ ] Run full unittest, compileall, and diff checks.
