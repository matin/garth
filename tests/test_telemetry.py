import pytest

from garth.http import Client
from garth.telemetry import Telemetry, sanitize


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
