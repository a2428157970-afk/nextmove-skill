"""Safe execution observation without business or credential content."""

from skill.ai.context import AIRequestContext
from skill.ai.metadata import AIExecutionMetadata
from skill.ai.schemas import AIEnhancementResult


class AIExecutionObserver:
    """Create non-sensitive metadata from request identity, timing, and outcome."""

    def observe(
        self,
        request_context: AIRequestContext,
        started_at: float,
        ended_at: float,
        result: AIEnhancementResult,
    ) -> AIExecutionMetadata:
        """Return safe metadata with latency measured in seconds."""
        return AIExecutionMetadata(
            request_id=request_context.request_id,
            provider_name=request_context.provider_name,
            model_name=request_context.model_name,
            latency=max(0.0, ended_at - started_at),
            status="success" if result.success else "failure",
        )
