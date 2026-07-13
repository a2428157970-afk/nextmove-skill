# Runtime Quick Start

1. Extract the complete Runtime Package.
2. Confirm Python 3.11 or later: `python --version`.
3. From the extracted package, install locally with
   `python -m pip install --no-deps --no-build-isolation .`, or use the package
   directory directly on `PYTHONPATH`.
4. Run the real offline preflight:
   `python scripts/check_skill_package.py --package .`
5. Continue only when the final line is `NEXTMOVE_READY`.
6. Generate a fictional Human Career Report:
   `python scripts/run_human_career_report.py --scenario transition`

The preflight performs an actual `NextMoveSkill.run("career_analysis", ...)`
call and JSON serialization while network access is blocked. Discovering
`SKILL.md` or `skill.json` is not sufficient.

The sample files contain HR, technology, and career-transition sections. Use
`--scenario hr`, `--scenario technology`, or `--scenario transition`. Review
[PROMPTS.md](PROMPTS.md) before replacing them with privacy-reviewed inputs.
