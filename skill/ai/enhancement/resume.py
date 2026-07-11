"""Optional AI enhancement for deterministic resume improvement output."""

import json

from skill.ai.enhancement.service import EnhancementService
from skill.ai.enhancement.resume_output import parse_resume_ai_output
from skill.ai.prompts.contracts import PromptTemplate
from skill.ai.prompts.resume import ResumeImprovementPrompt
from skill.ai.providers.base import AIProvider
from skill.ai.schemas import AIEnhancementResult
from skill.improvement.schemas import ResumeImprovementResult


class ResumeAIEnhancer:
    """Enhance a ResumeImprovementResult without changing Skill Core behavior."""

    def __init__(
        self,
        provider: AIProvider,
        prompt_template: PromptTemplate | None = None,
    ):
        self.service = EnhancementService(provider=provider)
        self.prompt_template = prompt_template or ResumeImprovementPrompt()

    def enhance(self, result: ResumeImprovementResult) -> AIEnhancementResult:
        """Pass structured resume improvement output through the AI layer."""
        context = {
            "issues": result.issues,
            "suggestions": result.suggestions,
            "improved_sections": result.improved_sections,
        }
        prompt = self.prompt_template.render(context)
        response = self.service.enhance(prompt, context)
        if not response.success:
            return response
        parsed = parse_resume_ai_output(response.enhanced_content or "")
        if parsed is None:
            return AIEnhancementResult(success=False, error="AI provider response error")
        return AIEnhancementResult(success=True, enhanced_content=json.dumps(parsed.to_dict(), sort_keys=True))
