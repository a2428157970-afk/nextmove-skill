"""Run the complete NextMove career intelligence workflow."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skill import NextMoveSkill
from skill.utils import to_dict


def run_full_career_analysis(resume_text: str, job_description: str) -> dict:
    """Return a JSON-serializable report for the four Career Intelligence capabilities."""
    skill = NextMoveSkill()

    analysis = skill.run("analyze_resume", {"resume": resume_text})
    improvement = skill.run("improve_resume", {"resume": resume_text})
    job_match = skill.run(
        "match_job",
        {"resume": resume_text, "job_description": job_description},
    )
    career_advice = skill.run(
        "career_advice",
        {"resume": resume_text, "analysis": analysis.result},
    )

    return {
        "analysis": to_dict(analysis),
        "improvement": to_dict(improvement),
        "job_match": to_dict(job_match),
        "career_advice": to_dict(career_advice),
    }


if __name__ == "__main__":
    report = run_full_career_analysis(
        """
        Jane Doe

        Summary
        Backend engineer focused on Python APIs and internal tooling.

        Experience
        Backend Engineer
        Built Python APIs with FastAPI and SQL.

        Skills
        Python, FastAPI, SQL, Testing
        """,
        "Backend role requiring Python, FastAPI, SQL, Docker, and API testing.",
    )
    print(json.dumps(report, indent=2))
