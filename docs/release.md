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

For v0.6.0, the expected public version is `0.6.0`.

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
