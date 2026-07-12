# Epic-023 v0.8.0 Release Finalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make NextMove Skill v0.8.0 Developer Preview Ready through release hygiene, documentation alignment, manifest clarification, and reproducible validation without changing product behavior.

**Architecture:** Preserve every runtime boundary and public API. Limit machine-readable changes to additive `skill.json` entrypoint metadata, protect them with release acceptance tests, and keep all other changes in release-facing documentation and project records.

**Tech Stack:** Python 3.11+, standard library, JSON, Markdown, setuptools, unittest, Git.

## Global Constraints

- Do not modify Skill Core architecture, AI Provider, Application Layer, backend, or frontend.
- Do not modify `NextMoveSkill`, Agent Tool schemas, or the `career_analysis` input contract.
- Do not add a dependency, network requirement, Skill capability, or CLI option.
- Keep CLI `job_description` optional and Python/Agent `job_description` required for `match_job` and `career_analysis`.
- Do not create a Git tag, push, or GitHub Release.
- Finish with one implementation commit named `release: finalize NextMove Skill v0.8.0 readiness`.

---

### Task 1: Protect additive entrypoint metadata with acceptance coverage

**Files:**
- Modify: `tests/test_skill_acceptance.py`
- Modify: `skill.json`

**Interfaces:**
- Consumes: existing `skill.json` legacy `entrypoint` and `NextMoveSkill.run(capability, payload)`.
- Produces: `skill_entrypoint = "NextMoveSkill.run"` and `cli_entrypoint = "skill.__main__:main"` without changing `entrypoint`.

- [ ] **Step 1: Add a failing manifest compatibility assertion**

Extend the existing manifest discovery test with exact assertions:

```python
self.assertEqual(manifest["entrypoint"], "skill.__main__:main")
self.assertEqual(manifest["skill_entrypoint"], "NextMoveSkill.run")
self.assertEqual(manifest["cli_entrypoint"], "skill.__main__:main")
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```text
python -m unittest tests.test_skill_acceptance.SkillOperationalAcceptanceTests.test_agent_discovers_entrypoint_and_career_analysis -v
```

Expected: failure because `skill_entrypoint` is absent.

- [ ] **Step 3: Add the two fields to `skill.json`**

Keep the existing field and place the additive fields beside it:

```json
"entrypoint": "skill.__main__:main",
"skill_entrypoint": "NextMoveSkill.run",
"cli_entrypoint": "skill.__main__:main",
```

- [ ] **Step 4: Run the focused test and verify GREEN**

Run the Step 2 command. Expected: one test passes.

### Task 2: Complete release documentation and repository records

**Files:**
- Create: `docs/agent-compatibility.md`
- Modify: `README.md`
- Modify: `SKILL.md`
- Modify: `docs/release/v0.8.0.md`
- Modify: `docs/release.md`
- Modify: `CHANGELOG.md`
- Modify: `PROJECT.md`
- Modify: `NEXT_TASK.md`
- Add existing: `docs/superpowers/plans/2026-07-11-epic-020.2-application-request-boundary-validation.md`
- Add existing: `docs/superpowers/plans/2026-07-11-epic-020.3-application-execution-metadata.md`

**Interfaces:**
- Consumes: the unchanged runtime contracts and the entrypoint metadata from Task 1.
- Produces: one primary README entry point, truthful ecosystem status, examples, CLI evaluation, and Developer Preview Ready project state.

- [ ] **Step 1: Rewrite release-facing README sections**

Remove the duplicated quality-evaluation block and replace visible mojibake with plain ASCII arrows or normal prose. Ensure README covers installation prerequisites, CLI/Python input differences, entrypoint differences, offline behavior, examples, compatibility-document link, and Developer Preview Ready status.

- [ ] **Step 2: Align `SKILL.md` examples and contract language**

Add compact examples for a structured `ResumeProfile` payload, the four `CareerAnalysisReport` sections, a successful `SkillResponse`, and a failed `SkillResponse`. Reiterate the non-fabrication rule and the CLI-versus-Agent `job_description` distinction.

- [ ] **Step 3: Create the compatibility matrix and CLI evaluation**

Create the approved four-row matrix. Explain that ChatGPT Agent, Claude, and Cursor have repository contract validation only and remain pending external invocation. Record Codex repository validation as tested and available. Document `--job-description-file` as deferred until after v0.8.0, including precedence, encoding, and error-contract questions that must be designed before implementation.

- [ ] **Step 4: Update release and maintenance records**

Add Epic-023 to CHANGELOG and set PROJECT/NEXT_TASK to the final-check state. Extend release documents with Python 3.11+, setuptools/pip prerequisites, exact entrypoint meanings, and the external compatibility limitation.

- [ ] **Step 5: Scan documentation consistency**

Run:

```text
rg -n "Release Candidate|optional job description|job_description|skill_entrypoint|cli_entrypoint|--job-description-file" README.md SKILL.md skill.json docs CHANGELOG.md PROJECT.md NEXT_TASK.md
```

Expected: no current-state claim leaves v0.8.0 as Release Candidate; optional input language is explicitly scoped to CLI; the deferred CLI option is never documented as available.

### Task 3: Validate installation, behavior, boundaries, and repository state

**Files:**
- Verify only; no product file changes.

**Interfaces:**
- Consumes: the complete Epic-023 worktree.
- Produces: fresh release evidence and a clean implementation commit.

- [ ] **Step 1: Confirm local commits belong to v0.8.0 history**

Run:

```text
git log --oneline origin/main..main
git diff --stat origin/main..main
```

Expected: commits cover the previously completed NextMove roadmap through v0.8.0 productization, operational readiness, and Epic-023; no unrelated product appears.

- [ ] **Step 2: Install the editable package**

Run `pip install -e .` with Python 3.11+ in the available validation environment. If isolated build dependency resolution is unavailable offline, use the environment's already installed setuptools with `--no-build-isolation` and record the distinction.

Expected: `nextmove-skill 0.8.0` installs successfully with no project runtime dependencies.

- [ ] **Step 3: Run required acceptance commands**

Run:

```text
nextmove --help
python examples/skill_demo.py
python -m unittest discover -s tests -v
python -m compileall skill tests examples
git diff --check
```

Expected: CLI exit 0; demo success response; all non-live tests pass and live tests skip by default; compilation exit 0; no whitespace errors.

- [ ] **Step 4: Reconfirm release boundaries**

Run tracked-file secret-pattern scans, inspect `pyproject.toml` dependencies, search `skill/` for `application` imports, and confirm default live tests remain opt-in.

Expected: no real credential; `dependencies = []`; no `skill` to `application` import; no default network call.

- [ ] **Step 5: Review the final diff and commit**

Confirm only approved paths changed, stage the two Epic-020 plans and all Epic-023 files, then commit:

```text
release: finalize NextMove Skill v0.8.0 readiness
```

Expected: commit succeeds; worktree is clean; no tag or push occurs.
