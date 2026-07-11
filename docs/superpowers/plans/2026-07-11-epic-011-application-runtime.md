# Epic-011 Application Runtime Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect application-owned dependencies to the existing AI runtime through a feature-gated adapter and safe execution metadata.

**Architecture:** Add a small `skill.ai.application` package whose adapter composes the unchanged `AIRuntime`. Keep transport and credentials externally owned, and represent feature controls and execution observations as pure data objects.

**Tech Stack:** Python standard library, dataclasses, unittest.

## Global Constraints

- Preserve `skill/ai/runtime.py` and `from skill.ai.runtime import AIRuntime`.
- Do not modify Skill Core or Agent modules.
- Do not add environment reading, secret adapters, FastAPI integration, provider SDKs, MCP, RAG, vector databases, or embeddings.

---

### Task 1: Feature Policy and Execution Metadata

**Files:**
- Create: `skill/ai/application/policy.py`
- Create: `skill/ai/application/__init__.py`
- Create: `skill/ai/metadata.py`
- Modify: `skill/ai/__init__.py`
- Test: `tests/test_ai_application_runtime.py`

**Interfaces:**
- Produces `AIFeaturePolicy(enabled: bool = True, enhancement_enabled: bool = True)`.
- Produces `AIExecutionMetadata(request_id: str, provider_name: str, model_name: str, latency: float, status: str)`.

- [ ] Write tests that import both types, verify defaults and explicit values, and verify metadata exposes only the five approved fields.
- [ ] Run `python -m unittest tests.test_ai_application_runtime` and confirm missing imports fail.
- [ ] Implement frozen, slotted dataclasses and public exports.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Application Runtime Adapter

**Files:**
- Create: `skill/ai/application/adapters/runtime.py`
- Create: `skill/ai/application/adapters/__init__.py`
- Modify: `skill/ai/application/__init__.py`
- Modify: `skill/ai/__init__.py`
- Test: `tests/test_ai_application_runtime.py`

**Interfaces:**
- Consumes `AIProviderSettings`, `CredentialProvider`, `ProviderFactory`, an opaque transport, and `AIFeaturePolicy`.
- Produces `build_runtime() -> AIRuntime` and `build_enhancement_service() -> EnhancementService`.

- [ ] Write tests proving runtime dependency identity, credential injection, enabled enhancement behavior, and disabled short-circuit behavior without credential lookup or provider creation.
- [ ] Run the focused tests and confirm missing adapter behavior fails.
- [ ] Implement the adapter with the feature check before `AIRuntime.build_enhancement_service()`.
- [ ] Run the focused tests and complete suite.

### Task 3: Credential Documentation and Project State

**Files:**
- Create: `docs/credential-boundary.md`
- Modify: `docs/provider-integration.md`
- Modify: `CHANGELOG.md`
- Modify: `PROJECT.md`
- Modify: `NEXT_TASK.md`

**Interfaces:**
- Documents application ownership of credentials and transport plus the future backend integration boundary.

- [ ] Document prohibited secret handling and the application-to-runtime flow.
- [ ] Record Epic-011 completion and recommend an operational observability/transport validation scope for Epic-012.
- [ ] Run `python -m unittest discover -s tests`.
- [ ] Run `python -m compileall skill tests`.
