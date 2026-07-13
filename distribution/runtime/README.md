# NextMove Runtime Skill Package

This is the executable, offline NextMove Runtime Package. It includes the
actual `skill/` Python implementation, packaging metadata, fictional samples,
and a readiness checker. Python 3.11 or later is required; NextMove has no
third-party runtime dependency.

Do not infer readiness from `SKILL.md` or `skill.json`. Only a successful import,
real `career_analysis` smoke execution, JSON serialization check, and zero
network-call check may print `NEXTMOVE_READY`.

Start with [QUICK_START.md](QUICK_START.md). Prompt templates are in
[PROMPTS.md](PROMPTS.md). The package is career decision support, not an
employment guarantee.

## Contents

- `skill/`: unchanged NextMove runtime implementation;
- `pyproject.toml`: Python package configuration;
- `scripts/check_skill_package.py`: offline readiness preflight;
- `scripts/run_human_career_report.py`: explicit internal report demonstration;
- `examples/`: fictional HR, technology, and transition inputs;
- `PACKAGE_MANIFEST.json`: versions, mode, file inventory, and checksums.

Never submit credentials or unredacted personal information with feedback.
