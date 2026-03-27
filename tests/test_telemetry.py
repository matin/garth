from unittest.mock import MagicMock

import pytest
from requests import Session

from garth.http import Client
from garth.telemetry import (
    DEFAULT_TOKEN,
    REDACTED,
    Telemetry,
    _scrubbing_callback,
    sanitize,
    sanitize_cookie,
    sanitize_headers,
)
from garth.version import __version__


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


def test_telemetry_defaults(monkeypatch):
    monkeypatch.delenv("GARTH_TELEMETRY_ENABLED", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_TOKEN", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_SEND_TO_LOGFIRE", raising=False)

    t = Telemetry()
    assert t.enabled is False
    assert t.send_to_logfire is False
    assert t.token == DEFAULT_TOKEN
    assert t.callback is None
    assert t.session_id  # non-empty


def test_telemetry_configure_disabled(monkeypatch):
    monkeypatch.delenv("GARTH_TELEMETRY_ENABLED", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_TOKEN", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_SEND_TO_LOGFIRE", raising=False)

    t = Telemetry()
    t.configure(enabled=False)
    assert t.enabled is False


@pytest.mark.vcr
def test_telemetry_enabled_request(authed_client: Client, monkeypatch):
    """Test that telemetry works with real API requests (VCR recorded)."""
    captured_data = []

    def capture_callback(data):
        captured_data.append(data)

    authed_client.configure(
        telemetry_enabled=True,
        telemetry_callback=capture_callback,
    )

    assert authed_client.telemetry.enabled is True

    profile = authed_client.connectapi("/userprofile-service/socialProfile")
    assert profile is not None
    assert "displayName" in profile

    assert len(captured_data) == 1
    assert captured_data[0]["method"] == "GET"
    assert "userprofile-service" in captured_data[0]["url"]
    assert captured_data[0]["status_code"] == 200
    assert "session_id" in captured_data[0]
    assert captured_data[0]["garth_version"] == __version__


def test_telemetry_env_override_disabled(monkeypatch):
    monkeypatch.setenv("GARTH_TELEMETRY_ENABLED", "false")

    t = Telemetry()
    assert t.enabled is False


def test_telemetry_env_send_to_logfire_false(monkeypatch):
    monkeypatch.setenv("GARTH_TELEMETRY_SEND_TO_LOGFIRE", "false")
    monkeypatch.delenv("GARTH_TELEMETRY_ENABLED", raising=False)

    t = Telemetry()
    assert t.send_to_logfire is False


def test_telemetry_configure_all_params(monkeypatch):
    monkeypatch.delenv("GARTH_TELEMETRY_ENABLED", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_TOKEN", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_SEND_TO_LOGFIRE", raising=False)

    t = Telemetry()
    callback = lambda data: None  # noqa: E731
    t.configure(
        enabled=False,
        send_to_logfire=False,
        token="test-token",
        callback=callback,
    )
    assert t.enabled is False
    assert t.send_to_logfire is False
    assert t.token == "test-token"
    assert t.callback is callback


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
    headers = {
        "authorization": "Bearer token123",
        "cookie": "session=abc",
    }
    result = sanitize_headers(headers)
    assert result["authorization"] == REDACTED
    assert result["cookie"] == REDACTED


def test_response_hook_with_string_body():
    captured_data = []
    t = Telemetry()
    t.enabled = True
    t.callback = lambda data: captured_data.append(data)

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
    assert data["session_id"] == t.session_id
    assert data["garth_version"] == __version__
    assert "secret" not in data["request_body"]
    assert "token123" not in data["response_body"]


def test_response_hook_with_bytes_body():
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
    captured_data = []
    t = Telemetry()
    t.enabled = False
    t.callback = lambda data: captured_data.append(data)

    response = MagicMock()
    t._response_hook(response)

    assert len(captured_data) == 0


def test_response_hook_handles_exceptions():
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

    # Should not raise
    t._response_hook(response)


def test_scrubbing_callback_bypasses_logfire_scrubbing():
    m = MagicMock()
    m.value = "test body"

    result = _scrubbing_callback(m)
    assert result == "test body"


