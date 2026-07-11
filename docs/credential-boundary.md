# Credential Source Boundary

## Ownership

AI credentials belong to the Application Layer. NextMove Skill accepts the
existing `CredentialProvider` contract but does not decide where credentials
come from or how they are stored.

```text
Application Secret Infrastructure
              |
              v
      CredentialProvider
              |
              v
ApplicationRuntimeAdapter
              |
              v
          AIRuntime
              |
              v
       ProviderFactory
```

## Application Responsibilities

An application may obtain an API key, token, or cloud credential from its own
approved secret infrastructure. It owns secret storage, access policy,
rotation, revocation, refresh, auditing, and transport configuration.

The application supplies a `CredentialProvider` and a preconfigured
`ProviderFactory` to `ApplicationRuntimeAdapter`. The adapter does not read a
credential. When AI enhancement is enabled, the existing `AIRuntime` requests
an opaque credential and passes it to the factory.

## Skill Prohibitions

The Skill must not:

- read credentials from environment variables or files;
- store or cache secrets;
- implement a secret manager;
- rotate, refresh, log, or serialize credentials;
- expose credentials through results, metadata, or exceptions.

`AIExecutionMetadata` is limited to request ID, provider name, model name,
latency, and status. It cannot contain a credential, prompt, resume text, or
user data.

## Feature-Disabled Behavior

When `AIFeaturePolicy.enabled` or `enhancement_enabled` is false,
`ApplicationRuntimeAdapter` returns an unavailable `EnhancementService`
without credential lookup, provider creation, or transport use. Skill Core
continues to operate independently.

## Transport and Live Validation

The Application Layer owns `UrllibHTTPTransport`, its base URL, reuse, and
live-request decision. The transport accepts authorization headers for one
call but never stores them as credential state or emits request/response
content.

Live validation is disabled unless `RUN_LIVE_AI_TEST=true`. Tests receive a
validator from an external assembly hook and do not read a credential directly.
Missing external configuration produces a safe skip.

Operational rollback is explicit:

```text
AIFeaturePolicy disabled
        -> no credential lookup
        -> no provider creation
        -> no transport call
        -> AI provider unavailable
        -> Skill Core result remains valid
```
