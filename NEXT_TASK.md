# Next Task

## Status

Epic-025.2 is complete on `codex/epic-025.2-career-stage-model`. The Skill Core
now derives an internal career-stage assessment from evidence, maps it to the
existing legacy `career_level` output, and tailors existing advice without
changing public Skill, Agent, Application, or CLI contracts.

## Recommended Next Step

Perform a human review and normal merge decision for the completed Epic-025.1
Domain-aware Job Matching branch and this Epic-025.2 Career Stage Model branch.
Validate their combined behavior against representative non-technical, technical,
and career-transition resumes before any new quality-model Epic is started.

## Notes

- Do not continue expanding the Application Layer until instructed.
- Keep `CareerStageAssessment` internal. Do not expose its stage, signals, or
  confidence through the Agent schema or existing public result dataclasses.
- Preserve legacy mapping: `entry -> junior`, `developing -> mid`,
  `experienced -> senior`, `advanced -> lead`, and `unknown -> unknown`.
- Treat years of experience, title text, and tenure as supporting evidence only;
  do not promote a resume to advanced stage without responsibility and impact
  evidence.
- Keep insufficient evidence deterministic: return internal `unknown` with low
  confidence and avoid fabricated career-stage advice.
- Keep the v0.8.0 tag, push, and GitHub Release flow paused until explicitly
  resumed.
- Do not add telemetry or retain resume, job-description, identity, contact,
  employer, credential, or raw Agent-conversation content during the Pilot.
- Do not implement `--job-description-file` before post-release feedback and a
  separate CLI input/error contract design.
- Keep `entrypoint` and `cli_entrypoint` mapped to `skill.__main__:main`; keep
  `skill_entrypoint` mapped to `NextMoveSkill.run`.
- Keep `career_analysis` ordered and fail-fast through the existing public
  `NextMoveSkill.run()` API.
- Keep `skill/__version__.py` as the only package version source.
- Keep the Product Application Layer transport-neutral and dependent only on
  public Skill contracts. It must call capabilities through
  `NextMoveSkill.run()` and never be imported by `skill/`.
- Preserve the fixed fail-fast workflow: `analyze_resume`, `improve_resume`,
  `match_job`, then `career_advice`. On failure, retain the original
  structured `SkillError` without exposing resume or job-description input.
- Keep Skill Core independent from backend, frontend, HTTP logic, file upload
  handling, prompt text, and AI provider SDKs.
- Preserve `AIProvider` as the only provider-facing contract and keep all
  provider failures structured through `AIEnhancementResult`.
- Keep provider instance lifecycle external to `ProviderRegistry` and
  `EnhancementService`.
- Keep `AIProviderSettings` credential-free and interpret its timeout in
  seconds only at an external application or provider-adapter boundary.
- Keep `CredentialProvider` and `ProviderFactory` abstract. Credentials remain
  opaque and externally owned; `AIRuntime` must return structured unavailable
  behavior when assembly cannot produce a provider.
- Keep future Provider SDK imports inside a dedicated provider adapter package,
  with integration and live tests opt-in only.
- Keep `OpenAICompatibleProvider` transport-injected: the Skill must not add an
  HTTP client, SDK, environment loading, or credential persistence.
- Keep `ProviderRuntimePolicy` credential-free and network-free. Default to an
  enabled provider, one generation attempt, and structured failure fallback.
- Keep `AIRequestContext` transient and metadata-only; never include prompts,
  credentials, resume content, or user-private data.
- Keep live tests opt-in through `RUN_LIVE_AI_TEST=true`; do not configure a
  live credential or transport inside this repository.
- Keep `ApplicationRuntimeAdapter` as dependency assembly only. Provider
  behavior, prompt handling, and AI calls remain in their existing layers.
- Keep `AIRuntime` transport-free and preserve
  `from skill.ai.runtime import AIRuntime`.
- Keep `AIExecutionMetadata` separate from `AIEnhancementResult` and free of
  prompts, resume text, credentials, and user data.
- Keep credential storage, environment reading, key rotation, and concrete
  transport ownership in the external Application Layer.
- Keep `UrllibHTTPTransport` standard-library-only and free of credential or
  environment ownership. Never log headers, request bodies, or responses.
- Keep `AIExecutionObserver` content-blind and `AIApplicationLimits`
  non-mutating. Live requests require explicit application permission.
- Keep live validation externally assembled and default-skipped; the repository
  must contain no endpoint, API key, or secret.