def test_telemetry_env_enabled_with_mock(monkeypatch):
    import garth.telemetry as telemetry_module

    monkeypatch.setenv("GARTH_TELEMETRY_ENABLED", "true")
    monkeypatch.delenv("GARTH_TELEMETRY_TOKEN", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_SEND_TO_LOGFIRE", raising=False)

    mock_logfire = MagicMock()
    monkeypatch.setattr(telemetry_module, "logfire", mock_logfire)

    t = Telemetry()
    t.configure()

    assert t.enabled is True
    assert t._logfire_configured is True
    mock_logfire.configure.assert_called_once()


def test_telemetry_attach_to_session():
    t = Telemetry()
    t.enabled = True

    session = Session()
    initial_hook_count = len(session.hooks["response"])

    t.attach(session)

    assert len(session.hooks["response"]) == initial_hook_count + 1
    assert t._response_hook in session.hooks["response"]


def test_telemetry_attach_idempotent():
    t = Telemetry()
    t.enabled = True

    session = Session()
    initial_hook_count = len(session.hooks["response"])

    t.attach(session)
    t.attach(session)
    t.attach(session)

    assert len(session.hooks["response"]) == initial_hook_count + 1


def test_telemetry_custom_callback_skips_logfire(monkeypatch):
    monkeypatch.setenv("GARTH_TELEMETRY_ENABLED", "true")
    monkeypatch.delenv("GARTH_TELEMETRY_TOKEN", raising=False)

    t = Telemetry()
    t.configure(callback=lambda data: None)

    assert t.enabled is True
    assert t._logfire_configured is False


def test_client_telemetry_callback(monkeypatch):
    monkeypatch.delenv("GARTH_HOME", raising=False)
    monkeypatch.delenv("GARTH_TOKEN", raising=False)
    monkeypatch.delenv("GARTH_TELEMETRY_ENABLED", raising=False)

    captured_data = []
    client = Client()
    client.configure(
        telemetry_enabled=True,
        telemetry_callback=lambda data: captured_data.append(data),
    )

    assert client.telemetry.enabled is True
    assert client.telemetry.callback is not None


def test_default_callback_calls_logfire_instance():
    mock_instance = MagicMock()

    t = Telemetry()
    t._logfire_configured = True
    t._logfire_instance = mock_instance
    data = {
        "method": "GET",
        "url": "https://example.com/api",
        "status_code": 200,
    }

    t._default_callback(data)

    mock_instance.info.assert_called_once_with(
        "http {method} {url} {status_code}", **data
    )


def test_default_callback_skips_when_logfire_unavailable(monkeypatch):
    import garth.telemetry as telemetry_module

    monkeypatch.setattr(telemetry_module, "LOGFIRE_AVAILABLE", False)

    t = Telemetry()
    data = {
        "method": "GET",
        "url": "https://example.com/api",
        "status_code": 200,
    }

    # Should not raise
    t._default_callback(data)


def test_configure_logfire_skips_when_unavailable(monkeypatch):
    import garth.telemetry as telemetry_module

    monkeypatch.setattr(telemetry_module, "LOGFIRE_AVAILABLE", False)

    t = Telemetry()
    t.enabled = True
    t._configure_logfire()

    assert t._logfire_configured is False


def test_configure_logfire_uses_local_instance(monkeypatch):
    """logfire.configure is called with local=True to avoid
    overwriting the host app's logfire config."""
    import garth.telemetry as telemetry_module

    mock_logfire = MagicMock()
    monkeypatch.setattr(telemetry_module, "logfire", mock_logfire)

    t = Telemetry()
    t.enabled = True
    t._configure_logfire()

    mock_logfire.configure.assert_called_once()
    call_kwargs = mock_logfire.configure.call_args[1]
    assert call_kwargs["local"] is True
    assert call_kwargs["service_name"] == "garth"
    assert t._logfire_instance is not None


def test_session_id_unique():
    t1 = Telemetry()
    t2 = Telemetry()
    assert t1.session_id != t2.session_id
    assert len(t1.session_id) == 16
