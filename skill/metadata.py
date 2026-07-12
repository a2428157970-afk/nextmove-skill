"""Metadata for Agent discovery of the NextMove Skill."""

from skill.__version__ import __version__

SKILL_METADATA = {
    "name": "NextMove",
    "version": __version__,
    "capabilities": [
        "analyze_resume",
        "improve_resume",
        "match_job",
        "career_advice",
        "career_analysis",
    ],
    "description": (
        "AI Career Intelligence Skill for resume analysis, resume improvement, "
        "job matching, and career advice with provider-neutral structured output."
    ),
}


__all__ = ["SKILL_METADATA"]
