"""Tests for safe application observation and operational limits."""

import unittest

from skill.ai import (
    AIApplicationLimits,
    AIEnhancementResult,
    AIExecutionObserver,
    AIRequestContext,
    ApplicationEnhancementService,
)


class RecordingEnhancementService:
    def __init__(self):
        self.calls: list[tuple] = []

    def enhance(self, prompt, context, request_context=None):
        self.calls.append((prompt, context, request_context))
        return AIEnhancementResult(success=True, enhanced_content="enhanced")


class AIApplicationOperationsTests(unittest.TestCase):
    def setUp(self):
        self.request_context = AIRequestContext(
            provider_name="mock",
            model_name="mock-model",
            capability="resume_improvement",
            request_id="request-123",
        )

    def test_observer_creates_safe_success_metadata(self):
        observer = AIExecutionObserver()
        result = AIEnhancementResult(success=True, enhanced_content="private output")

        metadata = observer.observe(
            self.request_context,
            started_at=10.0,
            ended_at=10.25,
            result=result,
        )

        self.assertEqual(metadata.request_id, "request-123")
        self.assertEqual(metadata.provider_name, "mock")
        self.assertEqual(metadata.model_name, "mock-model")
        self.assertEqual(metadata.latency, 0.25)
        self.assertEqual(metadata.status, "success")
        self.assertEqual(
            set(metadata.__slots__),
            {"request_id", "provider_name", "model_name", "latency", "status"},
        )

    def test_observer_marks_structured_failure_without_copying_error_content(self):
        observer = AIExecutionObserver()
        result = AIEnhancementResult(success=False, error="sensitive detail")

        metadata = observer.observe(self.request_context, 5.0, 4.0, result)

        self.assertEqual(metadata.latency, 0.0)
        self.assertEqual(metadata.status, "failure")
        self.assertFalse(hasattr(metadata, "error"))
        self.assertFalse(hasattr(metadata, "prompt"))
        self.assertFalse(hasattr(metadata, "context"))

    def test_limits_reject_prompt_without_mutating_or_delegating(self):
        delegate = RecordingEnhancementService()
        limits = AIApplicationLimits(max_prompt_characters=4, max_context_items=None)
        service = ApplicationEnhancementService(delegate, limits)
        prompt = "12345"
        context = {"unchanged": ["value"]}

        result = service.enhance(prompt, context, self.request_context)

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI application limit exceeded")
        self.assertEqual(delegate.calls, [])
        self.assertEqual(prompt, "12345")
        self.assertEqual(context, {"unchanged": ["value"]})

    def test_limits_reject_context_item_count_without_delegating(self):
        delegate = RecordingEnhancementService()
        service = ApplicationEnhancementService(
            delegate,
            AIApplicationLimits(max_prompt_characters=None, max_context_items=1),
        )

        result = service.enhance("prompt", {"one": 1, "two": 2})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI application limit exceeded")
        self.assertEqual(delegate.calls, [])

    def test_limits_reject_live_request_unless_explicitly_allowed(self):
        delegate = RecordingEnhancementService()
        service = ApplicationEnhancementService(
            delegate,
            AIApplicationLimits(
                max_prompt_characters=None,
                max_context_items=None,
                allow_live_requests=False,
            ),
            live_request=True,
        )

        result = service.enhance("prompt", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error, "AI provider unavailable")
        self.assertEqual(delegate.calls, [])

    def test_valid_request_is_delegated_with_original_objects(self):
        delegate = RecordingEnhancementService()
        service = ApplicationEnhancementService(
            delegate,
            AIApplicationLimits(
                max_prompt_characters=100,
                max_context_items=10,
                allow_live_requests=True,
            ),
            live_request=True,
        )
        prompt = "prompt"
        context = {"item": "value"}

        result = service.enhance(prompt, context, self.request_context)

        self.assertTrue(result.success)
        self.assertEqual(len(delegate.calls), 1)
        self.assertIs(delegate.calls[0][0], prompt)
        self.assertIs(delegate.calls[0][1], context)
        self.assertIs(delegate.calls[0][2], self.request_context)


if __name__ == "__main__":
    unittest.main()
