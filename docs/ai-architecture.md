# AI Enhancement Layer Architecture

## Purpose

The optional AI Enhancement Layer extends NextMove without changing the
deterministic Skill Core. Provider-neutral layers contain no provider SDK,
credential storage, environment access, or production Prompt content. An
opt-in standard-library transport exists only in the Application Layer.

## Dependency Direction

```text
Skill Core structured result
        |
        v
EnhancementService
        |
        v
AIProvider / BaseProviderAdapter
        |
        v
Future external provider adapter
```

Core modules never import `skill.ai`, provider SDKs, templates, settings, or
credentials.

## Provider and Adapter Contracts

- `AIProvider` declares `generate(prompt: str, context: dict) -> str`.
- `BaseProviderAdapter` inherits `AIProvider` and receives
  `AIProviderSettings` from the application.
- `MockProviderAdapter` is a deterministic test implementation.
- `ProviderRegistry` stores externally created instances and never manages
  their lifecycle.
- `EnhancementService` resolves a registered provider at construction, while
  keeping direct `provider=` injection compatible.

## Configuration and Prompt Boundaries

`AIProviderConfig` and `AIProviderSettings` hold provider name, model name,
metadata, and an optional timeout in seconds. `None` leaves timeout policy to
the external application. Neither type stores API keys, secrets, SDK clients,
or transport configuration.

`PromptTemplate` is a named abstract contract with
`render(context: dict) -> str`. No production Prompt text is stored here, and
templates must not contain credential, transport, or Career Core logic.

## Error Contract

`ProviderUnavailableError`, `ProviderTimeoutError`, and
`ProviderResponseError` are mapped by `EnhancementService` to structured
`AIEnhancementResult` failures. Unexpected provider exceptions use the same
unavailable-provider fallback, so implementation details remain private.

## Credential and Runtime Boundary

`CredentialProvider` is an abstract application-facing interface with
`get_credentials(provider_name) -> object | None`. Its values are opaque to the
Skill: it does not load environment variables, store credentials, or manage
their lifecycle.

`ProviderFactory` accepts `AIProviderSettings` and an opaque credential value,
then returns a `BaseProviderAdapter`. It is a contract only: no factory in this
package builds a real SDK client or performs a network operation.

`AIRuntime` composes the application-owned collaborators:

```text
AIProviderSettings + CredentialProvider + ProviderFactory
                         |
                         v
                    AIRuntime
                         |
             credentials -> factory -> adapter
                         |
                         v
        ProviderRegistry -> EnhancementService
```

Missing credentials or factory failure produce an unbound
`EnhancementService`, which returns the existing structured unavailable-provider
result. Runtime assembly does not expose provider creation exceptions.

## Application Transport and Observation Boundary

```text
ApplicationRuntimeAdapter
        |
        +--> AIFeaturePolicy / AIApplicationLimits
        +--> CredentialProvider / ProviderFactory
        +--> reusable UrllibHTTPTransport
        |
        v
AIRuntime -> EnhancementService -> AIProvider
```

`AIRuntime` and `AIProvider` remain transport-implementation agnostic.
`UrllibHTTPTransport` implements the existing protocol with Python standard
library facilities and maps failures to stable Provider errors.

`ApplicationEnhancementService` validates prompt length, top-level context
item count, and explicit live-request permission before provider generation.
It never truncates input. `AIExecutionObserver` produces metadata containing
only request ID, provider, model, latency in seconds, and success/failure
status. It cannot collect prompt or user content.

Disabling the feature policy short-circuits before credential, factory, or
transport access. Default unit tests use injected transport doubles and perform
no network calls; live validation is opt-in and externally assembled.

## Extension Rules

Applications own provider configuration, credentials, and instance lifecycle.
Future adapters implement `AIProvider` through `BaseProviderAdapter`, are
created externally, and are registered with `ProviderRegistry`. AI output stays
optional and never replaces existing Core results or public Skill APIs.
