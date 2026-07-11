# Epic-011 Application Provider Runtime Integration Design

## Goal

Add an application integration boundary around the existing AI runtime without
adding AI capabilities, changing Skill Core, or coupling `AIRuntime` to HTTP,
credentials, environment variables, or a web framework.

## Architecture

`ApplicationRuntimeAdapter` is a concrete dependency-assembly object under
`skill.ai.application.adapters`. It receives `AIProviderSettings`, a
`CredentialProvider`, a preconfigured `ProviderFactory`, an opaque transport,
and `AIFeaturePolicy`. `build_runtime()` creates the existing `AIRuntime`
without changing its constructor. `build_enhancement_service()` checks feature
flags before building or invoking the runtime.

The transport remains an application-owned injected object. It is retained at
the application boundary so an externally configured factory can share the
same infrastructure dependency, but it is not passed into `AIRuntime`,
`AIProvider`, or the provider base contract.

## Feature Policy

`AIFeaturePolicy(enabled=True, enhancement_enabled=True)` is a pure data
object. If either flag is false, `build_enhancement_service()` returns an empty
`EnhancementService`. This produces the existing structured unavailable result
and avoids credential lookup, provider creation, and transport use.

## Execution Metadata

`AIExecutionMetadata(request_id, provider_name, model_name, latency, status)`
is a frozen, slotted observation record. It does not contain a prompt, resume
text, user data, credentials, or raw provider responses. This Epic does not
attach it to or modify `AIEnhancementResult`.

## Credential Boundary

Credentials remain application-owned. Secret storage, environment reading,
key rotation, and token lifecycle are outside the Skill. The adapter accepts
only the existing `CredentialProvider` contract and never reads a credential
itself; `AIRuntime` performs lookup only when an enabled enhancement service is
built.

## Compatibility and Scope

`skill/ai/runtime.py` and `from skill.ai.runtime import AIRuntime` remain
unchanged. No files under `skill/resume`, `skill/analysis`,
`skill/improvement`, `skill/matching`, `skill/career`, or `skill/agent` are
modified. No SDK, MCP, RAG, vector database, embedding, FastAPI integration, or
secret adapter is added.

## Testing

Unit tests verify dependency assembly, credential injection through the
existing runtime, both feature flags, structured disabled behavior, transport
identity, and metadata fields. The full unittest and compileall commands remain
the acceptance gates.
