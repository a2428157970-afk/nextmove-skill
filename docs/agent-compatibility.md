# Agent Compatibility

This document records evidence for NextMove Skill v0.8.0 distribution modes.
See the detailed [Agent Loading Guide](agent-loading-guide.md).

| Agent | Supported distribution boundary | Contract | Repository | External runtime |
|---|---|---|---|---|
| ChatGPT | Prompt-only file reference; ordinary uploads do not execute local Python | Contract supported | Repository tested | Pending |
| Claude Code | Complete Runtime Package plus Python 3.11+ and preflight | Contract supported | Repository tested | Pending |
| Cursor | Complete Runtime Package plus Python 3.11+ and preflight | Contract supported | Repository tested | Pending |
| Codex desktop 26.707.8168.0 | Complete Runtime Package plus Python 3.11+ and preflight | Contract supported | Repository tested | External runtime verified (2026-07-13) |

`Repository tested` means deterministic archive construction, manifest and
checksum validation, clean-room import, actual offline `career_analysis`, JSON
serialization, zero network calls, fictional Human Career Report generation,
privacy checks, and a negative readiness test passed. It is not an external
product certification.

Runtime readiness is valid only when the preflight's final line is
`NEXTMOVE_READY`. Prompt-only validation returns `NEXTMOVE_PROMPT_ONLY`. Merely
finding `SKILL.md`, reading `skill.json`, uploading files, or following prompts
does not prove execution.

Codex external verification used Python 3.13.14 and Runtime ZIP SHA-256
`2109917ef3591a054a239c68095c0e052c17ddc14b87a64aa2f1fe4e3cfbafb7`.
Codex extracted the ZIP to a new temporary directory, ran the package preflight
before import, received `NEXTMOVE_READY` with zero network calls, confirmed the
imported `skill` path was inside the extraction directory rather than the source
repository, and generated the fictional Sales-to-Product-Manager Human Career
Report. The first diagnostic attempt imported before directory preflight and
therefore created `__pycache__`; strict manifest validation correctly rejected
that modified directory. A fresh extraction then passed in documented order.

External verification remains Pending for ChatGPT, Claude Code, and Cursor
until a dated record names the product version, exact package checksum/build
ID, loading method, successful and failed preflight behavior, and sanitized
output evidence. Do not retain
resume, job-description, identity, contact, employer, credential, or private
conversation content in that record.
