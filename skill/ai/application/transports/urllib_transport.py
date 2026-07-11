"""Standard-library HTTP transport for application-owned provider traffic."""

import json
import socket
from collections.abc import Callable
from urllib.error import URLError
from urllib.request import Request, urlopen

from skill.ai.errors import (
    ProviderResponseError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


class UrllibHTTPTransport:
    """POST JSON through urllib without owning credentials or configuration."""

    def __init__(
        self,
        base_url: str,
        opener: Callable[..., object] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self._opener = opener or urlopen

    def post(
        self,
        path: str,
        headers: dict[str, str],
        body: dict,
        timeout: float | None,
    ) -> dict:
        """POST a JSON object and return a decoded JSON object."""
        request_headers = {"Content-Type": "application/json", **headers}
        request = Request(
            url=f"{self.base_url}/{path.lstrip('/')}",
            data=json.dumps(body).encode("utf-8"),
            headers=request_headers,
            method="POST",
        )

        try:
            if timeout is None:
                response = self._opener(request)
            else:
                response = self._opener(request, timeout=timeout)
            with response:
                payload = response.read()
        except (TimeoutError, socket.timeout) as exc:
            raise ProviderTimeoutError() from exc
        except URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise ProviderTimeoutError() from exc
            raise ProviderUnavailableError() from exc
        except OSError as exc:
            raise ProviderUnavailableError() from exc

        try:
            decoded = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderResponseError() from exc
        if not isinstance(decoded, dict):
            raise ProviderResponseError()
        return decoded
