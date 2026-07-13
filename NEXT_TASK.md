# Next Task

## Status

Epic-025.1, Epic-025.2, and Epic-025.3 are complete. Job matching now uses
deterministic domain, job-family, skill, and qualification evidence and builds
an internal evidence-based explanation, while resume analysis and career advice
share an internal evidence-based stage model. The public six-field
`JobMatchResult`, legacy career-level values, Skill API, Agent contract,
Application Layer, and CLI remain unchanged.

## Recommended Next Step

Design Epic-025.4 Career Intelligence Scenario Validation. Use synthetic HR,
technical, cross-domain career-transition, and insufficient-information
fixtures to evaluate the combined domain, stage, evidence, and explanation
behavior while preserving deterministic privacy and all public contracts.

## Notes

- Do not continue expanding the Application Layer until instructed.
- Keep `JobMatchResult` limited to `match_score`, `matched_skills`,
  `missing_skills`, `strengths`, `gaps`, and `recommendations` until a separate
  Agent Contract versioning Epic is approved.
- Keep domain classification, job family, confidence, and component scores
  internal to `skill/matching/` during the Pilot.
- Keep `RequirementAssessment` and `MatchExplanationResult` internal. Never
  retain raw resume or job-description text in explanation results.
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
