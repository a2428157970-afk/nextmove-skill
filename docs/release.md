# Release Checklist

Use this checklist before creating a NextMove Skill release.

## 1. Install

Install the package from the repository root in a clean Python 3.11 or later
environment with pip and setuptools 61 or later:

```bash
python -m pip install -e .
```

For offline installation, ensure the build backend is already installed. Build
isolation may otherwise try to resolve setuptools from a package index even
though NextMove has no runtime package dependencies.

## 2. Import Check

Confirm that the public API and release version can be imported:

```bash
python -c "from skill import NextMoveSkill, __version__; print(__version__)"
```

The printed version must match `skill/__version__.py` and
`skill.metadata.SKILL_METADATA["version"]`.

## 3. Demo Check

Run the installable Skill product workflow:

```bash
python examples/skill_demo.py
```

Confirm that the JSON report includes successful results for `analysis`,
`improvement`, `job_match`, and `career_advice`.

## 4. Test Suite

Run every Skill test:

```bash
python -m unittest discover -s tests -v
```

## 5. Version Check

Confirm that there is one version source:

- `skill/__version__.py` contains the release version.
- `skill/metadata.py` imports that version rather than duplicating it.
- `pyproject.toml` reads the version dynamically from `skill.__version__`.
- `skill.json` mirrors the release version and is validated against the Python
  source of truth by the test suite.

For the Skill Developer Preview, the expected public version is `0.8.0`.

## 6. Optional AI Validation

Run the deterministic offline demonstration:

```bash
python examples/ai_enhancement_demo.py
```

Confirm that it emits JSON containing a successful mock enhancement, a
successful application-runtime result, and a structured unavailable result for
the disabled feature. It must not read environment variables, use an API key,
or access the network.

Live tests remain opt-in and skip safely unless explicitly enabled:

```bash
python -m unittest discover -s tests/live -v
```

## 7. Agent Compatibility

Review [agent-compatibility.md](agent-compatibility.md). Repository contract
validation and external product invocation must be reported separately. Do not
mark a pending Agent available without a recorded external invocation.

## 8. Final Git Check

Before creating the tag, confirm the release commit is present remotely, the
worktree is clean, all intended plan documents are tracked, and the tag target
is the approved v0.8.0 release commit. Tagging, pushing, and creating a GitHub
Release are manual approval gates.
