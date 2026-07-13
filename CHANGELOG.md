# NextMove Changelog

## Unreleased

## Epic-025.3 - Evidence-based Match Explanation

- Status: Completed
- Added internal requirement-evidence and match-explanation contracts with
  deterministic strengths, gaps, and risks derived from professional evidence.
- Integrated explanation building into `JobMatcher` without changing the
  six-field `JobMatchResult`, Skill API, Agent contract, Application Layer, or
  CLI behavior.
- Kept `unknown` distinct from `missing`, so absent resume evidence is reported
  conservatively and cannot pollute `missing_skills`.
- Added HR, cross-domain career-transition, insufficient-information, empty
  evidence, and evidence-privacy regression coverage without retaining raw
  resumes or job descriptions or introducing provider or network dependencies.

## Epic-025.1 - Domain-aware Job Matching

- Status: Completed
- Replaced the global technical-keyword scoring path with deterministic career
  domain and job-family classification inside `skill/matching/`.
- Added provider-neutral Domain, Skill, and Qualification scoring with
  explainable strengths and gaps, conservative missing-evidence language, and
  stable low-information behavior.
- Added focused English and Chinese coverage for HR, technology, finance,
  operations, unsupported occupations, ambiguous roles, and weak job
  descriptions.
- Preserved the six-field `JobMatchResult`, `NextMoveSkill.run("match_job", ...)`,
  Agent Tool schemas, CLI behavior, and application-to-Skill dependency direction.

## Epic-025.2 - Career Stage Model

- Status: Completed
- Added the internal, evidence-based Career Stage model: `entry`,
  `developing`, `experienced`, `advanced`, and `unknown`.
- Added deterministic experience, responsibility, and impact signals with
  conservative low-confidence handling for insufficient resume evidence.
- Mapped internal stages to the existing legacy `career_level` contract without
  changing Skill APIs, Agent schemas, `JobMatchResult`, the Application Layer,
  or CLI behavior.
- Tailored existing career-advice wording to internal stage evidence while
  preserving the public `CareerAdviceResult` structure.

## Epic-024.2 - Agent-first Pilot Kit Implementation

- Status: Completed
- Added a five-minute Agent-first Quick Start for non-technical job seekers.
- Added public-safe fictional resume and job-description samples that execute
  the complete offline `career_analysis` workflow.
- Added four copyable Agent Prompt templates and a user-language output guide
  without changing the Skill or CLI contract.
- Added a platform-neutral anonymous feedback template, Pilot guidelines, and
  a secondary GitHub Issue channel with explicit privacy boundaries.
- Added focused Pilot Kit acceptance coverage while keeping CLI UX changes,
  telemetry, Web, backend, database, and new providers out of scope.

## 0.8.0 - Skill Developer Preview

## Epic-023 - v0.8.0 Release Finalization

- Status: Completed
- Marked the v0.8.0 codebase Developer Preview Ready while keeping tag creation
  and publication as separate human-approved actions.
- Clarified the compatible legacy, Skill, and CLI entrypoints in `skill.json`
  and release-facing documentation without changing runtime behavior.
- Made README the primary user entry point, removed duplicated and corrupted
  text, and documented Python 3.11+, offline build prerequisites, and input
  contract differences.
- Added a truthful Agent compatibility matrix and deferred
  `--job-description-file` until post-release feedback justifies the added CLI
  behavior and regression surface.
- Added the missing Epic-020 plan records and the Epic-023 design and execution
  records to preserve development history.

## Epic-022 - Skill Operational Readiness

- Status: Completed
- Added the offline `python -m skill` and installed `nextmove analyze` CLI
  entrypoints for `career_analysis`.
- Added Agent discovery-to-invocation acceptance coverage for manifest fields,
  CLI normalization, JSON success and failure responses, and serialization.
- Unified capability descriptions across runtime metadata and `skill.json`,
  expanded Agent instructions, and added the v0.8.0 release note.
- Preserved the required Python/Agent `job_description` contract and all
  Skill-to-Application dependency boundaries.

## Epic-021 - Skill Productization

- Status: Completed
- Added the public `career_analysis` capability and structured,
  JSON-serializable `CareerAnalysisReport` with fixed-order fail-fast behavior.
- Added `skill.json` product metadata and Agent-facing `SKILL.md` for ChatGPT
  Agent, Claude Agent, Cursor, and Codex consumers.
- Added a fully offline Skill demo that invokes `career_analysis` and prints a
  JSON report.
- Preserved compatibility for the four existing public capabilities and kept
  the Skill independent from Web, FastAPI, databases, authentication, frontend,
  network, and Application Layer imports.

## Epic-020.3 - Application Execution Metadata Contract

- Status: Completed
- Added application-owned immutable UTC ISO-8601 execution metadata for valid
  workflow success and failure results.
