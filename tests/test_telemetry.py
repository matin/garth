from unittest.mock import MagicMock

import pytest

from garth.http import Client
from garth.telemetry import (
    REDACTED,
    Telemetry,
    _response_hook,
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
def test_telemetry_enabled_request(authed_client: Client):
    """Test that telemetry works with real API requests (VCR recorded)."""
    # Configure telemetry with send_to_logfire=False to avoid needing
    # credentials. This still enables request instrumentation via OTel.
    authed_client.telemetry.configure(enabled=True, send_to_logfire=False)

    assert authed_client.telemetry.enabled is True
    assert authed_client.telemetry._configured is True

    # Make a real API request - this will be recorded by VCR
    profile = authed_client.connectapi("/userprofile-service/socialProfile")
    assert profile is not None
    assert "displayName" in profile


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
    t.configure(
        service_name="test-service",
        enabled=False,
        send_to_logfire=False,
        token="test-token",
    )
    assert t.service_name == "test-service"
    assert t.enabled is False
    assert t.send_to_logfire is False
    assert t.token == "test-token"


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
    span = MagicMock()
    request = MagicMock()
    request.headers = {"Content-Type": "application/json"}
    request.body = '{"password": "secret"}'
    response = MagicMock()
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"access_token": "token123"}'

    _response_hook(span, request, response)

    # Check that attributes were set
    assert span.set_attribute.call_count == 4
    calls = {
        call[0][0]: call[0][1] for call in span.set_attribute.call_args_list
    }
    assert "http.request.headers" in calls
    assert "http.request.body" in calls
    assert "http.response.headers" in calls
    assert "http.response.body" in calls
    # Verify sanitization
    assert "secret" not in calls["http.request.body"]
    assert "token123" not in calls["http.response.body"]


def test_response_hook_with_bytes_body():
    span = MagicMock()
    request = MagicMock()
    request.headers = {"Content-Type": "application/json"}
    request.body = b'{"password": "secret"}'
    response = MagicMock()
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"data": "ok"}'

    _response_hook(span, request, response)

    calls = {
        call[0][0]: call[0][1] for call in span.set_attribute.call_args_list
    }
    assert "http.request.body" in calls
    assert "secret" not in calls["http.request.body"]


def test_response_hook_no_body():
    span = MagicMock()
    request = MagicMock()
    request.headers = {"Content-Type": "application/json"}
    request.body = None
    response = MagicMock()
    response.headers = {"Content-Type": "application/json"}
    response.text = '{"data": "ok"}'

    _response_hook(span, request, response)

    # Should only set 3 attributes (no request body)
    assert span.set_attribute.call_count == 3


def test_response_hook_handles_exceptions():
    span = MagicMock()
    span.set_attribute.side_effect = Exception("test error")
    request = MagicMock()
    request.headers = {"Content-Type": "application/json"}
    request.body = "test"
    response = MagicMock()
    response.headers = {"Content-Type": "application/json"}
    response.text = "test"

    # Should not raise, just silently handle exceptions
    _response_hook(span, request, response)


def test_scrubbing_callback_allows_http_attributes():
    m = MagicMock()
    m.path = ("attributes", "http.request.body")
    m.value = "test body"

    result = _scrubbing_callback(m)
    assert result == "test body"


def test_scrubbing_callback_default_scrubbing():
    m = MagicMock()
    m.path = ("attributes", "other.attribute")
    m.value = "sensitive"

    result = _scrubbing_callback(m)
    assert result is None  # Use default scrubbing


def test_telemetry_env_enabled_with_mock(monkeypatch):
    """Test GARTH_TELEMETRY=true enables telemetry."""
    import sys

    monkeypatch.setenv("GARTH_TELEMETRY", "true")
    monkeypatch.delenv("GARTH_TELEMETRY_SERVICE_NAME", raising=False)
    monkeypatch.delenv("LOGFIRE_SEND_TO_LOGFIRE", raising=False)

    mock_logfire = MagicMock()
    monkeypatch.setitem(sys.modules, "logfire", mock_logfire)

    t = Telemetry()
    t.configure()

    assert t.enabled is True
    assert t._configured is True
    mock_logfire.configure.assert_called_once()
    mock_logfire.instrument_requests.assert_called_once()


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
