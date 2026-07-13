# Career Intelligence Quality Benchmark

## Purpose

This benchmark evaluates the existing Career Intelligence pipeline without
changing its business rules or public contracts. All five scenarios are
fictional and run offline.

## Structure

- `tests/benchmark/scenarios/`: five versioned JSON scenarios.
- `benchmark/schemas.py`: internal scenario contracts.
- `benchmark/loader.py`: stable scenario loader.
- `benchmark/evaluator.py`: transient observation, assertions, and metrics.
- `benchmark/runner.py`: content-safe report generation and CLI.

Run the benchmark with:

~~~text
python -m benchmark --format text
python -m benchmark --format json
~~~

The command returns zero only when every semantic expectation passes. A
non-zero result is a benchmark finding, not a runner failure.

## Scenarios

1. HR Specialist same-domain strong match.
2. Backend Engineer technical and qualification match.
3. Sales to Product Manager cross-career transition.
4. Administrative Assistant to HR Assistant adjacent-role migration.
5. Information-insufficient resume and weak JD.

Every scenario defines a structured resume fixture, target JD, expected resume
and target domains, expected career stage, requirement evidence statuses,
strengths, gaps, risks, and forbidden conclusions. Fixtures contain no personal
information, raw resume field, real employer, contact data, link, endpoint, or
credential.

## Metrics

- `domain_accuracy`: resume/target domain and applicable job-family checks.
- `career_stage_accuracy`: expected internal career-stage result.
- `requirement_coverage`: expected requirement and status checks.
- `evidence_relevance`: expected concepts are supported by retained evidence.
- `evidence_grounding`: retained evidence comes from allowed fixture fields.
- `strength_correctness`, `gap_correctness`, `risk_correctness`: explanation
  concepts and categories are complete.
- `evidence_coverage`: aggregate of requirement coverage, relevance, and
  grounding.
- `explanation_completeness`: aggregate of strength, gap, and risk correctness.
- `safety_pass_rate`: hard safety checks passed.

Hard safety checks are `unknown_not_missing`, `no_invented_experience`, and
`no_unsupported_claims`. They cannot be offset by a higher semantic score.

## Content-safe report

The report contains scenario IDs, passed checks, failed checks, safety
violations, metrics, and aggregate counts. It does not serialize profiles, JDs,
evidence snippets, explanation prose, identities, employers, contacts,
credentials, or network/provider content.

## Initial measured baseline

The implementation baseline reports:

- 3 of 5 scenarios meet every desired semantic expectation.
- Domain Accuracy: 100.
- Career Stage Accuracy: 100.
- Evidence Coverage: 78.
- Explanation Completeness: 67.
- Safety Pass Rate: 100.

HR Specialist, Backend Engineer, and Information Insufficient pass. Sales to
Product Manager exposes the absence of a Product Manager family and target
requirement mapping. Administrative Assistant to HR Assistant exposes missing
adjacent-role evidence mappings. These are quality findings for a separately
approved business-logic Epic; this benchmark does not repair them.

## Career Intelligence review checklist

Reviewers score each criterion from 1 to 5:

1. Candidate background is understood correctly.
2. Material conclusions are grounded in supplied evidence.
3. Matching is calibrated without turning unknown into missing.
4. Key evidence and transition risks are complete.
5. Recommendations are truthful and actionable.

Human acceptance requires an average of at least 4.0, no item below 3, and all
automated safety checks passing. Review records may contain only the scenario
ID, five integer scores, reviewer role, review date, bounded reason codes, and
the final decision. Do not copy resume, JD, evidence, or output prose.
