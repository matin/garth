import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field

from requests import Response, Session


REDACTED = "[REDACTED]"

_SENSITIVE_QUERY_PARAMS = [
    "username",
    "password",
    "refresh_token",
    "oauth_token",
    "oauth_token_secret",
    "mfa_token",
    "embed",
]

# Pre-compiled regex patterns for query params (key=value format)
_QUERY_PARAM_PATTERNS = [
    re.compile(rf"{key}=[^&\s]*", re.IGNORECASE)
    for key in _SENSITIVE_QUERY_PARAMS
]
_QUERY_PARAM_REPLACEMENTS = [
    f"{key}={REDACTED}" for key in _SENSITIVE_QUERY_PARAMS
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

# Pre-compiled regex for cookie sanitization
_COOKIE_PATTERN = re.compile(r"=[^;]*")


def sanitize_cookie(cookie_value: str) -> str:
    """Sanitize cookie value by redacting all values."""
    return _COOKIE_PATTERN.sub(f"={REDACTED}", cookie_value)


def sanitize(text: str) -> str:
    """Sanitize sensitive data from request/response text."""
    # Sanitize query params using pre-compiled patterns
    for pattern, replacement in zip(
        _QUERY_PARAM_PATTERNS, _QUERY_PARAM_REPLACEMENTS, strict=True
    ):
        text = pattern.sub(replacement, text)

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


def _scrubbing_callback(m):
    """Bypass logfire scrubbing since we've already sanitized all data."""
    return m.value


@dataclass
class Telemetry:
    service_name: str = "garth"
    enabled: bool = False
    send_to_logfire: bool = True
    token: str | None = None
    callback: Callable[[dict], None] | None = None
    _configured: bool = field(default=False, repr=False)
    _logfire_configured: bool = field(default=False, repr=False)
    _attached_sessions: set = field(default_factory=set, repr=False)

    def _default_callback(self, data: dict):
        """Default callback that sends to logfire."""
        import logfire

        logfire.info("http {method} {url} {status_code}", **data)

    def _response_hook(self, response: Response, *args, **kwargs):
        """Session hook that captures request/response data."""
        if not self.enabled:
            return

        try:
            request = response.request
            data = {
                "method": request.method,
                "url": request.url,
                "status_code": response.status_code,
                "request_headers": str(
                    sanitize_headers(dict(request.headers))
                ),
                "response_headers": str(
                    sanitize_headers(dict(response.headers))
                ),
            }

            if request.body:
                body = request.body
                if isinstance(body, bytes):
                    body = body.decode("utf-8", errors="replace")
                data["request_body"] = sanitize(body)

            data["response_body"] = sanitize(response.text)

            callback = self.callback or self._default_callback
            callback(data)
        except Exception:
            pass  # Don't let telemetry errors break the app

    def configure(
        self,
        service_name: str | None = None,
        enabled: bool | None = None,
        send_to_logfire: bool | None = None,
        token: str | None = None,
        callback: Callable[[dict], None] | None = None,
    ):
        """
        Configure telemetry. Disabled by default.

        Args:
            service_name: Service name for traces (default: "garth")
            enabled: Enable/disable telemetry (default: False)
            send_to_logfire: Send to Logfire Cloud (default: True)
            token: Logfire write token (or use LOGFIRE_TOKEN env var)
            callback: Custom callback for telemetry data. If provided,
                logfire will not be configured and data will be passed
                to this callback instead.
        """
        if service_name is not None:
            self.service_name = service_name
        if enabled is not None:
            self.enabled = enabled
        if send_to_logfire is not None:
            self.send_to_logfire = send_to_logfire
        if token is not None:
            self.token = token
        if callback is not None:
            self.callback = callback

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

        if not self.enabled:
            return

        # Configure logfire only if using default callback and not yet done
        if self.callback is None and not self._logfire_configured:
            self._configure_logfire()

        self._configured = True

    def _configure_logfire(self):
        """Configure logfire for default callback."""
        env_token = os.getenv("LOGFIRE_TOKEN")
        if self.token:
            os.environ["LOGFIRE_TOKEN"] = self.token
        elif not env_token:
            # No token available, can't configure logfire
            return

        import logfire

        logfire.configure(
            service_name=self.service_name,
            send_to_logfire=self.send_to_logfire,
            scrubbing=logfire.ScrubbingOptions(callback=_scrubbing_callback),
            console=False,
        )
        self._logfire_configured = True

    def attach(self, session: Session):
        """Attach telemetry hooks to a session.

        This method is idempotent - calling it multiple times with the same
        session will only attach the hook once.
        """
        session_id = id(session)
        if session_id in self._attached_sessions:
            return

        session.hooks["response"].append(self._response_hook)
        self._attached_sessions.add(session_id)
