# NextMove Agent Prompt Templates

These platform-neutral templates help a non-technical user ask an Agent to use
NextMove. Replace the placeholders with privacy-reviewed text. If the Agent
cannot access NextMove, it must say so instead of simulating a Skill result.

Every template follows the same safety rule: use supplied facts only. Do not
invent experience, skills, education, projects, certifications, achievements,
employers, credentials, or metrics. Keep facts separate from suggestions. When
information is insufficient, say what is missing and preserve any structured
failure returned by NextMove.

## Complete Career Analysis

```text
Use the NextMove Skill to run the career_analysis capability.
Use privacy-reviewed input only.
If you cannot access NextMove, say so and do not simulate a Skill result.

Resume input:
RESUME_TEXT

Target job description:
JOB_DESCRIPTION

Rules:
- Use only facts present in my input.
- Do not invent experience, skills, education, projects, certifications,
  achievements, employers, credentials, or metrics.
- Clearly distinguish existing facts from suggestions.
- If information is insufficient or required input is missing, show the
  structured failure and do not improvise an answer.
- Do not change a match score or hide a NextMove warning.

Present the result in this order:
1. Top resume strengths and weaknesses from analysis.
2. Top three truthful priorities from improvement.
3. Job match, supported skills, and visible skill gaps from job_match.
4. Three practical next actions from career_advice.

Keep the explanation concise and remind me to verify every recommendation
against my real experience.
```

For Agent/Python `career_analysis`, both `resume` and `job_description` are
required.

## Resume Improvement

```text
Use the NextMove Skill to run the improve_resume capability.
Use privacy-reviewed input only.
If you cannot access NextMove, say so and do not simulate a Skill result.

Resume input:
RESUME_TEXT

Rules:
- Use only facts present in my resume.
- Do not invent experience, skills, education, projects, certifications,
  achievements, employers, credentials, or metrics.
- Keep facts separate from suggestions and label proposed wording as a draft.
- If information is insufficient, explain the gap instead of filling it in.
- Preserve any structured failure returned by NextMove.

Present:
1. The most important observed issues.
2. The top three improvement suggestions.
3. Sections I should revise first.
4. A checklist of evidence I should gather before rewriting.
```

## Job Matching

```text
Use the NextMove Skill to run the match_job capability.
Use privacy-reviewed input only.
If you cannot access NextMove, say so and do not simulate a Skill result.

Resume input:
RESUME_TEXT

Target job description:
JOB_DESCRIPTION

Rules:
- Use only facts present in the resume and job description.
- Do not invent experience, skills, education, projects, certifications,
  achievements, employers, credentials, or metrics.
- Clearly distinguish matched facts from suggestions for future development.
- Treat the score as directional, not a hiring prediction.
- If required input is missing or information is insufficient, show the
  structured failure and do not simulate a result.

Present:
1. Match score and its limitation.
2. Skills supported by the resume.
3. Skills visible in the role but missing from the resume.
4. Three truthful actions to improve fit or evidence.
```

## Career Planning

```text
Use the NextMove Skill to run the career_advice capability.
Use privacy-reviewed input only.
If you cannot access NextMove, say so and do not simulate a Skill result.

Resume input:
RESUME_TEXT

Rules:
- Use only facts present in my resume.
- Do not invent experience, skills, education, projects, certifications,
  achievements, employers, credentials, or metrics.
- Keep current facts separate from suggestions and possible future paths.
- If information is insufficient, explain which decisions need more evidence.
- Preserve any structured failure returned by NextMove.

Present:
1. Current career-level signal and its limitations.
2. Plausible paths supported by the input.
3. Visible skill gaps.
4. Three practical next actions for the next 30 days.

Do not present career advice as a guaranteed hiring outcome.
```

## Privacy reminder

Before using personal input, remove real names, phone numbers, email addresses,
addresses, identifiers, company-confidential information, credentials, and API
keys. Do not paste private career content into Pilot feedback.
