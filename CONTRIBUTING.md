# Contributing to NextMove

NextMove is a Skill-first AI Career Intelligence framework. Contributions
should strengthen reusable career intelligence while preserving a clean
boundary between the Skill Core and delivery layers.

## Development setup

NextMove requires Python 3.11 or later. Install the Skill package locally:

```bash
pip install -e .
```

Run the Skill test suite before submitting changes:

```bash
python -m unittest discover -s tests -v
```

## Adding a Capability

Every capability must be independently useful through `NextMoveSkill` and
return a structured result.

1. Define the input or output dataclasses under `skill/schemas/` or the
   capability's own schema module.
2. Implement the focused domain behavior in a dedicated module under `skill/`.
3. Add a direct method to `NextMoveSkill` and route the capability through
   `NextMoveSkill.run()`.
4. Add an `AgentTool` definition only when the capability should be discoverable
   by Agents; the tool name should match the capability name.
5. Add unit tests for the new behavior and API-level tests for its structured
   `SkillResponse`.
6. Add or update a runnable example and public documentation when the
   capability is ready for users.

## Skill Core Design Principles

- **Structured outputs first.** Public capabilities return typed dataclasses
  and `run()` returns a `SkillResponse` envelope.
- **Small, focused modules.** Keep parsing, analysis, matching, improvement,
  and career advice independently understandable and testable.
- **Skill Core before Web.** Do not make core behavior depend on HTTP, file
  uploads, frontend state, or backend application code.
- **Preserve compatibility.** Keep existing direct methods working while
  extending the unified `run()` interface.
- **Test real behavior.** Prefer tests that exercise actual Skill components;
  use mocks only when an external boundary makes them necessary.

## Provider-Neutral Principle

The core package must not import or require OpenAI, Claude, Gemini, MCP, or a
specific Agent framework. Future providers belong behind adapter boundaries and
must consume the provider-neutral `AgentTool` schema and structured Skill
responses.

Do not introduce provider SDKs, provider-specific request formats, web
framework dependencies, or transport logic into `skill/`.

## Pull Requests

- Keep each pull request focused on one capability or documentation concern.
- Include tests for behavior changes and run the complete Skill test suite.
- Do not commit secrets, local environments, build output, or uploaded resumes.
- Explain the user-facing behavior, architecture impact, and verification
  results in the pull request description.
