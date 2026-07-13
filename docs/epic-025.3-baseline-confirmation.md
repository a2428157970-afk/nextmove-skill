# Epic-025.3 Baseline Confirmation Report

Date: 2026-07-13

Baseline commit: `79fafb940d87754ae086a0bc6a9e748c3e7f62a6` (`79fafb9 merge: integrate Epic-025.2 career stage model`)

Branch: `codex/epic-025.3-evidence-based-match-explanation`

Worktree: `D:\1.Project\NextMove\.worktrees\codex\epic-025.3-evidence-based-match-explanation-v2`

## Result

Epic-025.3 may start from this baseline. The requested matching and career modules exist, the core classes import successfully, the `JobMatcher` facade composes the domain classifier and scorer, and `CareerStageAssessment` is available for internal use. The worktree is based on the requested latest `main` commit.

## Matching baseline

Confirmed files:

- `skill/matching/taxonomy.py`
- `skill/matching/classifier.py`
- `skill/matching/scoring.py`
- `skill/matching/matcher.py`
- `skill/matching/schemas.py`

Confirmed callable imports:

- `skill.matching.classifier.DomainClassifier`
- `skill.matching.scoring.MatchScorer`
- `skill.matching.matcher.JobMatcher`

Confirmed facade integration:

- `JobMatcher.__init__()` creates a `DomainClassifier` and `MatchScorer`.
- `JobMatcher.match()` classifies the resume and job description, passes both classifications to `MatchScorer.assess()`, and maps the returned internal `MatchAssessment` to the unchanged public `JobMatchResult`.
- `MatchScorer.assess()` remains the score owner and returns the aggregate score, confidence, component scores, strengths, gaps, matched skills, and missing skills.

Requirement-evidence handoff finding:

- The scorer's private `Requirement` currently carries `canonical` and `aliases`.
- `MatchAssessment` does not yet carry ordered per-requirement records, requirement kind or priority, evidence source/text, a requirement status, or per-requirement score contribution.
- Epic-025.3 Requirement Evidence Mapping must therefore enrich the internal scorer handoff without re-extracting requirements in a separate explanation layer and without changing score weights.

## Career baseline

Confirmed files:

- `skill/career/stages.py`
- `skill/career/stage_assessor.py`
- `skill/career/advisor.py`

Confirmed internal availability:

- `CareerStageAssessment` imports from `skill.career.stages`.
- `CareerStageAssessor.assess()` returns `CareerStageAssessment`.
- `CareerAdvisor` consumes `CareerStageAssessment` internally for legacy level mapping and stage-specific actions.
- `ResumeAnalyzer` also invokes `CareerStageAssessor` internally.

## Verification evidence

Import probe:

```text
DomainClassifier MatchScorer JobMatcher CareerStageAssessment
```

Focused baseline suite:

```text
python -m unittest tests.test_matching_classifier tests.test_matching_scoring tests.test_job_matcher tests.test_career_stage_assessor tests.test_career_advisor -v
Ran 49 tests
OK
```

Full baseline suite:

```text
python -m unittest discover -s tests -v
Ran 223 tests
OK (skipped=3)
```

The three skipped tests are the expected opt-in live AI tests guarded by `RUN_LIVE_AI_TEST=true`.

## Protected boundaries for implementation

Epic-025.3 implementation must not modify:

- `NextMoveSkill.run()` or `skill/interface.py`
- the six-field `JobMatchResult` public contract
- Agent contracts or schemas
- Application Layer code
- CLI code
- providers
- Git tags

No push or tag action is authorized.
