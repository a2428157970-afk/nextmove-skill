"""Example: analyze a resume through NextMoveSkill.run()."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill import NextMoveSkill
from skill.utils import to_dict


resume_text = """
Jane Doe
jane@example.com

Summary
Backend engineer focused on Python services and internal tooling.

Experience
Backend Engineer
Built Python APIs for internal career tools.

Skills
Python, FastAPI, SQL, Docker, Testing
"""


skill = NextMoveSkill()
response = skill.run("analyze_resume", {"resume": resume_text})

print(json.dumps(to_dict(response), indent=2))
