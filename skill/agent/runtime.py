"""Runtime entry point for invoking NextMove Agent Tools."""

from skill.agent.registry import SkillToolRegistry, UnknownToolError, get_default_tool_registry
from skill.interface import NextMoveSkill
from skill.schemas.api import SkillError, SkillResponse


class AgentRuntime:
    """Resolve an Agent Tool and execute its matching Skill capability."""

    def __init__(
        self,
        registry: SkillToolRegistry | None = None,
        skill: NextMoveSkill | None = None,
    ):
        self.registry = registry or get_default_tool_registry()
        self.skill = skill or NextMoveSkill()

    def invoke(self, tool_name: str, payload: dict) -> SkillResponse:
        """Invoke a registered Agent Tool with the supplied payload."""
        try:
            binding = self.registry.get(tool_name)
        except UnknownToolError as exc:
            return SkillResponse(
                success=False,
                capability=tool_name,
                result=None,
                error=SkillError(code="UNKNOWN_TOOL", message=str(exc)),
            )

        return self.skill.run(binding.capability, payload)
