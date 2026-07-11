"""Application-level pre-call validation for AI enhancement."""

from skill.ai.application.limits import AIApplicationLimits
from skill.ai.context import AIRequestContext
from skill.ai.enhancement.service import EnhancementService
from skill.ai.schemas import AIEnhancementResult


class ApplicationEnhancementService(EnhancementService):
    """Validate application limits before delegating an enhancement call."""

    def __init__(
        self,
        delegate: EnhancementService,
        limits: AIApplicationLimits,
        live_request: bool = False,
    ):
        self.delegate = delegate
        self.limits = limits
        self.live_request = live_request

    def enhance(
        self,
        prompt: str,
        context: dict,
        request_context: AIRequestContext | None = None,
    ) -> AIEnhancementResult:
        """Reject invalid calls without truncating or modifying their content."""
        rejection = self.limits.validate(prompt, context, self.live_request)
        if rejection is not None:
            return rejection
        return self.delegate.enhance(prompt, context, request_context)
