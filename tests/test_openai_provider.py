"""Unit tests for the injected-transport OpenAI-compatible adapter."""

import unittest

from skill.ai import (
    AIProviderSettings,
    OpenAICompatibleProvider,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


class MockTransport:
    """Captures a request and returns a configured response or error."""

    def __init__(self, response: dict | None = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.request: dict | None = None

    def post(
        self,
        path: str,
        headers: dict[str, str],
        body: dict,
        timeout: float | None,
    ) -> dict:
        self.request = {
            "path": path,
            "headers": headers,
            "body": body,
            "timeout": timeout,
        }
        if self.error is not None:
            raise self.error
        return self.response or {}


class OpenAICompatibleProviderTests(unittest.TestCase):
    def setUp(self):
        self.settings = AIProviderSettings(
            provider_name="openai-compatible",
            model_name="test-model",
            timeout=3.0,
        )

    def test_maps_request_and_parses_chat_completion_response(self):
        transport = MockTransport(
            response={"choices": [{"message": {"content": "Enhanced text"}}]}
        )
        provider = OpenAICompatibleProvider(
            settings=self.settings,
            credentials="test-credential",
            transport=transport,
        )

        content = provider.generate("Improve this resume", {"issue": "summary"})

        self.assertEqual(content, "Enhanced text")
        self.assertEqual(transport.request["path"], "/v1/chat/completions")
        self.assertEqual(transport.request["headers"]["Authorization"], "Bearer test-credential")
        self.assertEqual(transport.request["body"]["model"], "test-model")
        self.assertEqual(transport.request["body"]["messages"][0]["content"], "Improve this resume")
        self.assertEqual(transport.request["timeout"], 3.0)

    def test_maps_transport_timeout_to_provider_timeout_error(self):
        provider = OpenAICompatibleProvider(
            self.settings,
            "test-credential",
            MockTransport(error=TimeoutError()),
        )

        with self.assertRaises(ProviderTimeoutError):
            provider.generate("Improve", {})

    def test_maps_transport_failure_to_provider_unavailable_error(self):
        provider = OpenAICompatibleProvider(
            self.settings,
            "test-credential",
            MockTransport(error=OSError("connection failed")),
        )

        with self.assertRaises(ProviderUnavailableError):
            provider.generate("Improve", {})

    def test_maps_invalid_response_to_provider_response_error(self):
        provider = OpenAICompatibleProvider(
            self.settings,
            "test-credential",
            MockTransport(response={"choices": []}),
        )

        with self.assertRaises(ProviderResponseError):
            provider.generate("Improve", {})


if __name__ == "__main__":
    unittest.main()
