from unittest.mock import MagicMock

import pytest
from requests import Session

from garth.http import Client
from garth.telemetry import (
    REDACTED,
    Telemetry,
    _scrubbing_callback,
    sanitize,
    sanitize_cookie,
    sanitize_headers,
)


def test_sanitize_password():
    text = '{"password": "secret123", "username": "user"}'
    result = sanitize(text)
    assert "secret123" not in result
    assert '"password": "[REDACTED]"' in result
    assert "username" in result


def test_sanitize_tokens():
    text = '{"access_token": "abc123", "refresh_token": "xyz789"}'
    result = sanitize(text)
    assert "abc123" not in result
    assert "xyz789" not in result
    assert result.count("[REDACTED]") == 2


def test_sanitize_oauth_tokens():
    text = '{"oauth_token": "token1", "oauth_token_secret": "secret1"}'
    result = sanitize(text)
    assert "token1" not in result
    assert "secret1" not in result


def test_sanitize_query_params():
    text = "password=mysecret&username=user"
    result = sanitize(text)
    assert "mysecret" not in result
    assert "password=[REDACTED]" in result


def test_telemetry_defaults():
    t = Telemetry()
    assert t.service_name == "garth"
    assert t.enabled is False
    assert t.send_to_logfire is True
    assert t.token is None
    assert t.callback is None
    assert t._configured is False


def test_telemetry_configure_disabled(monkeypatch):
    monkeypatch.delenv("GARTH_TELEMETRY", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_SERVICE_NAME", raising=False)
    monkeypatch.delenv("LOGFIRE_SEND_TO_LOGFIRE", raising=False)

    t = Telemetry()
    t.configure(service_name="my-app")
    assert t.service_name == "my-app"
    assert t.enabled is False
    assert t._configured is False  # Not configured because disabled


@pytest.mark.vcr
def test_telemetry_enabled_request(authed_client: Client, monkeypatch):
    """Test that telemetry works with real API requests (VCR recorded)."""
    captured_data = []

    def capture_callback(data):
        captured_data.append(data)

    # Configure telemetry with custom callback to capture data
    authed_client.configure(
        telemetry_enabled=True,
        telemetry_callback=capture_callback,
    )

    assert authed_client.telemetry.enabled is True
    assert authed_client.telemetry._configured is True

    # Make a real API request - this will be recorded by VCR
    profile = authed_client.connectapi("/userprofile-service/socialProfile")
    assert profile is not None
    assert "displayName" in profile

    # Verify telemetry was captured
    assert len(captured_data) == 1
    assert captured_data[0]["method"] == "GET"
    assert "userprofile-service" in captured_data[0]["url"]
    assert captured_data[0]["status_code"] == 200


def test_telemetry_env_override_disabled(monkeypatch):
    monkeypatch.setenv("GARTH_TELEMETRY", "false")

    t = Telemetry()
    t.configure(enabled=True)  # Try to enable via code
    assert t.enabled is False  # Env var wins


def test_telemetry_env_service_name(monkeypatch):
    monkeypatch.setenv("GARTH_TELEMETRY_SERVICE_NAME", "custom-service")
    monkeypatch.delenv("GARTH_TELEMETRY", raising=False)

    t = Telemetry()
    t.configure()
    assert t.service_name == "custom-service"


def test_telemetry_env_send_to_logfire_false(monkeypatch):
    monkeypatch.setenv("LOGFIRE_SEND_TO_LOGFIRE", "false")
    monkeypatch.delenv("GARTH_TELEMETRY", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_SERVICE_NAME", raising=False)

    t = Telemetry()
    t.configure()
    assert t.send_to_logfire is False


def test_telemetry_configure_all_params():
    t = Telemetry()
    callback = lambda data: None  # noqa: E731
    t.configure(
        service_name="test-service",
        enabled=False,
        send_to_logfire=False,
        token="test-token",
        callback=callback,
    )
    assert t.service_name == "test-service"
    assert t.enabled is False
    assert t.send_to_logfire is False
    assert t.token == "test-token"
    assert t.callback is callback


def test_telemetry_only_configures_once(monkeypatch):
    monkeypatch.delenv("GARTH_TELEMETRY", raising=False)
    monkeypatch.delenv("LOGFIRE_TOKEN", raising=False)

    t = Telemetry()
    t._configured = True  # Pretend already configured

    # Even if enabled, should not reconfigure
    t.configure(enabled=True)
    # _configured should still be True (not reconfigured)
    assert t._configured is True


def test_sanitize_cookie():
    cookie = "session=abc123; path=/; domain=example.com"
    result = sanitize_cookie(cookie)
    assert "abc123" not in result
    assert f"session={REDACTED}" in result


def test_sanitize_headers():
    headers = {
        "Authorization": "Bearer token123",
        "Cookie": "session=abc",
        "Content-Type": "application/json",
    }
    result = sanitize_headers(headers)
    assert result["Authorization"] == REDACTED
    assert result["Cookie"] == REDACTED
    assert result["Content-Type"] == "application/json"


def test_sanitize_headers_case_insensitive():
    headers = {"authorization": "Bearer token123", "cookie": "session=abc"}
    result = sanitize_headers(headers)
    assert result["authorization"] == REDACTED
    assert result["cookie"] == REDACTED


def test_response_hook_with_string_body():
    """Test session response hook captures and sanitizes data."""
    captured_data = []
    t = Telemetry()
    t.enabled = True
    t.callback = lambda data: captured_data.append(data)

    # Create mock response with request
    response = MagicMock()
    response.request = MagicMock()
    response.request.method = "POST"
    response.request.url = "https://example.com/api"
    response.request.headers = {"Content-Type": "application/json"}
    response.request.body = '{"password": "secret"}'
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"access_token": "token123"}'

    t._response_hook(response)

    assert len(captured_data) == 1
    data = captured_data[0]
    assert data["method"] == "POST"
    assert data["url"] == "https://example.com/api"
    assert data["status_code"] == 200
    assert "secret" not in data["request_body"]
    assert "token123" not in data["response_body"]


def test_response_hook_with_bytes_body():
    """Test session response hook handles bytes body."""
    captured_data = []
    t = Telemetry()
    t.enabled = True
    t.callback = lambda data: captured_data.append(data)

    response = MagicMock()
    response.request = MagicMock()
    response.request.method = "POST"
    response.request.url = "https://example.com/api"
    response.request.headers = {"Content-Type": "application/json"}
    response.request.body = b'{"password": "secret"}'
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"data": "ok"}'

    t._response_hook(response)

    assert len(captured_data) == 1
    assert "secret" not in captured_data[0]["request_body"]


