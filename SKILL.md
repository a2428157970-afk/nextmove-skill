---
name: nextmove-career-intelligence
description: Analyze and improve resumes, match candidates to job descriptions, provide career advice, or run a complete structured career analysis. Use when an agent needs offline, provider-neutral career intelligence from resume text, with a job description required for matching and complete analysis.
---

# NextMove Career Intelligence

## Purpose

Use `NextMoveSkill` to turn resume and job-description inputs into deterministic, structured career intelligence. Prefer `career_analysis` when a complete report is needed.

## Operational manifest

- Discover the product as `NextMove`; use the lowercase frontmatter name only as the Agent Skill identifier.
- Read version `0.8.0` from `skill.__version__.__version__` as the authoritative source.
- Invoke the Skill entrypoint as `NextMoveSkill.run`. Invoke the separate CLI entrypoint `skill.__main__:main` through `python -m skill` or the installed `nextmove` command. The legacy manifest `entrypoint` remains the CLI entrypoint for compatibility.
- Discover the machine-readable capability list, input schema, and output schema in `skill.json` or `skill.metadata.SKILL_METADATA`; both expose the same contract.
- Require `resume` and `job_description` in the `career_analysis` Agent/Python input schema. Expect a JSON `SkillResponse` containing `success`, `capability`, `result`, and `error`; `result` contains the `CareerAnalysisReport`.

## When to use

Use this Skill when an Agent needs to review a resume, identify improvement opportunities, compare a candidate with a target role, suggest career directions, or produce a complete career analysis. Use the combined capability for end-to-end requests and a focused capability for a single question.

## Supported capabilities

- Call `analyze_resume` to identify strengths, weaknesses, skills, and career level.
- Call `improve_resume` to produce issues, suggestions, and improved-section guidance.
- Call `match_job` to compare a resume with a job description.
- Call `career_advice` to produce career paths, skill gaps, and next actions.
- Call `career_analysis` to execute all four capabilities in the documented order and return one `CareerAnalysisReport`.

## Input format

For Python or Agent calls, instantiate `NextMoveSkill`, then call `run(capability, payload)`. Supply `resume` as raw text or a Python `ResumeProfile`. Supply `job_description` for `match_job` and `career_analysis`; this public API field remains required.

For the CLI, pass a UTF-8 plain-text resume file to `--resume`. The CLI accepts an optional `--job-description`; when omitted, it passes an empty string to the unchanged Skill API.

```python
from skill import NextMoveSkill

response = NextMoveSkill().run(
    "career_analysis",
    {"resume": resume_text, "job_description": job_description},
)
```

A Python caller may provide a structured profile directly:

```python
from skill import NextMoveSkill
from skill.schemas import ResumeProfile

profile = ResumeProfile(
    summary="Backend engineer focused on Python services.",
    skills=["Python", "SQL"],
    raw_text="Backend engineer focused on Python services. Skills: Python, SQL.",
)
response = NextMoveSkill().run(
    "career_analysis",
    {
        "resume": profile,
        "job_description": "Backend role requiring Python, SQL, and Docker.",
    },
)
```

Agent payloads should use raw resume text because Python dataclass instances are not portable JSON values.

## Output format

Use `skill.utils.to_dict()` before JSON serialization. `run()` returns a `SkillResponse`. A successful `career_analysis` call contains a `CareerAnalysisReport` with `analysis`, `improvement`, `job_match`, and `career_advice`. On a workflow failure, inspect `failed_capability` and `error`; later results remain `null`.

The report sections mean:

- `analysis`: resume strengths, weaknesses, skill assessment, and career level.
- `improvement`: observed issues, truthful suggestions, and section guidance.
- `job_match`: match score, supported skill matches, gaps, and recommendations.
- `career_advice`: possible paths, skill gaps, and recommended next actions.

Minimal successful envelope:

```json
{
  "success": true,
  "capability": "career_analysis",
  "result": {
    "success": true,
    "analysis": {},
    "improvement": {},
    "job_match": {},
    "career_advice": {},
    "failed_capability": null,
    "error": null
  },
  "error": null
}
```

Minimal failed envelope:

```json
{
  "success": false,
  "capability": "career_analysis",
  "result": null,
  "error": {
    "code": "INVALID_INPUT",
    "message": "\"payload requires 'job_description'\""
  }
}
```

## Limitations

- Treat results as career decision support, not guaranteed hiring outcomes or professional legal advice.
- Expect deterministic rule-based analysis; nuanced context may require human review.
- Provide plain resume text for offline Agent use; Python-only `ResumeProfile` objects are not portable JSON inputs.
- Do not infer or invent facts, credentials, employment history, projects, skills, achievements, or metrics absent from the input.
- Accept only plain UTF-8 resume text through the CLI; PDF and Word extraction are outside this Skill entrypoint.

## Examples

Run the installed CLI with a target job:

```bash
nextmove analyze --resume resume.txt --job-description "Backend role requiring Python and SQL."
```

Run without a target job:

```bash
python -m skill analyze --resume resume.txt
```

Both commands print a JSON `SkillResponse` whose `result` is a `CareerAnalysisReport`.

## Pilot templates

Non-technical users can start with the copyable
[Agent Prompt Templates](docs/agent-prompt-template.md) and the
[Output Guide](docs/output-guide.md). These documents are user-facing wrappers
around the unchanged Skill contract; they do not authorize an Agent to invent
facts or simulate a response when NextMove is unavailable.
