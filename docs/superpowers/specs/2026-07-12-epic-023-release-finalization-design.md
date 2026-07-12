# Epic-023 v0.8.0 Release Finalization Design

## Goal

Convert NextMove Skill v0.8.0 from Release Candidate to Developer Preview Ready without adding capabilities or changing core behavior.

## Scope

Epic-023 is limited to release hygiene, documentation alignment, manifest clarification, compatibility records, and release validation.

The Epic must not modify the Skill Core architecture, AI Provider layer, Application Layer, backend, frontend, `NextMoveSkill` API, Agent Tool schemas, or the `career_analysis` input contract. It must not introduce dependencies, network requirements, or a new CLI option.

## Repository and documentation hygiene

- Add the two existing Epic-020 plan documents that are currently untracked so the project history is complete.
- Add the Epic-023 design and implementation-plan records.
- Update `README.md`, `CHANGELOG.md`, `PROJECT.md`, and `NEXT_TASK.md` for Developer Preview readiness.
- Make `README.md` the primary user entry point by removing duplicated AI-quality content, correcting mojibake characters, and clarifying installation, invocation, offline behavior, and release status.

## Contract alignment

Keep the existing `skill.json` field:

```json
"entrypoint": "skill.__main__:main"
```

Add explicit fields while preserving compatibility:

```json
"skill_entrypoint": "NextMoveSkill.run",
"cli_entrypoint": "skill.__main__:main"
```

Documentation must consistently state:

- CLI: `job_description` is optional and omitted input is normalized to an empty string.
- Python and Agent calls: `job_description` remains required for `match_job` and `career_analysis`.

No runtime API or schema behavior changes are permitted.

## Agent compatibility record

Create `docs/agent-compatibility.md` with an evidence-based matrix:

| Agent | Discovery | Invocation | Status |
|---|---|---|---|
| ChatGPT Agent | Contract validation | Not externally tested | Pending |
| Claude | Contract validation | Not externally tested | Pending |
| Cursor | Contract validation | Not externally tested | Pending |
| Codex | Repository validation | Tested | Available |

The document must distinguish repository contract validation from external ecosystem invocation. It must not claim external tests that were not performed.

## CLI UX decision

Evaluate `--job-description-file` and record it as a post-v0.8.0 candidate. Do not implement it in Epic-023. This avoids adding parameter precedence, file-reading errors, encoding behavior, and regression surface during release finalization.

## Validation

Run and record:

```text
pip install -e .
nextmove --help
python examples/skill_demo.py
python -m unittest discover -s tests -v
python -m compileall skill tests examples
git diff --check
```

Also confirm:

- no real secrets or credentials are tracked;
- default Skill, CLI, demo, and unit-test flows require no network;
- `skill/` does not import `application/`;
- project runtime dependencies remain empty;
- all local commits ahead of `origin/main` belong to the v0.8.0 development and release history.

If the machine's default Python cannot provide pip, validation may use the bundled Python runtime, but the environment limitation and exact successful command must be reported truthfully.

## Release and commit policy

Create one implementation commit with message:

```text
release: finalize NextMove Skill v0.8.0 readiness
```

Do not create a tag, push commits, or create a GitHub Release. The final handoff must include the commit hash and a final pre-tag checklist for human approval.

## Acceptance criteria

- Release-facing documentation consistently describes v0.8.0 Developer Preview readiness.
- README duplication and visible mojibake are removed.
- `skill.json` exposes compatible legacy, Skill, and CLI entrypoint fields.
- the compatibility matrix contains only verified claims.
- the `--job-description-file` decision is documented but not implemented.
- all required validation commands pass in the documented validation environment.
- the worktree contains no unexplained release files after the implementation commit.
- no product capability, core behavior, provider, application, backend, or frontend code changes are included.