def test_response_hook_no_body():
    """Test session response hook handles missing request body."""
    captured_data = []
    t = Telemetry()
    t.enabled = True
    t.callback = lambda data: captured_data.append(data)

    response = MagicMock()
    response.request = MagicMock()
    response.request.method = "GET"
    response.request.url = "https://example.com/api"
    response.request.headers = {"Content-Type": "application/json"}
    response.request.body = None
    response.status_code = 200
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"data": "ok"}'

    t._response_hook(response)

    assert len(captured_data) == 1
    assert "request_body" not in captured_data[0]


def test_response_hook_disabled():
    """Test session response hook does nothing when disabled."""
    captured_data = []
    t = Telemetry()
    t.enabled = False
    t.callback = lambda data: captured_data.append(data)

    response = MagicMock()
    t._response_hook(response)

    assert len(captured_data) == 0


def test_response_hook_handles_exceptions():
    """Test session response hook handles exceptions gracefully."""
    t = Telemetry()
    t.enabled = True
    t.callback = lambda data: 1 / 0  # Will raise ZeroDivisionError

    response = MagicMock()
    response.request = MagicMock()
    response.request.method = "GET"
    response.request.url = "https://example.com/api"
    response.request.headers = {}
    response.request.body = None
    response.status_code = 200
    response.headers = {}
    response.text = "{}"

    # Should not raise, just silently handle exceptions
    t._response_hook(response)


def test_scrubbing_callback_bypasses_logfire_scrubbing():
    """Scrubbing callback should return value as-is since we pre-sanitize."""
    m = MagicMock()
    m.value = "test body"

    result = _scrubbing_callback(m)
    assert result == "test body"


