"""Example: match a resume against a job description through NextMoveSkill.run()."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill import NextMoveSkill
from skill.utils import to_dict


resume_text = """
Jane Doe

Summary
Backend engineer focused on Python APIs.

Experience
Backend Engineer
Built Python APIs with FastAPI and SQL.

Skills
Python, FastAPI, SQL, Testing
"""

job_description = """
Backend role requiring Python, FastAPI, SQL, Docker, and API testing.
"""


skill = NextMoveSkill()
response = skill.run(
    "match_job",
    {
        "resume": resume_text,
        "job_description": job_description,
    },
)

print(json.dumps(to_dict(response), indent=2))
