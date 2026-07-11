# NextMove AI Career Intelligence Skill

[![Release](https://img.shields.io/badge/release-v0.6.0-blue)](docs/release.md)
[![Skill tests](https://img.shields.io/badge/skill%20tests-passing-brightgreen)](.github/workflows/test.yml)

NextMove is a provider-neutral Python Skill framework for turning resume and
job-description inputs into structured career intelligence. It is designed to
be called directly by Python applications today and connected to AI Agents
through a thin Agent layer without coupling the Skill Core to a model provider,
web framework, or transport protocol.

> Know Your Value. Find Your Next Career Move.

## 1. Project Introduction

NextMove separates career intelligence from delivery mechanisms. The core
accepts a raw resume string or a structured `ResumeProfile`, applies
deterministic first-pass career analysis, and returns typed result objects or
structured `SkillResponse` envelopes.

It currently has no OpenAI, Claude, Gemini, MCP, backend, or frontend runtime
dependency.

## 2. Features

- **Resume Analysis** — identify strengths, weaknesses, skill signals, and an
  inferred career level.
- **Resume Improvement** — produce issues, actionable suggestions, and
  improved-section guidance.
- **Job Matching** — compare a resume against a job description, returning a
  match score, matched skills, gaps, and recommendations.
- **Career Advice** — suggest career paths, skill gaps, and next actions from
  a resume and optional analysis.

## 3. Installation

NextMove requires Python 3.11 or later. Install the local package in editable
mode:

```bash
pip install -e .
```

## 4. Quick Start

Run the end-to-end career analysis demo:

```bash
python examples/full_career_analysis.py
```

The demo runs Resume Analysis, Resume Improvement, Job Matching, and Career
Advice, then prints a structured JSON report. See
[docs/demo-output.md](docs/demo-output.md) for a concise response example.

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

## 5. Python API

`NextMoveSkill` is the primary Skill API. `run()` accepts a capability name and
a payload dictionary, then returns a `SkillResponse` with `success`,
`capability`, `result`, and `error` fields.

```python
from skill import NextMoveSkill
from skill.utils import to_dict

skill = NextMoveSkill()
response = skill.run(
    "match_job",
    {
        "resume": "Backend engineer with Python, FastAPI, and SQL experience.",
        "job_description": "Backend role requiring Python, FastAPI, SQL, and Docker.",
    },
)

print(to_dict(response))
```

Supported capabilities are `analyze_resume`, `improve_resume`, `match_job`,
and `career_advice`. See [examples/full_career_analysis.py](examples/full_career_analysis.py)
for a complete four-capability report.

## 6. Agent Runtime

`AgentRuntime` is an optional Agent entry point. It resolves an `AgentTool`
name through the built-in Tool Registry and forwards the matching capability to
`NextMoveSkill.run()`.

```python
from skill.agent import AgentRuntime
from skill.utils import to_dict

runtime = AgentRuntime()
response = runtime.invoke(
    "analyze_resume",
    {"resume": "Backend engineer with Python and SQL experience."},
)

print(to_dict(response))
```

Tool names map directly to the built-in capability names. An unknown tool
returns a failed `SkillResponse` with the `UNKNOWN_TOOL` error code.

## 7. Architecture

```text
Resume / Job Description
          ↓
    NextMoveSkill API
          ↓
Skill Core: parser, analyzer, improver, matcher, advisor
          ↓
Structured result dataclasses / SkillResponse
          ↓
Optional Agent Layer: tools, registry, runtime
          ↓
Future provider adapters
```

The Skill Core is intentionally independent from Agent providers and Web
delivery. Read [docs/architecture.md](docs/architecture.md) for layer
responsibilities and extension boundaries.

## 8. Optional AI Enhancement

NextMove continues to run its four Skill Core capabilities with deterministic,
rule-based logic by default. AI is an optional enhancement layer; it neither
manages API keys nor reads environment variables. Applications inject the
credential provider, provider factory, and transport they own. If a provider is
unavailable or the feature is disabled, the result is a structured
`AIEnhancementResult` failure and the Skill Core continues to work.

The offline demonstration creates `AIProviderSettings`, injects a
`CredentialProvider`, `ProviderFactory`, and opaque transport through
`ApplicationRuntimeAdapter`, then uses `ResumeAIEnhancer`. It uses only the
deterministic `MockProviderAdapter` and emits serializable JSON:

```bash
python examples/ai_enhancement_demo.py
```

Run the deterministic, offline quality contract evaluation:

```bash
python scripts/run_ai_quality_evaluation.py
```

It checks synthetic samples for fact preservation, actionable directions,
fabrication, sensitive-content leakage, serialization, and Core immutability.
See [AI quality validation](docs/ai-quality-validation.md) for scope and
limitations.

Run the deterministic, offline quality contract evaluation:

```bash
python scripts/run_ai_quality_evaluation.py
```

It checks synthetic samples for fact preservation, actionable directions,
fabrication, sensitive-content leakage, serialization, and Core immutability.
See [AI quality validation](docs/ai-quality-validation.md) for scope and
limitations.

## 9. Examples

- [Full career analysis](examples/full_career_analysis.py): analyze, improve,
  match, and advise in one JSON report.
- [Resume analysis](examples/analyze_resume.py): a focused analysis call.
- [Job matching](examples/match_job.py): a focused job-match call.
- [Agent runtime](examples/agent_demo.py): Agent Tool invocation through the
  optional runtime.

## 10. Development

Keep the Skill Core modular and provider-neutral. Changes to a capability
should include its schema, focused behavior tests, and public-interface tests
where appropriate.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the Skill-first contribution
workflow and architecture constraints.

## 11. Release

NextMove Skill v0.6.0 is the current release. Follow the
[release checklist](docs/release.md) to validate an install, import, demo, and
test run from a fresh clone.
