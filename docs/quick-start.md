# Try NextMove in 5 Minutes

NextMove helps you review a resume, identify truthful improvements, compare it
with a target role, and choose practical next actions. The fastest Pilot path is
to use an Agent that can access the NextMove Skill.

## Before you start

Protect your privacy. Remove your real name, phone number, email, address,
account identifiers, employer-confidential information, and credentials before
sharing career material with an Agent. Never ask NextMove to invent experience,
skills, education, projects, certifications, achievements, or metrics.

## Step 1: Copy a Prompt

Open [Agent Prompt Templates](agent-prompt-template.md) and copy **Complete
Career Analysis** into ChatGPT Agent, Claude, Cursor, Codex, or another Agent
that has access to NextMove.

## Step 2: Use the public sample

Paste these two entirely fictional inputs into the Prompt placeholders:

- [Sample resume](../examples/data/sample_resume.txt)
- [Sample job description](../examples/data/sample_job_description.txt)

Ask the Agent to invoke NextMove. Do not ask it to simulate a Skill result if
NextMove is unavailable; it should report that limitation clearly.

## Step 3: Check the result

A successful complete analysis contains:

- `analysis` - strengths, weaknesses, skill signals, and career level;
- `improvement` - truthful priorities for improving the resume;
- `job_match` - directional match score, supported skills, and visible gaps;
- `career_advice` - possible directions and practical next actions.

Use [How to Read Your NextMove Report](output-guide.md) to turn the structured
result into a short action list.

## Step 4: Try privacy-reviewed personal input

Replace the sample with your own resume text and target role only after removing
identifying and confidential information. Treat every output as decision
support, verify it against your source material, and reject any unsupported
claim.

## Step 5: Share anonymous feedback

Copy the [Pilot Feedback Template](pilot-feedback-template.md). It works in an
Agent conversation, community post, email, or Issue. Do not include resume or
job-description text in feedback.

Read [Pilot Guidelines](pilot-guidelines.md) for the data boundary and success
criteria. Developers and advanced users may also use the GitHub Pilot Issue
template.

## Secondary path: CLI

After installing NextMove, run the real sample resume offline:

```bash
nextmove analyze --resume examples/data/sample_resume.txt --job-description "Fictional junior role requiring Python, SQL, Docker, and cloud deployment."
```

The current CLI accepts job-description text inline. `--job-description-file`
is not available in this Pilot.

## Secondary path: Python

```python
from pathlib import Path

from skill import NextMoveSkill
from skill.utils import to_dict

resume = Path("examples/data/sample_resume.txt").read_text(encoding="utf-8")
job = Path("examples/data/sample_job_description.txt").read_text(encoding="utf-8")
response = NextMoveSkill().run(
    "career_analysis",
    {"resume": resume, "job_description": job},
)
print(to_dict(response))
```

Both secondary paths preserve the same Skill contract and require no hosted
NextMove service.
