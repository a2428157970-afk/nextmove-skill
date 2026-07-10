"""Registry linking Agent Tool metadata to Skill execution capabilities."""

from dataclasses import dataclass

from skill.agent.schemas import AgentTool
from skill.agent.tools import get_agent_tools


class UnknownToolError(KeyError):
    """Raised when a requested Agent Tool is not registered."""


@dataclass(frozen=True, slots=True)
class SkillToolBinding:
    """Binding between Agent Tool metadata and a NextMoveSkill capability."""

    tool: AgentTool
    capability: str


class SkillToolRegistry:
    """Registry for resolving Agent Tool names to Skill capabilities."""

    def __init__(self):
        self._bindings: dict[str, SkillToolBinding] = {}

    def register(self, tool: AgentTool, capability: str | None = None) -> None:
        self._bindings[tool.name] = SkillToolBinding(
            tool=tool,
            capability=capability or tool.name,
        )

    def get(self, name: str) -> SkillToolBinding:
        try:
            return self._bindings[name]
        except KeyError as exc:
            raise UnknownToolError(f"unknown tool: {name}") from exc

    def list_tools(self) -> list[SkillToolBinding]:
        return list(self._bindings.values())


def get_default_tool_registry() -> SkillToolRegistry:
    """Return a registry with the built-in NextMove Agent Tools registered."""

    registry = SkillToolRegistry()
    for tool in get_agent_tools():
        registry.register(tool, capability=tool.name)
    return registry
