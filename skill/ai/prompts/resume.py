"""Prompt template for optional resume improvement enhancement."""

import json
from dataclasses import dataclass

from skill.ai.prompts.contracts import PromptTemplate


@dataclass(slots=True)
class ResumeImprovementPrompt(PromptTemplate):
    """Render an AI-layer prompt from deterministic improvement output."""

    name: str = "resume_improvement_enhancement"

    def render(self, context: dict) -> str:
        """Render structured resume improvement context without Core coupling."""
        structured_result = json.dumps(context, default=str, sort_keys=True)
        return (
            "Provide clear and practical resume improvement guidance based on "
            f"this structured resume improvement result: {structured_result}"
        )
