# How to Read Your NextMove Report

NextMove returns structured career decision support. It does not guarantee a
job outcome, verify every detail of your career history, or replace human
judgment. Check every statement against the resume and role you supplied.

## The four report sections

| Section | Question it answers | How to use it |
|---|---|---|
| `analysis` | What does my resume currently communicate? | Review strengths, weaknesses, skill signals, and career level. A career-level label is a rule-based signal, not a final judgment. |
| `improvement` | What should I change first? | Prioritize evidence-backed changes. Never add a claim only because it appears in a suggestion. |
| `job_match` | How well does this resume support the target role? | Treat the match score as directional. Verify matched and missing skills against both inputs. |
| `career_advice` | What could I do next? | Choose a small number of practical actions and validate major decisions with human judgment. |

## Five-part action view

Ask your Agent to summarize the unchanged report as:

```text
Top strengths
Top three improvements
Job match
Visible skill gaps
Next three actions
```

This view is for readability. It must not change scores, add facts, or hide
warnings and errors from `CareerAnalysisReport`.

## Truthfulness check

Before acting on the report, ask:

1. Is every claimed experience, skill, project, certification, employer, and
   metric present in my source material?
2. Are proposed changes clearly labeled as suggestions rather than existing
   facts?
3. Does a missing skill mean I lack it, or only that the resume lacks evidence?
4. Is the recommendation practical for my situation and timeline?

Reject unsupported claims. Do not copy invented content into a resume.

## Choosing next actions

Start with actions that are truthful, specific, and achievable. A useful first
week might include gathering evidence for one accomplishment, improving one
resume section, and researching one visible skill gap. Re-run the analysis only
after the input has genuinely changed.

## Understanding a structured failure

A structured failure is not career analysis. It may indicate missing resume
text, a missing Agent `job_description`, an unreadable CLI file, or an
unsupported capability. Correct the input and call NextMove again. The Agent
must not replace a structured failure with a simulated or invented report.

## Share privacy-safe feedback

Use the [Pilot Feedback Template](pilot-feedback-template.md) to rate clarity
and value without submitting your resume, job description, identity, contact
details, employer information, or credentials.
