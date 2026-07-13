# Agent Compatibility

This document records evidence for NextMove Skill v0.8.0 distribution modes.
See the detailed [Agent Loading Guide](agent-loading-guide.md).

| Agent | Supported distribution boundary | Contract | Repository | External runtime |
|---|---|---|---|---|
| ChatGPT | Prompt-only file reference; ordinary uploads do not execute local Python | Contract supported | Repository tested | Pending |
| Claude Code | Complete Runtime Package plus Python 3.11+ and preflight | Contract supported | Repository tested | Pending |
| Cursor | Complete Runtime Package plus Python 3.11+ and preflight | Contract supported | Repository tested | Pending |
| Codex | Complete Runtime Package plus Python 3.11+ and preflight | Contract supported | Repository tested | Pending |

`Repository tested` means deterministic archive construction, manifest and
checksum validation, clean-room import, actual offline `career_analysis`, JSON
serialization, zero network calls, fictional Human Career Report generation,
privacy checks, and a negative readiness test passed. It is not an external
product certification.

Runtime readiness is valid only when the preflight's final line is
`NEXTMOVE_READY`. Prompt-only validation returns `NEXTMOVE_PROMPT_ONLY`. Merely
finding `SKILL.md`, reading `skill.json`, uploading files, or following prompts
does not prove execution.

External verification remains Pending for every host until a dated record names
the product version, exact package checksum/build ID, loading method, successful
and failed preflight behavior, and sanitized output evidence. Do not retain
resume, job-description, identity, contact, employer, credential, or private
conversation content in that record.