def test_telemetry_env_enabled_with_mock(monkeypatch):
    """Test GARTH_TELEMETRY=true enables telemetry."""
    import sys

    monkeypatch.setenv("GARTH_TELEMETRY", "true")
    monkeypatch.setenv("LOGFIRE_TOKEN", "test-token")
    monkeypatch.delenv("GARTH_TELEMETRY_SERVICE_NAME", raising=False)
    monkeypatch.delenv("LOGFIRE_SEND_TO_LOGFIRE", raising=False)

    mock_logfire = MagicMock()
    monkeypatch.setitem(sys.modules, "logfire", mock_logfire)

    t = Telemetry()
    t.configure()

    assert t.enabled is True
    assert t._configured is True
    assert t._logfire_configured is True
    mock_logfire.configure.assert_called_once()


def test_telemetry_sets_token_env_var(monkeypatch):
    """Test that token parameter sets LOGFIRE_TOKEN env var."""
    import sys

    monkeypatch.setenv("GARTH_TELEMETRY", "true")
    monkeypatch.delenv("LOGFIRE_TOKEN", raising=False)

    mock_logfire = MagicMock()
    monkeypatch.setitem(sys.modules, "logfire", mock_logfire)

    t = Telemetry()
    t.configure(token="my-test-token")

    assert t.token == "my-test-token"
    assert t._configured is True


def test_telemetry_attach_to_session():
    """Test attaching telemetry hooks to a session."""
    t = Telemetry()
    t.enabled = True

    session = Session()
    initial_hook_count = len(session.hooks["response"])

    t.attach(session)

    assert len(session.hooks["response"]) == initial_hook_count + 1
    assert t._response_hook in session.hooks["response"]


def test_telemetry_attach_idempotent():
    """Test attaching to the same session multiple times adds only one hook."""
    t = Telemetry()
    t.enabled = True

    session = Session()
    initial_hook_count = len(session.hooks["response"])

    t.attach(session)
    t.attach(session)
    t.attach(session)

    assert len(session.hooks["response"]) == initial_hook_count + 1


def test_telemetry_custom_callback_skips_logfire(monkeypatch):
    """Test that providing a custom callback skips logfire configuration."""
    import sys

    monkeypatch.setenv("GARTH_TELEMETRY", "true")
    monkeypatch.setenv("LOGFIRE_TOKEN", "test-token")

    mock_logfire = MagicMock()
    monkeypatch.setitem(sys.modules, "logfire", mock_logfire)

    t = Telemetry()
    t.configure(callback=lambda data: None)

    assert t.enabled is True
    assert t._configured is True
    assert t._logfire_configured is False
    mock_logfire.configure.assert_not_called()


def test_telemetry_no_token_skips_logfire_config(monkeypatch):
    """Test that missing token skips logfire configuration."""
    import sys

    monkeypatch.setenv("GARTH_TELEMETRY", "true")
    monkeypatch.delenv("LOGFIRE_TOKEN", raising=False)

    mock_logfire = MagicMock()
    monkeypatch.setitem(sys.modules, "logfire", mock_logfire)

    t = Telemetry()
    t.configure()  # No token provided

    assert t.enabled is True
    assert t._configured is True
    assert t._logfire_configured is False
    mock_logfire.configure.assert_not_called()


def test_client_telemetry_callback(monkeypatch):
    """Test that client properly passes telemetry callback."""
    monkeypatch.delenv("GARTH_HOME", raising=False)
    monkeypatch.delenv("GARTH_TOKEN", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY", raising=False)

    captured_data = []
    client = Client()
    client.configure(
        telemetry_enabled=True,
        telemetry_callback=lambda data: captured_data.append(data),
    )

    assert client.telemetry.enabled is True
    assert client.telemetry.callback is not None


def test_default_callback_calls_logfire(monkeypatch):
    """Test that _default_callback calls logfire.info."""
    import sys

    mock_logfire = MagicMock()
    monkeypatch.setitem(sys.modules, "logfire", mock_logfire)

    t = Telemetry()
    data = {
        "method": "GET",
        "url": "https://example.com/api",
        "status_code": 200,
    }

    t._default_callback(data)

    mock_logfire.info.assert_called_once_with(
        "http {method} {url} {status_code}", **data
    )
