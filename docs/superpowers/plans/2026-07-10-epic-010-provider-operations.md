# Epic-010 Provider Operations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add policy, request metadata, health checking, opt-in live-test boundaries, and structured fallback to the optional AI layer.

**Architecture:** Keep all runtime controls in `skill.ai`; Provider policy and request context are pure dataclasses. `EnhancementService` checks its injected provider and policy before generation, while `AIProvider` supplies a compatible default health check.

**Tech Stack:** Python standard library, dataclasses, unittest.

## Global Constraints

- Do not modify `skill/resume`, `skill/analysis`, `skill/improvement`, `skill/matching`, `skill/career`, or `skill/agent`.
- Do not add providers, MCP, LangChain, RAG, vector databases, embeddings, SDKs, network clients, credential persistence, or environment-based credential loading.
- Default behavior is healthy, one generation attempt, and structured failure fallback.

---

### Task 1: Data Boundaries

**Files:**
- Create: `skill/ai/operations/policy.py`
- Create: `skill/ai/operations/__init__.py`
- Create: `skill/ai/context.py`
- Modify: `skill/ai/__init__.py`
- Test: `tests/test_ai_operations.py`

**Interfaces:**
- Produces `ProviderRuntimePolicy(enabled=True, timeout=None, max_retries=0, fallback_enabled=True)`.
- Produces `AIRequestContext(provider_name, model_name, capability, request_id)`.

- [ ] Write tests for policy defaults, explicit policy values, and request-context fields.
- [ ] Run `python -m unittest tests.test_ai_operations` and confirm the imports fail before implementation.
- [ ] Implement frozen/slotted dataclasses and public exports.
- [ ] Run `python -m unittest tests.test_ai_operations` and confirm success.

### Task 2: Health and Structured Runtime Fallback

**Files:**
- Modify: `skill/ai/providers/base.py`
- Modify: `skill/ai/enhancement/service.py`
- Test: `tests/test_ai_operations.py`

**Interfaces:**
- `AIProvider.health_check() -> bool` returns `True` by default.
- `EnhancementService(..., runtime_policy: ProviderRuntimePolicy | None = None)`.
- `enhance(prompt, context, request_context=None) -> AIEnhancementResult`.

- [ ] Write tests for health-check failure, disabled policy, default single call, one configured retry, and request-context compatibility.
- [ ] Run the focused test module and confirm the new behaviors fail.
- [ ] Add the default health check and minimal retry/structured-fallback behavior.
- [ ] Run the focused test module and all unit tests.

### Task 3: Live Boundary and Documentation

**Files:**
- Create: `tests/live/__init__.py`
- Create: `tests/live/test_live_ai_boundary.py`
- Modify: `docs/provider-integration.md`
- Modify: `CHANGELOG.md`
- Modify: `PROJECT.md`
- Modify: `NEXT_TASK.md`

**Interfaces:**
- Live tests run only when `RUN_LIVE_AI_TEST=true`; default discovery skips them.

- [ ] Write a live-boundary test guarded by `unittest.skipUnless`.
- [ ] Run default discovery and confirm the test is skipped.
- [ ] Document policy, context, health, retry, fallback, and live-test constraints; update project status for Epic-010.
- [ ] Run `python -m unittest discover -s tests` and `python -m compileall skill tests`.
