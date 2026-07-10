# Release Checklist

Use this checklist before creating a NextMove Skill release.

## 1. Install

Install the package from the repository root in a clean Python 3.11 or later
environment:

```bash
python -m pip install -e .
```

## 2. Import Check

Confirm that the public API and release version can be imported:

```bash
python -c "from skill import NextMoveSkill, __version__; print(__version__)"
```

The printed version must match `skill/__version__.py` and
`skill.metadata.SKILL_METADATA["version"]`.

## 3. Demo Check

Run the full Career Intelligence workflow:

```bash
python examples/full_career_analysis.py
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

For v0.5.0, the expected public version is `0.5.0`.
