"""OpenAI-compatible Chat Completions adapter without an SDK dependency."""

import json

from skill.ai.configuration.settings import AIProviderSettings
from skill.ai.errors import (
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from skill.ai.providers.adapters.base import BaseProviderAdapter
from skill.ai.providers.openai.transport import HTTPTransport


class OpenAICompatibleProvider(BaseProviderAdapter):
    """Map the generic provider contract to an injected HTTP transport request."""

    def __init__(
        self,
        settings: AIProviderSettings,
        credentials: object,
        transport: HTTPTransport,
    ):
        super().__init__(settings)
        self._credentials = credentials
        self._transport = transport

    def generate(self, prompt: str, context: dict) -> str:
        """Generate content through an OpenAI-compatible chat-completions API."""
        body = {
            "model": self.settings.model_name,
            "messages": [
                {"role": "user", "content": prompt},
                {
                    "role": "user",
                    "content": json.dumps(context, default=str, sort_keys=True),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._credentials}",
            "Content-Type": "application/json",
        }

        try:
            response = self._transport.post(
                "/v1/chat/completions",
                headers,
                body,
                self.settings.timeout,
            )
        except (
            ProviderResponseError,
            ProviderTimeoutError,
            ProviderUnavailableError,
        ):
            raise
        except TimeoutError as exc:
            raise ProviderTimeoutError() from exc
        except OSError as exc:
            raise ProviderUnavailableError() from exc
        except Exception as exc:
            raise ProviderUnavailableError() from exc

        try:
            content = response["choices"][0]["message"]["content"]
        except (IndexError, KeyError, TypeError) as exc:
            raise ProviderResponseError() from exc

        if not isinstance(content, str) or not content.strip():
            raise ProviderResponseError()
        return content