- Preserved the established application response contract and failure-step
  information without adding transport, provider, or dependency concerns.

## Epic-020.2 - Application Request Boundary Validation

- Status: Completed
- Added `CareerAnalysisRequest` validation for string and `ResumeProfile` inputs,
  optional job-description normalization, and fail-fast application validation.
- Stabilized success and failure JSON response contracts and strengthened both
  directions of the Application/Skill dependency boundary tests.

## Epic-020.1 - Product Application Layer Boundary

- Status: Completed
- Added a standalone, application-owned career-analysis service, schemas, and
  workflow that compose the stable public `NextMoveSkill.run()` API.
- The workflow executes resume analysis, improvement, job matching, and career
  advice in a fixed order, stops at the first unsuccessful Skill response, and
  preserves the original structured `SkillError` in its application response.
- Added deterministic coverage for the success path, first-step and matching
  failures, JSON serialization, service delegation, and the one-way
  Skill-to-application dependency boundary.

## 0.7.0

- AI Enhancement Quality System, Prompt and Output Contracts, Quality Validation,
  Live Pilot Boundary, Human Review Workflow, Artifact Retention, Controlled Export,
  and Release Hardening.

## Epic-016 - Real Provider Quality Pilot

- Added opt-in, content-safe pilot review records for external real-provider validation.

## Epic-015 - AI Enhancement Prompt & Output Contract Refinement

- Added the versioned `resume-improvement.v1` prompt and validated internal
  JSON output contract for resume enhancement.
- Invalid provider text now degrades to the existing structured provider
  response error without exposing parser details.

## Epic-014 - AI Enhancement Quality Validation

- Added eight fully synthetic offline quality fixtures, deterministic quality
  checks, a content-safe JSON/Markdown runner, and an opt-in live observation
  boundary.
- Added Core-versus-AI immutability and provider failure regression coverage.
- Empty provider content now maps to the existing structured response-error
  result rather than a successful empty enhancement.

## 0.6.0

### Added

- Optional AI Enhancement Layer, `AIProvider` contract, provider registry and
  factory, credential boundary, and `AIRuntime` assembly.
- OpenAI-Compatible Provider Adapter, injected `HTTPTransport`, resume AI
  enhancement, provider runtime policy, health checks, and `AIRequestContext`.
- `ApplicationRuntimeAdapter`, feature flags, `AIExecutionMetadata`,
  `UrllibHTTPTransport`, safe observability, application limits, safe rollback,
  opt-in live validation, and an offline enhancement demonstration.

### Security / Privacy

- The Skill neither stores nor reads credentials; default tests do not access
  the network.
- Observability never records prompts, resumes, job descriptions, credentials,
  or response bodies.
- Provider failures return structured results and do not affect the rule-based
  Skill Core.

### Compatibility

- Existing `NextMoveSkill` APIs remain compatible.
- Skill Core and Agent Layer do not depend on `skill.ai`.
- AI Enhancement is optional and can be disabled before any credential,
  provider, or transport work occurs.

## Epic-012 - Application Transport & Observability Validation

- Status: Completed
- Added reusable `UrllibHTTPTransport` using only Python standard library JSON
  POST support and stable timeout, unavailable, and response error mapping.
- Added safe `AIExecutionObserver`, conservative `AIApplicationLimits`, and an
  application enhancement wrapper that rejects invalid calls before provider
  generation without modifying input.
- Preserved explicit feature rollback before credential, provider, or
  transport access and added an externally assembled, default-skipped live
  transport validation hook.
- Added deterministic transport, observability, limits, rollback, and live
  boundary tests without endpoints, credentials, SDKs, or new AI capability.

## Epic-011 - Application Provider Runtime Integration MVP

- Status: Completed
- Added `ApplicationRuntimeAdapter` to compose application-owned settings,
  credential source, provider factory, transport, and feature policy around
  the unchanged `AIRuntime`.
- Added `AIFeaturePolicy` with early disabled behavior that avoids credential
  lookup, provider creation, and transport use while preserving structured AI
  failure results.
- Added metadata-only `AIExecutionMetadata` and documented application
  ownership of secret storage, environment access, key rotation, and transport.
- Added deterministic application runtime tests without a live provider,
  network client, SDK, or new AI capability.

## Epic-010 - Production Provider Operations MVP

- Status: Completed
- Added credential-free `ProviderRuntimePolicy` and transient,
  metadata-only `AIRequestContext` contracts to the optional AI layer.
- Added a backwards-compatible default `AIProvider.health_check()` and
  policy-aware enhancement execution with disabled/unhealthy structured
  fallback and opt-in additional retries.
- Added a default-skipped `tests/live/` boundary controlled by
  `RUN_LIVE_AI_TEST=true`; no live API call, credential loading, or new
  provider was added.

