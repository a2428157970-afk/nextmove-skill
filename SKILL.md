---
name: nextmove-career-intelligence
description: Analyze and improve resumes, match candidates to job descriptions, provide career advice, or run a complete structured career analysis. Use when an agent needs offline, provider-neutral career intelligence from resume text and an optional job description.
---

# NextMove Career Intelligence

## Purpose

Use `NextMoveSkill` to turn resume and job-description inputs into deterministic, structured career intelligence. Prefer `career_analysis` when a complete report is needed.

## Supported capabilities

- Call `analyze_resume` to identify strengths, weaknesses, skills, and career level.
- Call `improve_resume` to produce issues, suggestions, and improved-section guidance.
- Call `match_job` to compare a resume with a job description.
- Call `career_advice` to produce career paths, skill gaps, and next actions.
- Call `career_analysis` to execute all four capabilities in the documented order and return one `CareerAnalysisReport`.

## Input format

Instantiate `NextMoveSkill`, then call `run(capability, payload)`. Supply `resume` as raw text or a Python `ResumeProfile`. Supply `job_description` as text for `match_job` and `career_analysis`.

```python
from skill import NextMoveSkill

response = NextMoveSkill().run(
    "career_analysis",
    {"resume": resume_text, "job_description": job_description},
)
```

## Output format

Use `skill.utils.to_dict()` before JSON serialization. `run()` returns a `SkillResponse`. A successful `career_analysis` call contains a `CareerAnalysisReport` with `analysis`, `improvement`, `job_match`, and `career_advice`. On a workflow failure, inspect `failed_capability` and `error`; later results remain `null`.

## Limitations

- Treat results as career decision support, not guaranteed hiring outcomes or professional legal advice.
- Expect deterministic rule-based analysis; nuanced context may require human review.
- Provide plain resume text for offline Agent use; Python-only `ResumeProfile` objects are not portable JSON inputs.
- Do not infer facts, credentials, employment history, or metrics absent from the input.
