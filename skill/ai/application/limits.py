"""Application-owned limits evaluated before an AI enhancement call."""

from dataclasses import dataclass

from skill.ai.schemas import AIEnhancementResult


@dataclass(frozen=True, slots=True)
class AIApplicationLimits:
    """Reject oversized or unauthorized calls without changing their content."""

    max_prompt_characters: int | None = 12_000
    max_context_items: int | None = 100
    allow_live_requests: bool = False

    def validate(
        self,
        prompt: str,
        context: dict,
        live_request: bool = False,
    ) -> AIEnhancementResult | None:
        """Return a structured rejection, or None when the call is allowed."""
        if live_request and not self.allow_live_requests:
            return AIEnhancementResult(success=False, error="AI provider unavailable")
        if (
            self.max_prompt_characters is not None
            and len(prompt) > self.max_prompt_characters
        ):
            return AIEnhancementResult(
                success=False,
                error="AI application limit exceeded",
            )
        if self.max_context_items is not None and len(context) > self.max_context_items:
            return AIEnhancementResult(
                success=False,
                error="AI application limit exceeded",
            )
        return None
