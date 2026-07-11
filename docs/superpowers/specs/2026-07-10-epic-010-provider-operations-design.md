# Epic-010 Production Provider Operations MVP Design

## Scope

Epic-010 adds provider-runtime operational boundaries to `skill.ai` without
changing Skill Core or adding an AI capability, provider, SDK, transport, or
credential source.

## Components

- `ProviderRuntimePolicy` is a credential-free data object with `enabled`,
  `timeout`, `max_retries`, and `fallback_enabled`. It performs no provider
  initialization or network work.
- `AIRequestContext` is a transient, metadata-only data object for a provider
  name, model name, capability, and request identifier. It excludes prompts,
  credentials, resume contents, and other user-private data.
- `AIProvider.health_check()` has a concrete default of `True`, so existing
  provider subclasses continue to work unchanged. Adapters may override it.
- `EnhancementService` owns policy application. A disabled or unhealthy
  provider produces the existing structured unavailable result. It retries
  provider generation at most `max_retries` additional times. The default is
  one request with no retry.

## Failure Semantics

No automatic provider or model routing is introduced. Provider absence,
disabled policy, unsuccessful health check, or provider failure returns an
`AIEnhancementResult` failure. The deterministic Skill Core result remains
independent and valid.

`fallback_enabled` records the runtime fallback policy. This MVP always keeps
provider failures structured, does not expose provider exceptions or sensitive
data, and introduces no provider-routing fallback chain.

## Live-Test Boundary

`tests/live/` is intentionally separate from normal unit tests. Its test
module is skipped unless `RUN_LIVE_AI_TEST=true`. The repository stores no
credential, emits no credential, and uses no live network path by default.

## Compatibility

The existing two-argument `EnhancementService.enhance(prompt, context)` and
all existing `AIProvider.generate(prompt, context)` implementations remain
valid. Request context is an optional third service argument and is not
persisted by the service.
