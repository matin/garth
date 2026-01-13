import json
import os
import re
from dataclasses import dataclass, field


REDACTED = "[REDACTED]"

# Query param patterns (key=value format)
QUERY_PARAM_PATTERNS = [
    "username",
    "password",
    "refresh_token",
    "oauth_token",
    "oauth_token_secret",
    "mfa_token",
    "embed",
]

# JSON field names to sanitize
JSON_SENSITIVE_FIELDS = [
    "access_token",
    "refresh_token",
    "jti",
    "consumer_key",
    "consumer_secret",
    "password",
    "oauth_token",
    "oauth_token_secret",
]

# Header keys to sanitize
SENSITIVE_HEADERS = ["Authorization", "Cookie", "Set-Cookie"]
SENSITIVE_HEADERS_LOWER = {h.lower() for h in SENSITIVE_HEADERS}


def sanitize_cookie(cookie_value: str) -> str:
    """Sanitize cookie value by redacting all values."""
    return re.sub(r"=[^;]*", f"={REDACTED}", cookie_value)


def sanitize(text: str) -> str:
    """Sanitize sensitive data from request/response text."""
    # Sanitize query params (key=value&...)
    for key in QUERY_PARAM_PATTERNS:
        text = re.sub(
            key + r"=[^&\s]*", f"{key}={REDACTED}", text, flags=re.IGNORECASE
        )

    # Try to sanitize JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            for fld in JSON_SENSITIVE_FIELDS:
                if fld in data:
                    data[fld] = REDACTED
            return json.dumps(data)
    except (json.JSONDecodeError, TypeError):
        pass

    return text


def sanitize_headers(headers: dict) -> dict:
    """Sanitize sensitive headers."""
    sanitized = dict(headers)
    for key in list(sanitized.keys()):
        if key.lower() in SENSITIVE_HEADERS_LOWER:
            sanitized[key] = REDACTED
    return sanitized


def _response_hook(span, request, response):
    """Log sanitized request/response details for debugging."""
    try:
        req_headers = sanitize_headers(dict(request.headers))
        span.set_attribute("http.request.headers", str(req_headers))
    except Exception:
        pass

    try:
        if request.body:
            body = request.body
            if isinstance(body, bytes):
                body = body.decode("utf-8", errors="replace")
            span.set_attribute("http.request.body", sanitize(body))
    except Exception:
        pass

    try:
        resp_headers = sanitize_headers(dict(response.headers))
        span.set_attribute("http.response.headers", str(resp_headers))
    except Exception:
        pass

    try:
        span.set_attribute("http.response.body", sanitize(response.text))
    except Exception:
        pass


def _scrubbing_callback(m):
    """Allow our pre-sanitized attributes through Logfire's scrubbing."""
    if m.path[0] == "attributes" and m.path[1] in (
        "http.request.headers",
        "http.request.body",
        "http.response.headers",
        "http.response.body",
    ):
        return m.value
    return None  # Use default scrubbing


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
            scrubbing=logfire.ScrubbingOptions(callback=_scrubbing_callback),
            console=False,
        )
        logfire.instrument_requests(response_hook=_response_hook)
        self._configured = True
