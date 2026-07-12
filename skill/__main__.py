"""Offline command-line entry point for the NextMove Skill."""

import argparse
import json
from pathlib import Path
from typing import Sequence

from skill.interface import NextMoveSkill
from skill.schemas.api import SkillError, SkillResponse
from skill.utils import to_dict


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nextmove")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser(
        "analyze",
        help="Run the offline career_analysis capability.",
    )
    analyze.add_argument(
        "--resume",
        required=True,
        type=Path,
        help="Path to a UTF-8 plain-text resume file.",
    )
    analyze.add_argument(
        "--job-description",
        default="",
        help="Optional target job description text.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        resume = args.resume.read_text(encoding="utf-8")
        if not resume.strip():
            raise ValueError("resume file must contain text")
    except (OSError, UnicodeError, ValueError) as exc:
        response = SkillResponse(
            success=False,
            capability="career_analysis",
            error=SkillError(code="INVALID_INPUT", message=str(exc)),
        )
        print(json.dumps(to_dict(response), indent=2))
        return 2

    response = NextMoveSkill().run(
        "career_analysis",
        {
            "resume": resume,
            "job_description": args.job_description,
        },
    )
    print(json.dumps(to_dict(response), indent=2))
    return 0 if response.success and response.result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
