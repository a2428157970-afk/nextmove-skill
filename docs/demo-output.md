# Career Intelligence Demo Output

This document shows how a developer can read the structured output from the
complete NextMove workflow. The example uses fictional, non-identifying data
and runs entirely without an AI provider.

## Input

```text
Candidate A

Summary
Backend engineer focused on Python APIs and internal tooling.

Experience
Built Python APIs with FastAPI and SQL.

Skills
Python, FastAPI, SQL, Testing
```

The job description requests Python, FastAPI, SQL, Docker, and API testing.

## Workflow

```text
Resume Text
    ↓
analyze_resume
    ↓
improve_resume
    ↓
match_job
    ↓
career_advice
```

The runnable version is [examples/full_career_analysis.py](../examples/full_career_analysis.py).

## Compact JSON Output

Each capability returns the same response envelope: `success`, `capability`,
`result`, and `error`. The fields below are abbreviated only for readability;
the values illustrate the real output structure.

```json
{
  "analysis": {
    "success": true,
    "capability": "analyze_resume",
    "result": {
      "strengths": ["Clear summary", "Relevant technical keywords"],
      "weaknesses": ["Limited skills section", "No project experience"],
      "skill_assessment": {
        "strengths": ["Technical keywords are visible"],
        "gaps": ["Add role-relevant keywords"],
        "notes": null
      },
      "career_level": "junior"
    },
    "error": null
  },
  "improvement": {
    "success": true,
    "capability": "improve_resume",
    "result": {
      "issues": ["No project experience"],
      "suggestions": ["Add projects with contribution and outcome"],
      "improved_sections": {
        "projects": ["Describe the problem, technologies, and result"]
      }
    },
    "error": null
  },
  "job_match": {
    "success": true,
    "capability": "match_job",
    "result": {
      "match_score": 68,
      "matched_skills": ["Python", "FastAPI", "SQL"],
      "missing_skills": ["Docker", "API"],
      "recommendations": ["Add truthful evidence for missing keywords"]
    },
    "error": null
  },
  "career_advice": {
    "success": true,
    "capability": "career_advice",
    "result": {
      "current_level": "junior",
      "possible_paths": ["backend engineer", "software engineer"],
      "skill_gaps": ["Add projects that demonstrate practical capability"],
      "recommended_actions": ["Add measurable achievements"]
    },
    "error": null
  }
}
```

Use `skill.utils.to_dict()` before serializing a response with `json.dumps()`.
This preserves the response envelope while converting nested dataclasses into
JSON-compatible values.
