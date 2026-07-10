"""NextMove Skill Core package."""

from skill.__version__ import __version__
from skill.interface import NextMoveSkill
from skill.schemas.api import SkillError, SkillResponse

__all__ = ["NextMoveSkill", "SkillError", "SkillResponse", "__version__"]
