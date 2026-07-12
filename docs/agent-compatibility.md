# Agent Compatibility

This document records evidence for NextMove Skill v0.8.0 Agent compatibility.
Repository contract validation confirms that an Agent can discover the manifest,
schemas, instructions, and invocation boundary. It does not prove successful
invocation inside an external Agent product.

| Agent | Discovery | Invocation | Status |
|---|---|---|---|
| ChatGPT Agent | Contract validation | Not externally tested | Pending |
| Claude | Contract validation | Not externally tested | Pending |
| Cursor | Contract validation | Not externally tested | Pending |
| Codex | Repository validation | Tested | Available |

## Evidence

Repository validation covers:

- `SKILL.md` discovery instructions;
- `skill.json` name, version, capabilities, entrypoints, input schema, and output schema;
- `NextMoveSkill.run` Python and Agent invocation;
- the built-in Agent Tool Registry and `AgentRuntime`;
- JSON-serializable success and failure responses;
- installed CLI and offline demo acceptance tests.

Codex performed the repository-level review and invoked the local package,
CLI, demo, and test suite. ChatGPT Agent, Claude, and Cursor have not been
invoked against a published v0.8.0 package, so their external status remains
pending.

## Entrypoints and inputs

- Agent and Python consumers use `NextMoveSkill.run`.
- CLI consumers use `skill.__main__:main`, `python -m skill`, or `nextmove`.
- The legacy manifest `entrypoint` remains the CLI entrypoint.
- `job_description` is required for Agent/Python `match_job` and
  `career_analysis` calls.
- `--job-description` is optional for CLI calls and becomes an empty string
  when omitted.

## Post-release interoperability check

For each pending Agent, validate discovery, one successful `career_analysis`
call, one missing-input failure, and preservation of the no-fabrication rule.
Record the product version, adapter or import method, observed response shape,
and any instruction ambiguity without retaining resume content.

## Deferred CLI UX candidate

`--job-description-file` was evaluated for v0.8.0 and deliberately deferred.
It could improve long job-description input, but implementation first needs a
clear rule for precedence against `--job-description`, UTF-8 decoding errors,
missing or empty files, and structured CLI failure output. Adding those
behaviors during final release preparation would expand regression risk.
Re-evaluate the option from real CLI feedback after v0.8.0.
