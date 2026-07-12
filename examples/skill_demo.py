"""Run the installable NextMove Skill product demo without network access."""

import json

from skill import NextMoveSkill
from skill.utils import to_dict


def main() -> None:
    response = NextMoveSkill().run(
        "career_analysis",
        {
            "resume": """
Jane Doe

Summary
Backend engineer focused on Python services and internal tooling.

Experience
Backend Engineer
Built Python APIs and SQL reporting workflows.

Skills
Python, SQL, APIs, Testing
""",
            "job_description": (
                "Backend engineer role requiring Python, SQL, Docker, APIs, "
                "and automated testing."
            ),
        },
    )
    print(json.dumps(to_dict(response), indent=2))


if __name__ == "__main__":
    main()
