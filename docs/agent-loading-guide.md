# NextMove Agent Loading Guide

NextMove has two intentionally different distribution modes. Never infer real
runtime availability from an uploaded `SKILL.md`, `skill.json`, or prompt.

## Distribution modes

| Mode | Contains Python runtime | Valid final marker | Meaning |
|---|---:|---|---|
| Runtime Skill Package | Yes | `NEXTMOVE_READY` | The package was validated, `NextMoveSkill` was imported, an offline `career_analysis` smoke test ran, its `SkillResponse` serialized, and network calls remained zero. |
| Prompt-only Pilot Kit | No | `NEXTMOVE_PROMPT_ONLY` | Prompts, examples, and report-format guidance are available, but no local NextMove runtime executed. |

Finding metadata is not readiness. If the runtime preflight fails, the host must
report the failure and must not simulate a NextMove result.

## Compatibility vocabulary

- **Contract supported:** the product documents a compatible file or Skill
  mechanism. This does not prove NextMove execution.
- **Repository tested:** the exact package passes NextMove's deterministic build,
  manifest, import, smoke, serialization, privacy, and clean-room tests.
- **External runtime verified:** the exact released archive passed in a named
  external product/version with dated evidence.
- **Pending:** required evidence has not been recorded.

## Current evidence status

| Host | Mode | Contract | Repository | External runtime |
|---|---|---|---|---|
| ChatGPT | Prompt-only file reference | Contract supported | Repository tested | Pending |
| Claude Code | Complete Runtime Package with local Python | Contract supported | Repository tested | Pending |
| Cursor | Complete Runtime Package with local Python | Contract supported | Repository tested | Pending |
| Codex | Complete Runtime Package with local Python | Contract supported | Repository tested | Pending |

No row above claims an externally verified product integration.

## ChatGPT

Treat ordinary file upload, Project files, or GPT knowledge as Prompt-only.
Uploading the Pilot Kit gives ChatGPT reference material; it does not execute
the local Python Skill. The conversation and every preview must remain labelled
`NEXTMOVE_PROMPT_ONLY`.

Do not claim that `NextMoveSkill.run()` executed unless a separately configured
code-execution integration has loaded the complete Runtime Package and passed
the same offline preflight. That integration is not supplied or externally
verified by this Epic.

## Claude Code

Load or copy the complete Runtime Package using the Skill/file mechanism
documented for the installed Claude Code version. The host must have Python
3.11+ and local filesystem/code-execution permission. From the package, run:

```text
python scripts/check_skill_package.py --package .
```

Only the final `NEXTMOVE_READY` marker proves this package executed. Merely
discovering the folder or invoking a slash command is insufficient.

## Cursor

Load the complete Runtime Package, not only `SKILL.md`. The Cursor environment
must allow Python 3.11+ local execution and access to package files. Run the
same package preflight and require `NEXTMOVE_READY` before claiming runtime use.
Editor discovery or an imported Agent Skill without the Python implementation
remains contract-level evidence only.

## Codex

Place the complete Runtime Package in a workspace accessible to Codex and use a
local environment with Python 3.11+. Run the package preflight before analysis.
Codex repository validation for this Epic is recorded, but external-runtime
status remains Pending until a versioned product-loading record is reviewed.

## Failure and privacy behavior

- A failed runtime preflight returns a nonzero status and a content-free
  structured error. It never prints the ready marker.
- A Prompt-only preflight prints only its Prompt-only marker and never executes
  the Skill.
- Use fictional samples first. Do not submit resumes, job descriptions,
  identity, contact details, employer/client confidential information,
  credentials, or private Agent transcripts in compatibility reports.
