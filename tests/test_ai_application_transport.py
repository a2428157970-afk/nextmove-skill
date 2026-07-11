"""Tests for the standard-library application HTTP transport."""

import json
import socket
import unittest
from urllib.error import HTTPError, URLError

from skill.ai import (
    AIProviderSettings,
    OpenAICompatibleProvider,
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    UrllibHTTPTransport,
)


class StubResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self) -> bytes:
        return self.payload


class CapturingOpener:
    def __init__(self, payload: bytes = b"{}", error: Exception | None = None):
        self.payload = payload
        self.error = error
        self.calls: list[dict] = []

    def __call__(self, request, **kwargs):
        self.calls.append({"request": request, "kwargs": kwargs})
        if self.error is not None:
            raise self.error
        return StubResponse(self.payload)


class ErrorTransport:
    def __init__(self, error: Exception):
        self.error = error

    def post(self, path, headers, body, timeout):
        raise self.error


class UrllibHTTPTransportTests(unittest.TestCase):
    def test_constructs_post_json_request_with_headers_and_timeout(self):
        opener = CapturingOpener(b'{"result": "ok"}')
        transport = UrllibHTTPTransport("https://provider.example", opener=opener)

        result = transport.post(
            "/v1/chat/completions",
            {"Authorization": "Bearer test-value", "X-Test": "yes"},
            {"model": "test-model"},
            2.5,
        )

        call = opener.calls[0]
        request = call["request"]
        self.assertEqual(request.full_url, "https://provider.example/v1/chat/completions")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"model": "test-model"})
        self.assertEqual(request.get_header("Authorization"), "Bearer test-value")
        self.assertEqual(request.get_header("X-test"), "yes")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(call["kwargs"], {"timeout": 2.5})
        self.assertEqual(result, {"result": "ok"})

    def test_omits_timeout_argument_when_policy_timeout_is_none(self):
        opener = CapturingOpener()
        transport = UrllibHTTPTransport("https://provider.example", opener=opener)

        transport.post("/test", {}, {}, None)

        self.assertEqual(opener.calls[0]["kwargs"], {})

    def test_same_transport_instance_can_be_reused(self):
        opener = CapturingOpener()
        transport = UrllibHTTPTransport("https://provider.example", opener=opener)

        transport.post("/first", {}, {}, None)
        transport.post("/second", {}, {}, None)

        self.assertEqual(len(opener.calls), 2)

    def test_maps_timeout_to_provider_timeout_error(self):
        transport = UrllibHTTPTransport(
            "https://provider.example",
            opener=CapturingOpener(error=socket.timeout()),
        )

        with self.assertRaises(ProviderTimeoutError):
            transport.post("/test", {}, {}, 1.0)

    def test_maps_url_and_http_errors_to_provider_unavailable(self):
        errors = [
            URLError("connection failed"),
            HTTPError("https://provider.example", 503, "unavailable", None, None),
            OSError("connection failed"),
        ]

        for error in errors:
            with self.subTest(error=type(error).__name__):
                transport = UrllibHTTPTransport(
                    "https://provider.example",
                    opener=CapturingOpener(error=error),
                )
                with self.assertRaises(ProviderUnavailableError):
                    transport.post("/test", {}, {}, 1.0)

    def test_maps_invalid_or_non_object_json_to_provider_response_error(self):
        for payload in (b"not-json", b"[]"):
            with self.subTest(payload=payload):
                transport = UrllibHTTPTransport(
                    "https://provider.example",
                    opener=CapturingOpener(payload),
                )
                with self.assertRaises(ProviderResponseError):
                    transport.post("/test", {}, {}, None)

    def test_provider_preserves_transport_provider_error_contract(self):
        settings = AIProviderSettings("openai-compatible", "test-model")
        errors = [
            ProviderTimeoutError(),
            ProviderUnavailableError(),
            ProviderResponseError(),
        ]

        for error in errors:
            with self.subTest(error=type(error).__name__):
                provider = OpenAICompatibleProvider(
                    settings,
                    "test-credential",
                    ErrorTransport(error),
                )
                with self.assertRaises(type(error)):
                    provider.generate("Improve", {})


if __name__ == "__main__":
    unittest.main()
