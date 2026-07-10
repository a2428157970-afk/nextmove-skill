# NextMove AI Career Intelligence Skill

NextMove is a provider-neutral Python Skill framework for turning resume and
job-description inputs into structured career intelligence. It is designed to
be called directly by Python applications today and connected to AI Agents
through a thin Agent layer without coupling the Skill Core to a model provider,
web framework, or transport protocol.

> Know Your Value. Find Your Next Career Move.

## 1. What is NextMove

NextMove separates career intelligence from delivery mechanisms. The core
accepts a raw resume string or a structured `ResumeProfile`, applies
deterministic first-pass career analysis, and returns typed result objects or
structured `SkillResponse` envelopes.

It currently has no OpenAI, Claude, Gemini, MCP, backend, or frontend runtime
dependency.

## 2. Core Capabilities

- **Resume Analysis** — identify strengths, weaknesses, skill signals, and an
  inferred career level.
- **Resume Improvement** — produce issues, actionable suggestions, and
  improved-section guidance.
- **Job Matching** — compare a resume against a job description, returning a
  match score, matched skills, gaps, and recommendations.
- **Career Advice** — suggest career paths, skill gaps, and next actions from
  a resume and optional analysis.

## 3. Quick Start

NextMove requires Python 3.11 or later. Install the local package in editable
mode:

```bash
pip install -e .
```

Run the end-to-end career analysis demo:

```bash
python examples/full_career_analysis.py
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

## 4. Python API

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

## 5. Agent Runtime Usage

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

## 6. Architecture

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

## 7. Examples

- [Full career analysis](examples/full_career_analysis.py): analyze, improve,
  match, and advise in one JSON report.
- [Resume analysis](examples/analyze_resume.py): a focused analysis call.
- [Job matching](examples/match_job.py): a focused job-match call.
- [Agent runtime](examples/agent_demo.py): Agent Tool invocation through the
  optional runtime.

## 8. Development

Keep the Skill Core modular and provider-neutral. Changes to a capability
should include its schema, focused behavior tests, and public-interface tests
where appropriate.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the Skill-first contribution
workflow and architecture constraints.
