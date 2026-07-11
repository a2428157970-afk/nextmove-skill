# Provider Integration Standard

## Purpose

This standard governs future real AI Provider integrations. It does not add an
SDK, load credentials, or make a network request by itself.

## Provider Adapter Responsibilities

Provider Adapters own Provider API calls, SDK encapsulation, request/response
conversion, and Provider-specific error mapping. They must not contain career
logic, resume analysis logic, or Prompt business logic.

## Adapter Contract

```text
AIProvider
    ^
Provider Adapter
    ^
OpenAI | Claude | Local Model
```

Every adapter implements `generate(prompt: str, context: dict) -> str`, extends
`BaseProviderAdapter`, receives credential-free `AIProviderSettings`, and is
externally created and registered. `EnhancementService` is the AI-layer
consumer of generated content.

## Runtime Operations Policy

`ProviderRuntimePolicy` is a pure, credential-free data object owned by the AI
runtime boundary:

```python
ProviderRuntimePolicy(
    enabled=True,
    timeout=None,
    max_retries=0,
    fallback_enabled=True,
)
```

It does not initialize providers, call a network, or manage credentials. The
MVP defaults to one generation attempt. `max_retries` defines additional
attempts only; it has no backoff or rate-limit behavior. The policy timeout is
operational metadata for an external transport or adapter boundary and does not
create an HTTP client in the Skill.

`AIRequestContext(provider_name, model_name, capability, request_id)` is
optional transient metadata for correlation and future provider selection. It
must never contain an API key, complete prompt, resume content, or other user
private data. `EnhancementService` accepts it without storing it.

## Application Runtime Integration

`ApplicationRuntimeAdapter`, located under `skill/ai/application/adapters/`,
connects application-owned settings, a credential provider, a preconfigured
provider factory, an opaque transport, and feature policy to the stable
`AIRuntime`.

```text
Application infrastructure
        |
        v
ApplicationRuntimeAdapter
        |
        v
AIRuntime -> ProviderFactory -> Provider Adapter -> AIProvider
```

`AIRuntime` does not receive transport and its constructor remains unchanged.
The transport stays at the application boundary; an application may use it
when constructing its provider factory. No FastAPI route, environment reader,
secret adapter, or concrete HTTP client is included.

`AIFeaturePolicy` defaults AI and enhancement availability to enabled. If
either flag is false, the application adapter returns the existing structured
unavailable service before credentials, providers, or transport are accessed.

`AIExecutionMetadata` is a separate observation record containing only request
ID, provider name, model name, latency, and status. It does not alter
`AIEnhancementResult`.

## Health Check and Fallback

`AIProvider.health_check()` defaults to `True`, preserving every existing
provider implementation. A provider may override it. Before generation,
`EnhancementService` checks that its runtime policy is enabled and the
provider is healthy. A false result or health-check exception returns the
existing structured unavailable result without a generation request.

There is no implicit provider switch, model downgrade, or fallback chain. A
disabled, unavailable, unhealthy, timed-out, or response-failing provider
returns `AIEnhancementResult(success=False, ...)`; the deterministic Skill
Core result remains valid and independent.

## First Provider: OpenAI-Compatible Transport Adapter

`OpenAICompatibleProvider`, located at `skill/ai/providers/openai/`, maps the
generic Provider contract to an OpenAI-compatible Chat Completions request. It
uses an externally injected `HTTPTransport`; it does not depend on an SDK or
implement an HTTP client.

The adapter sends the configured model and user messages, parses
`choices[0].message.content`, and maps transport timeouts, transport failures,
and unusable response payloads to existing Provider error contracts. Default
tests use Mock transport only and never make live API calls.

## Standard-library Application Transport

`UrllibHTTPTransport`, under `skill/ai/application/transports/`, implements the
existing `HTTPTransport` protocol in the Application Layer. It uses only Python
`urllib`, posts JSON with application-supplied headers and timeout, and returns
decoded JSON objects.

Socket and URL timeouts map to `ProviderTimeoutError`, HTTP and connection
failures map to `ProviderUnavailableError`, and invalid or non-object JSON maps
to `ProviderResponseError`. The transport never reads environment variables,
persists credentials, or logs authorization headers, request bodies, or
response bodies. Applications own and may reuse the same transport instance.

## Safe Observability and Operational Limits

`AIExecutionObserver` creates `AIExecutionMetadata` from request identity,
start/end times, and the structured result only. Latency is recorded in
seconds. Prompt text, context, resumes, job descriptions, credentials, headers,
and raw request/response content are not accepted or retained.

`AIApplicationLimits` defaults to 12,000 prompt characters, 100 top-level
context items, and live requests disabled. `ApplicationEnhancementService`
validates these limits before provider generation and returns structured
failure without truncating or modifying input.

Feature rollback remains stronger than request limits: disabling AI or
enhancement returns an unavailable service before credential lookup, provider
creation, or transport use. Skill Core remains independent.

## Credential Ownership Policy

Credentials belong to the Application or Runtime Layer.

```text
User or Application
        |
        v
CredentialProvider
        |
        v
Provider Adapter
        |
        v
AI Provider
```

The Skill does not store secrets, load environment variables, manage token
lifecycle, log credentials, or expose them in results. For the
OpenAI-compatible adapter, an application passes the credential at construction
and the adapter uses it only to form the external transport authorization
header.

## SDK Isolation Strategy

Provider SDK imports may only exist inside a dedicated adapter package such as
`skill/ai/providers/openai/`. The following must never import a Provider SDK:

```text
skill/resume/
skill/analysis/
skill/improvement/
skill/matching/
skill/career/
skill/agent/
```

SDK clients cannot cross the adapter boundary; upper layers use only the AI
contracts and structured results.

## Error Mapping Strategy

| Provider failure | Provider contract | AI layer result |
| --- | --- | --- |
| Request timeout | `ProviderTimeoutError` | `AI provider timeout` |
| Service, transport, authentication, or rate-limit failure | `ProviderUnavailableError` | `AI provider unavailable` |
| Invalid or unusable response | `ProviderResponseError` | `AI provider response error` |

```text
SDK exception -> Provider error contract -> AI layer result -> AIEnhancementResult
```

Raw exception details, payloads, response bodies, and credentials must not
appear in `AIEnhancementResult`.

## Testing Strategy

### Contract Tests

Verify each adapter satisfies `AIProvider` and the `generate()` return type.

### Adapter Unit Tests

Use transport doubles to test request mapping, response parsing, and every
error conversion without credentials or network access.

### Integration Tests

Run against a Provider only after explicit approval and separate them from the
default Skill suite.

### Live Tests

Live tests live under `tests/live/` and are skipped by default. Run the normal
suite without real AI traffic:

```bash
python -m unittest discover -s tests
```

Only `RUN_LIVE_AI_TEST=true` enables that test boundary. The OpenAI-compatible
transport validator additionally requires an external
`NEXTMOVE_LIVE_TRANSPORT_FACTORY` import path; absent configuration skips
safely. Live credentials and transport remain externally managed, must not be
committed, and must not be printed by tests. This repository contains no live
endpoint or credential and does not invoke a live provider by default.

## Approval Checklist for the First Provider

- Provider SDK concerns stay in the Provider Adapter Layer; concrete transport
  implementation and lifecycle stay in the Application Layer.
- Credentials remain external and are not logged.
- Provider failures map to the documented contracts.
- Unit tests require no network access.
- Integration and live tests are opt-in.
- Removing the adapter leaves Core, Agent Runtime, and other adapters working.
