# NextMove Architecture

NextMove is organized as a provider-neutral Career Intelligence Skill. Its
design keeps reusable domain behavior independent from Agent providers and Web
delivery mechanisms.

## Layer Overview

```text
Layer 1: Skill Core
  Parser / Analyzer / Improver / Matcher / Advisor
                    ↓
Layer 2: Skill Interface
  NextMoveSkill direct methods and run(capability, payload)
                    ↓
Layer 3: Agent Layer
  AgentTool schema / Tool Registry / AgentRuntime
                    ↓
Layer 4: Future Adapter Layer
  Provider-specific integrations, when needed
```

## Layer 1: Skill Core

The Skill Core contains the reusable career intelligence logic:

- resume parsing and the `ResumeProfile` data model;
- resume analysis and improvement;
- job matching; and
- career advice.

It returns typed, structured result dataclasses. The Core does not know about
HTTP, frontend state, Agent provider SDKs, MCP, or provider request formats.

## Layer 2: Skill Interface

`NextMoveSkill` is the stable Python entry point. It exposes direct methods for
each domain capability and the unified `run(capability, payload)` method for
generic callers. `run()` returns a `SkillResponse` that consistently expresses
success, capability, result, and structured error information.

This layer converts caller input into the appropriate Core calls without
requiring callers to know the internal module layout.

## Layer 3: Agent Layer

The Agent Layer makes capabilities discoverable and callable by Agent hosts
without changing their implementation:

- `AgentTool` describes provider-neutral tool metadata and input/output schema.
- `SkillToolRegistry` maps each tool name directly to its Skill capability.
- `AgentRuntime` resolves a requested tool and delegates to
  `NextMoveSkill.run()`.

The Agent Layer is optional. Direct Python callers can use `NextMoveSkill`
without it.

## Layer 4: Future Adapter Layer

Future adapters may translate `AgentTool` metadata and `SkillResponse` values
for OpenAI, Claude, MCP, or other hosts. Those integrations are not part of the
current package and must remain outside the Skill Core.

An adapter should translate at the boundary only: it can export tool schemas,
receive provider-specific calls, pass a tool name and payload to
`AgentRuntime`, and translate the structured response back. It must not embed
provider SDK requirements into the Core.

## Dependency Direction

Dependencies move one way: callers and adapters depend on the Skill Interface,
which depends on the Skill Core. The Core never depends on Agent, provider, or
Web layers. This direction preserves portability, testability, and provider
neutrality.
