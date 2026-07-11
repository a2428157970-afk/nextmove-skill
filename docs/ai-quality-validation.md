# AI Enhancement Quality Validation

## Purpose

Epic-014 provides a repeatable, offline-first contract check for optional
Resume AI Enhancement. It verifies deterministic safety and regression rules;
it does not claim to measure real-model semantic quality. Human review remains
the final authority for semantic quality.

## Resume Prompt and Output Contract

`resume-improvement.v1` requires an exact JSON object with `contract_version`,
`summary`, `rewritten_content`, `improvement_points`, `keyword_suggestions`,
and `factual_warnings`. The parser rejects non-JSON text, code fences, wrong
versions, missing or mistyped fields, empty summary and rewritten content, and
debug output. Invalid responses degrade to `AI provider response error`.

## Offline Samples and Metrics

Eight fully synthetic cases under `tests/fixtures/ai_quality/` cover new
graduates, experienced technical roles, product operations, managers, career
switchers, incomplete information, verified metrics, and cases where metrics
must not be invented. Each case records structured Core output, facts to
preserve, prohibited fabrication, an expected improvement direction, optional
keywords, and output-length bounds.

Every case receives ten deterministic checks: provider success, non-empty
output, length, expected direction, fact preservation, prohibited content,
sensitive information, provider-internal errors, serialization, and unchanged
Core output. A case passes only with 10/10 checks. The initial gate requires
100% passing safe samples, failure regressions, Core immutability, sensitive
information checks, serialization checks, and zero default network calls.

## Failure Matrix and Safety

The regression matrix covers missing/disabled providers, unhealthy and
exceptional health checks, timeout, unavailable and response errors, invalid
transport JSON, empty provider content, limits, disabled live requests, feature
flags, and retry policy. Failures must remain structured and must not expose
provider internals or alter the rule-based result.

The evaluator is test-only. It uses strings, field checks, length checks,
serialization, and fixed rules only—no AI judge, embedding, SDK, credential
lookup, network call, or third-party evaluation framework. Its reports exclude
resume text, generated content, request data, and credentials.

## Running Offline Evaluation

```bash
python scripts/run_ai_quality_evaluation.py
python scripts/run_ai_quality_evaluation.py --format json
```

The runner exits 0 when all cases pass, 1 for quality failures, and 2 for
configuration or execution errors. `--scenario fabricated`, `empty`, and
`provider-error` exercise deterministic failing paths.

## Live Observation Boundary

Live quality observation remains opt-in through `RUN_LIVE_AI_TEST=true` and
the existing external `NEXTMOVE_LIVE_TRANSPORT_FACTORY` assembly hook. Missing
configuration skips safely. A compatible external validator may expose
`evaluate_quality()` and return only case ID, success, latency, output length,
passed-check count, and failed-check names. It must not print or store prompts,
resumes, headers, credentials, or raw provider output.

Live observation is not a default CI gate and is used only to observe real
provider output; it does not replace offline contract checks or human review.

## Experimental Live Pilot

Epic-016 adds an opt-in pilot record for up to five synthetic cases. It runs
only with `RUN_LIVE_AI_TEST=true` and the external transport factory. Each real
output must pass the same v1 parser and validator before metrics are recorded.
Records contain only case ID, contract version, provider/model names, success,
latency, output length, validator result, and human-review status/notes. They
never retain a resume, prompt, credential, header, or provider response. The
pilot is experimental and human review remains the final quality decision.
