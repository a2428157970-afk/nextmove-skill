# Next Task

## Status

Epic-026.3 has produced a v0.8.0 Release Candidate from the complete Epic-025.3
through Epic-026.2 chain. Separate Runtime and Prompt-only artifacts build
deterministically, their mode-specific preflights pass, and Codex external
Runtime verification succeeded from a fresh ZIP extraction outside the source
repository. Skill Core, public contracts, Application Layer, CLI behavior,
providers, and dependencies remain unchanged. The full suite passes 330 tests
with 3 opt-in live tests skipped.

## Recommended Next Step

Complete `docs/release-checklist-v0.8.0.md` against the actual uploaded and
downloaded assets. Recalculate published checksums, review the Codex evidence,
and confirm ordinary ChatGPT uploads remain Prompt-only. Keep ChatGPT, Claude
Code, and Cursor Pending until separately executed and reviewed. Publishing
ZIPs, merging to `main`, creating a tag, pushing, and creating a GitHub Release
require explicit human approval.

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
- Keep `CareerTransitionAssessment` internal. Preserve unknown gaps, bounded
  evidence-risk language, and the requirement that every action references a
  structured gap and expected direct evidence.
- Keep `HumanCareerReport`, `HumanCareerReportBuilder`, language safety, and
  formatters internal to `skill/reporting/`. Do not add them to existing Agent,
  Application, CLI, or Skill response schemas without a separately approved
  versioned integration Epic.
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
