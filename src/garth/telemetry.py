import os
import re
from dataclasses import dataclass, field


SENSITIVE_PATTERNS = [
    r'"password"\s*:\s*"[^"]*"',
    r'"refresh_token"\s*:\s*"[^"]*"',
    r'"access_token"\s*:\s*"[^"]*"',
    r'"oauth_token"\s*:\s*"[^"]*"',
    r'"oauth_token_secret"\s*:\s*"[^"]*"',
    r"password=[^&\s]*",
    r"embed=[^&\s]*",
]


def _sanitize(text: str) -> str:
    """Redact sensitive data from request/response bodies."""
    for pattern in SENSITIVE_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)
    return text


def _response_hook(span, request, response):
    """Log sanitized response body on failures for debugging."""
    if response.status_code >= 400:
        try:
            body = response.text[:1000]
            span.set_attribute("http.response.body.sanitized", _sanitize(body))
        except Exception:
            pass


@dataclass
class Telemetry:
    service_name: str = "garth"
    enabled: bool = False
    send_to_logfire: bool = True
    token: str | None = None
    _configured: bool = field(default=False, repr=False)

    def configure(
        self,
        service_name: str | None = None,
        enabled: bool | None = None,
        send_to_logfire: bool | None = None,
        token: str | None = None,
    ):
        """
        Configure telemetry. Disabled by default.

        Args:
            service_name: Service name for traces (default: "garth")
            enabled: Enable/disable telemetry (default: False)
            send_to_logfire: Send to Logfire Cloud (default: True)
            token: Logfire write token (or use LOGFIRE_TOKEN env var)
        """
        if service_name is not None:
            self.service_name = service_name
        if enabled is not None:
            self.enabled = enabled
        if send_to_logfire is not None:
            self.send_to_logfire = send_to_logfire
        if token is not None:
            self.token = token

        # Check env var overrides
        env_enabled = os.getenv("GARTH_TELEMETRY", "").lower()
        if env_enabled == "true":
            self.enabled = True
        elif env_enabled == "false":
            self.enabled = False

        env_service_name = os.getenv("GARTH_TELEMETRY_SERVICE_NAME")
        if env_service_name:
            self.service_name = env_service_name
        if os.getenv("LOGFIRE_SEND_TO_LOGFIRE", "").lower() == "false":
            self.send_to_logfire = False

        if not self.enabled or self._configured:
            return

        # Set token if provided
        if self.token:
            os.environ["LOGFIRE_TOKEN"] = self.token

        import logfire

        logfire.configure(
            service_name=self.service_name,
            send_to_logfire=self.send_to_logfire,
        )
        logfire.instrument_requests(response_hook=_response_hook)
        self._configured = True