## Epic-009.6 - First Real Provider Integration

- Status: Completed
- Added an injected-transport `OpenAICompatibleProvider` that maps generic AI
  requests to OpenAI-compatible Chat Completions payloads and parses responses.
- Added the AI-layer `ResumeAIEnhancer` and `ResumeImprovementPrompt` to
  optionally enhance `ResumeImprovementResult` without changing Skill Core.
- Added deterministic tests for request mapping, response parsing, provider
  error mapping, and the resume enhancement workflow; no live API calls run by
  default.

## Epic-009.5 - Provider Integration Readiness Review

- Status: Completed
- Added the Provider Integration Standard covering adapter responsibility,
  credential ownership, SDK isolation, error mapping, tests, and first-provider
  approval criteria.
- Kept the Skill Core, Agent Layer, and all runtime contracts free of SDKs,
  credentials, environment loading, and network calls.

## Epic-009.4 - Credential & Runtime Boundary

- Status: Completed
- Added the abstract `CredentialProvider` and `ProviderFactory` boundaries for
  externally supplied credentials and future adapter construction.
- Added `AIRuntime` to assemble settings, credentials, factories, registry, and
  `EnhancementService` without a real provider integration.
- Added runtime tests for credential lookup, assembly, missing credentials, and
  factory failures without SDKs, network access, environment loading, secrets,
  or new dependencies.

## Epic-009.3 - Provider Adapter Integration Readiness

- Status: Completed
- Added `BaseProviderAdapter`, `MockProviderAdapter`, and credential-free
  `AIProviderSettings` for future adapter implementations.
- Added stable unavailable, timeout, and response provider error contracts and
  mapped them through `EnhancementService` to structured results.
- Added adapter, settings, and error-conversion tests without an SDK, network
  call, secret, environment loading, or new dependency.

## Epic-009.2 - AI Provider Contract & Prompt Boundary

- Status: Completed
- Added the provider-neutral `AIProviderConfig` data boundary and an
  externally managed `ProviderRegistry` for named provider instances.
- Added the abstract `PromptTemplate` contract without production prompt text.
- Extended `EnhancementService` to resolve a registered provider by name at
  construction while preserving direct provider injection.
- Added contract tests without introducing any provider SDK, network call,
  credential handling, or new dependency.

## Epic-009.1 - AI Enhancement Boundary MVP

- Status: Completed
- Added an optional, provider-neutral `skill.ai` boundary with an abstract
  `AIProvider`, structured `AIEnhancementResult`, and injected
  `EnhancementService`.
- Kept the existing Skill Core, Agent runtime, backend, and frontend unchanged.
- Added contract tests for provider subclasses, successful enhancements,
  missing providers, provider exceptions, and public imports.
- Added architecture documentation and a prompt-directory boundary note without
  introducing an SDK, network call, credential, configuration system, or new
  dependency.

## Epic-008.5 - Post Release Validation

- Status: Completed
- Added a GitHub-facing Career Intelligence workflow output guide with a
  fictional, structured JSON example.
- Polished the README release entry point with release and test badges,
  installation guidance, a minimal runnable workflow, and demo documentation.
- Validated the public Skill install, workflow demo, unit tests, and Python
  compilation after the v0.5.0 release.

## 0.5.0

- Status: Release preparation complete
- Added the initial public release scope for the standalone AI Career
  Intelligence Skill:
  - Resume Analysis
  - Resume Improvement
  - Job Matching
  - Career Advice
- Added the provider-neutral Agent Tool Schema and Tool Registry.
- Added `AgentRuntime` for registered Agent Tool invocation.
- Added GitHub-facing documentation for the Skill API, architecture,
  contribution model, and release workflow.
- Added runnable examples, including the full career analysis workflow.

## Epic-004.3 - Package Polish & Release Preparation

- Status: Completed
- Completed:
  - Added `skill/__version__.py` as the single source of truth for Skill package version.
  - Updated `skill/metadata.py` to use the shared package version.
  - Expanded `skill/__init__.py` public exports to include `NextMoveSkill`, `SkillResponse`, `SkillError`, and `__version__`.
  - Added a minimal `pyproject.toml` for future editable installs and packaging readiness.
  - Added package import tests for public API exports and metadata version consistency.
  - Added README installation guidance with `pip install -e .`.

## Epic-004.2 - Skill Packaging Readiness

- Status: Completed
- Completed:
  - Added `skill.utils.to_dict()` for JSON-serializable Skill result, `SkillResponse`, and `SkillError` conversion.
  - Added `skill/metadata.py` with Skill name, version, capabilities, and Agent discovery description.
  - Added Skill usage documentation to `README.md`, including initialization, `run()` calls, capabilities, and input/output examples.
  - Added runnable examples for resume analysis and job matching.
  - Added serialization and metadata tests.

