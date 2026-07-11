# Task 5 Report: Application-to-Skill Dependency Boundary Tests

## Scope

- Added static dependency-boundary coverage in `tests/test_application_workflow.py` only.
- No Application or Skill production code was changed.

## TDD Record

### RED

Command:

```powershell
python -m unittest tests.test_application_workflow.ApplicationWorkflowTests.test_static_scan_rejects_direct_skill_implementation_imports
```

Result: failed as expected because the initial scanner returned no forbidden imports. The assertion expected `from skill.analysis import ResumeAnalyzer` to be reported.

### GREEN

Implemented an AST-based scanner that permits only `skill`, `skill.schemas` (including submodules), and `skill.utils` (including submodules) in Application sources. It reports direct Skill implementation imports with source file and line information.

Command:

```powershell
python -m unittest tests.test_application_workflow.ApplicationWorkflowTests.test_static_scan_rejects_direct_skill_implementation_imports tests.test_application_workflow.ApplicationWorkflowTests.test_application_imports_only_public_skill_interfaces
```

Result: `Ran 2 tests ... OK`.

## Verification

- `python -m unittest discover -s tests -p 'test_*.py'` — 134 tests passed, 3 skipped.
- `python -m compileall application skill tests` — completed successfully.
- `git diff --check` — completed with no whitespace errors.

## Notes

The static Application scan passes on the current tree. Its approved import surface is the public `skill` root plus `skill.schemas` and `skill.utils`; direct imports such as `skill.analysis`, `skill.matching`, `skill.career`, `skill.improvement`, and `skill.resume` are rejected by the scanner.

## Follow-up Fix: Root Import Alias Bypass

### Finding and root cause

The original AST helper inspected `ImportFrom.module`, so every statement of the
form `from skill import <alias>` appeared as the public root module `skill`.
That accidentally allowed implementation-module aliases such as `analysis` and
`matching`, despite correctly rejecting direct submodule imports.

### RED

Added `test_static_scan_rejects_root_import_implementation_module_aliases` with
one root import for each forbidden implementation module: `analysis`,
`matching`, `career`, `improvement`, and `resume`.

Command:

```powershell
python -m unittest tests.test_application_workflow.ApplicationWorkflowTests.test_static_scan_rejects_root_import_implementation_module_aliases
```

Result: failed as expected. The scanner returned `[]` while the test expected
five forbidden root-import aliases.

### GREEN

Added a test-only `PRIVATE_SKILL_ROOT_IMPORTS` set and made the helper inspect
the aliases of `from skill import ...` statements before treating the public
root import as allowed. Public root imports, including `NextMoveSkill` and
`SkillError`, remain permitted; the existing direct-submodule rejection remains
covered.

Focused verification command:

```powershell
python -m unittest tests.test_application_workflow.ApplicationWorkflowTests.test_static_scan_rejects_direct_skill_implementation_imports tests.test_application_workflow.ApplicationWorkflowTests.test_static_scan_rejects_root_import_implementation_module_aliases tests.test_application_workflow.ApplicationWorkflowTests.test_application_imports_only_public_skill_interfaces
```

Result: `Ran 3 tests ... OK`.

### Final verification

- `python -m unittest discover -s tests -p 'test_*.py'` — 135 tests passed, 3 skipped.
- `python -m compileall application skill tests` — completed successfully.
- `git diff --check` — completed with no whitespace errors.
- Scope check — only `tests/test_application_workflow.py` and this Task 5 report are included in the follow-up commit; no production source changes.
