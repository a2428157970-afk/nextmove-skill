# NextMove Skill Adoption Pilot Guidelines

## Purpose

This Pilot tests whether a non-technical job seeker can use NextMove through an
Agent, complete a career analysis, understand the report, and identify at least
one useful next action. It is not a test of how much infrastructure NextMove can
build.

## Recommended path

1. Follow [Try NextMove in 5 Minutes](quick-start.md).
2. Begin with the public fictional sample.
3. Use a copyable [Agent Prompt](agent-prompt-template.md).
4. Read the result with the [Output Guide](output-guide.md).
5. Submit the short [anonymous feedback template](pilot-feedback-template.md).

CLI and Python API paths are available for developers and advanced users. The
GitHub Pilot Issue is a secondary technical-feedback channel.

## Truthful input and output

Use only information you are permitted to share. NextMove and the Agent must not
invent experience, skills, education, projects, certifications, achievements,
employers, credentials, or metrics. Suggestions must remain distinguishable
from facts. Information gaps should be reported, not silently filled.

## Feedback data boundary

Feedback may include:

- Agent or invocation path;
- scenario category;
- whether the analysis completed;
- approximate completion time;
- most valuable report section;
- understanding rating;
- general error category;
- privacy-safe improvement suggestion.

Feedback must not include:

- resume or job-description bodies;
- real name, phone number, email, address, or account identifier;
- employer or company-confidential information;
- API keys, tokens, cookies, passwords, or credentials;
- raw Agent conversations containing private career information.

There is no hidden telemetry, analytics service, database, or automatic content
collection. Metrics use only voluntarily submitted, privacy-reviewed feedback.

## First-stage targets

| Metric | Target |
|---|---:|
| First-use completion | >= 80% |
| Report understanding | >= 80% |
| Recommendation actionability | >= 70% |
| Severe factual errors | 0 |
| Feedback completion | >= 30% |

Always report the participant count with these rates. Small Pilot samples are
directional evidence, not statistical proof.

## What happens after the Pilot

Review 5-10 privacy-safe feedback records before deciding whether to add
`--job-description-file`, a human-readable CLI summary, or any Skill behavior.
Do not treat a single preference as proof of a general product need.
