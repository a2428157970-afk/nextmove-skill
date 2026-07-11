# Next Task

## Status

The released v0.7.0 baseline now includes completed Epic-020.1 and Epic-020.2.
The Application Layer validates `CareerAnalysisRequest` before delegation,
normalizes an omitted job description to an empty string, and preserves the
fixed four-step Skill workflow and one-way dependency boundary.

## Recommended Next Step

Epic-020.3: define the next Application Layer contract concern only after
scope approval. Keep it transport-neutral; do not add an HTTP endpoint,
frontend integration, authentication, persistence, provider behavior, or new
dependencies.

## Notes

- Do not execute the next Epic until instructed.
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
