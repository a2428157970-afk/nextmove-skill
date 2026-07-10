"""Provider-neutral Agent Tool metadata schemas."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AgentTool:
    """Description of a callable NextMove capability for agent adapters."""

    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
