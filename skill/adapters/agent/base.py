"""Provider-neutral Agent adapter boundary."""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any

from skill.agent import AgentTool


class BaseAgentAdapter(ABC):
    """Base interface for converting AgentTool metadata into agent schemas."""

    @abstractmethod
    def export_tools(self, tools: list[AgentTool]) -> list[dict[str, Any]]:
        """Convert AgentTool definitions into an adapter-specific schema."""


class GenericAgentAdapter(BaseAgentAdapter):
    """Default adapter that preserves the provider-neutral AgentTool shape."""

    def export_tools(self, tools: list[AgentTool]) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": deepcopy(tool.input_schema),
                "output_schema": deepcopy(tool.output_schema),
            }
            for tool in tools
        ]
