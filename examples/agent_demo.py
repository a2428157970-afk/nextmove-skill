"""Example: invoke NextMove capabilities through AgentRuntime."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill.agent import AgentRuntime
from skill.utils import to_dict


resume_text = """
Jane Doe

Summary
Backend engineer focused on Python APIs.

Experience
Backend Engineer
Built Python APIs with FastAPI and SQL.

Skills
Python, FastAPI, SQL, Docker, Testing
"""

job_description = """
Backend role requiring Python, FastAPI, SQL, Docker, and API testing.
"""


runtime = AgentRuntime()

analyze_response = runtime.invoke("analyze_resume", {"resume": resume_text})
match_response = runtime.invoke(
    "match_job",
    {
        "resume": resume_text,
        "job_description": job_description,
    },
)

print("analyze_resume")
print(json.dumps(to_dict(analyze_response), indent=2))
print("\\nmatch_job")
print(json.dumps(to_dict(match_response), indent=2))
