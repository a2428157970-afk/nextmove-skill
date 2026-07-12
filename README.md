# NextMove AI Career Intelligence Skill

[![Release](https://img.shields.io/badge/release-v0.8.0-blue)](docs/release.md)
[![Skill tests](https://img.shields.io/badge/skill%20tests-passing-brightgreen)](.github/workflows/test.yml)

NextMove v0.8.0 is Developer Preview Ready: an installable, provider-neutral
Python Skill that turns resume and job-description inputs into structured
career intelligence. It supports direct Python calls and a thin Agent layer
without coupling the Skill Core to a model provider, web framework, database,
or transport protocol.

> Know Your Value. Find Your Next Career Move.

## 1. What NextMove does

NextMove accepts raw resume text or a structured `ResumeProfile`, applies
deterministic first-pass career analysis, and returns typed result objects or a
structured `SkillResponse` envelope.

- **Resume Analysis** - identify strengths, weaknesses, skill signals, and an
  inferred career level.
- **Resume Improvement** - produce issues, truthful suggestions, and
  improved-section guidance.
- **Job Matching** - compare a resume with a job description and return a score,
  matched skills, gaps, and recommendations.
- **Career Advice** - suggest career paths, skill gaps, and next actions.
- **Career Analysis** - run all four capabilities in a fixed, fail-fast order.

The default Skill, CLI, demo, and test workflows run offline. They do not need a
hosted service, API credential, model SDK, backend, or frontend.

## 2. Installation

NextMove requires Python 3.11 or later, pip, and setuptools 61 or later. From
the repository root, install the package in editable mode:

```bash
python -m pip install -e .
```

An offline machine must already have a compatible build backend installed;
otherwise pip build isolation may try to resolve setuptools from a package
index. NextMove itself has no runtime package dependencies.

## 3. Quick start

Run the installed CLI with a UTF-8 plain-text resume:

```bash
nextmove analyze --resume resume.txt --job-description "Backend role requiring Python and SQL."
```

The equivalent module entrypoint is:

```bash
python -m skill analyze --resume resume.txt
```

`--job-description` is optional only at the CLI boundary. When omitted, the
CLI passes an empty string to the unchanged Skill API. Python and Agent calls
must provide `job_description` for `match_job` and `career_analysis`.

Run the offline product demo:

```bash
python examples/skill_demo.py
```

The demo prints a JSON `SkillResponse` containing a `CareerAnalysisReport`.
See [docs/demo-output.md](docs/demo-output.md) for a concise output example.

## 4. Python API

`NextMoveSkill.run` is the primary Skill entrypoint. It accepts a capability
name and payload dictionary and returns `success`, `capability`, `result`, and
`error` fields.

```python
from skill import NextMoveSkill
from skill.utils import to_dict

response = NextMoveSkill().run(
    "career_analysis",
    {
        "resume": "Backend engineer with Python, FastAPI, and SQL experience.",
        "job_description": "Backend role requiring Python, SQL, and Docker.",
    },
)

print(to_dict(response))
```

Supported capabilities are `analyze_resume`, `improve_resume`, `match_job`,
`career_advice`, and `career_analysis`.

## 5. Entrypoint contract

The Skill and CLI entrypoints have different responsibilities:

- `NextMoveSkill.run` is the Skill entrypoint for Python and Agent consumers.
- `skill.__main__:main` is the CLI entrypoint used by `python -m skill` and the
  installed `nextmove` command.
- The legacy `skill.json` field `entrypoint` remains the CLI entrypoint for
  compatibility. Explicit `skill_entrypoint` and `cli_entrypoint` fields remove
  ambiguity for new consumers.

Machine-readable metadata is available in [skill.json](skill.json). Agent usage
instructions are in [SKILL.md](SKILL.md), and the evidence-based ecosystem
status is in [docs/agent-compatibility.md](docs/agent-compatibility.md).

## 6. Agent Runtime

`AgentRuntime` resolves a built-in Agent Tool name and forwards its capability
to `NextMoveSkill.run`.

```python
from skill.agent import AgentRuntime
from skill.utils import to_dict

response = AgentRuntime().invoke(
    "analyze_resume",
    {"resume": "Backend engineer with Python and SQL experience."},
)

print(to_dict(response))
```

An unknown tool returns a failed `SkillResponse` with the `UNKNOWN_TOOL` error
code.

## 7. Architecture

```text
Resume / Job Description
          -> NextMoveSkill API
          -> Skill Core: parser, analyzer, improver, matcher, advisor
          -> Structured dataclasses / SkillResponse
          -> Optional Agent Layer: tools, registry, runtime
          -> Optional provider adapters
```

The Skill Core remains independent from Agent providers and Web delivery. Read
[docs/architecture.md](docs/architecture.md) for layer responsibilities.

## 8. Optional AI enhancement

Rule-based Skill Core behavior remains the default. AI is an optional
enhancement layer; it does not own credentials or read environment variables.
Applications inject any credential provider, provider factory, and transport.
The offline demonstration uses only deterministic mock components:

```bash
python examples/ai_enhancement_demo.py
```

Run the deterministic offline quality evaluation:

```bash
python scripts/run_ai_quality_evaluation.py
```

It checks synthetic samples for fact preservation, actionable directions,
fabrication, sensitive-content leakage, serialization, and Core immutability.
See [docs/ai-quality-validation.md](docs/ai-quality-validation.md).

## 9. Examples

- [Skill product demo](examples/skill_demo.py)
- [Full career analysis](examples/full_career_analysis.py)
- [Resume analysis](examples/analyze_resume.py)
- [Job matching](examples/match_job.py)
- [Agent runtime](examples/agent_demo.py)

## 10. Development and validation

Keep the Skill Core modular and provider-neutral. See
[CONTRIBUTING.md](CONTRIBUTING.md) for contribution rules.

Run the release checks:

```bash
nextmove --help
python examples/skill_demo.py
python -m unittest discover -s tests -v
python -m compileall skill tests examples
```

## 11. Release status

The v0.8.0 codebase is Developer Preview Ready. Creating the Git tag and public
release remains a separate, human-approved action. Review the
[release checklist](docs/release.md) and
[v0.8.0 release note](docs/release/v0.8.0.md) before publishing.