## Epic-004.1 - Skill API Stabilization

- Status: Completed
- Completed:
  - Added provider-neutral `SkillError` and `SkillResponse` schemas for Agent-friendly calls.
  - Added `NextMoveSkill.run(capability, payload)` as a unified compatible API entrypoint.
  - Preserved direct methods and their original business result return types.
  - Renamed `match_job()` parameter from `job` to `job_description`.
  - Added structured success and error responses for supported capabilities, unknown capabilities, and invalid input.
  - Added tests covering all four capabilities through the unified Skill API.

## Epic-003.3 - Career Advice Skill

- Status: Completed
- Completed:
  - Added `skill/career/` with structured schema exports and a rule-based `CareerAdvisor`.
  - Added `CareerAdviceResult` with `current_level`, `possible_paths`, `skill_gaps`, and `recommended_actions`.
  - Connected `NextMoveSkill.career_advice()` to parse resumes when needed and reuse resume analysis when not provided.
  - Implemented first-pass career level inference, data/technical/management path detection, skill gap advice, and recommended actions.
  - Added unit tests for no-experience resumes, technical backgrounds, management backgrounds, and public Skill interface behavior.

## Epic-003.2 - Job Matching Skill

- Status: Completed
- Completed:
  - Added `skill/matching/` with structured schema exports and a rule-based `JobMatcher`.
  - Added `JobMatchResult` with `match_score`, `matched_skills`, `missing_skills`, `strengths`, `gaps`, and `recommendations`.
  - Connected `NextMoveSkill.match_job()` to parse resumes when needed and match against a job description string.
  - Implemented first-pass keyword matching, skill gap detection, and 0-100 scoring based on skill overlap plus work experience.
  - Added unit tests for high match, skill gaps, empty resume, and public Skill interface behavior.

## Epic-003.1 - Resume Improvement Skill

- Status: Completed
- Completed:
  - Added `skill/improvement/` with structured schema exports and a rule-based `ResumeImprover`.
  - Added `ResumeImprovementResult` with `issues`, `suggestions`, and `improved_sections`.
  - Connected `NextMoveSkill.improve_resume()` to parse, analyze, and improve resumes without AI provider dependencies.
  - Generated first-pass suggestions from analysis weaknesses for missing summaries, limited skills, missing skills, missing experience, missing projects, and unquantified outcomes.
  - Added unit tests for direct `ResumeImprover` use and the public Skill interface.

## Epic-002.4 - Skill Interface Integration

- Status: Completed
- Completed:
  - Connected `NextMoveSkill.analyze_resume()` to the Skill Core parser and analyzer.
  - Supported `str` input through `RuleBasedResumeParser.parse()`.
  - Supported `ResumeProfile` input through direct `ResumeAnalyzer.analyze()` execution.
  - Kept `improve_resume()`, `match_job()`, and `career_advice()` as explicit placeholders.
  - Added interface-level unit tests for text input, profile input, and placeholder responses.

## Epic-002.2 - Skill Core Bootstrap

- Status: Completed
- Completed:
  - Initialized standalone `skill/` core package.
  - Added first version of provider-neutral resume and analysis schemas.
  - Added `NextMoveSkill` interface with explicit placeholder responses.
  - Preserved existing FastAPI demo, backend structure, and frontend structure.

项目：

NextMove

Slogan：

Know Your Value.
Find Your Next Career Move.

Development Method：

Sprint + Task

----------------------------

# Sprint 0

## Task-001

- Status: Completed
- Objective: 初始化项目基础目录。
- Completed: 创建基础项目结构、README.md、PROJECT.md。

## Task-002

- Status: Completed
- Objective: 规范项目开发目录。
- Completed: 将项目迁移到 D 盘长期开发目录。

## Task-003

- Status: Completed
- Objective: 初始化 Frontend 项目。
- Completed: 创建 Next.js、TypeScript、Tailwind CSS、App Router、ESLint 前端基础项目。

----------------------------

# Sprint 1

## Task-004

- Status: Completed
- Objective: 初始化 Backend 项目。
- Completed: 创建 FastAPI 最小后端服务。

## Task-005

- Status: Completed
- Objective: 连接 Frontend 与 Backend。
- Completed: 前端读取 Backend API 并显示连接状态。

----------------------------

# Sprint 2

## Task-006

- Status: Completed
- Objective: 实现 Resume 本地文件选择与校验。
- Completed:
  - 本地文件选择
  - PDF/DOC/DOCX 支持
  - 文件大小校验（10MB）
  - 显示文件信息
  - 错误提示
- Knowledge:
  学习了：
  - HTML File Input
  - React State
  - 文件校验
