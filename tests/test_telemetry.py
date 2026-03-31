from garth.telemetry import (
    REDACTED,
    Telemetry,
    sanitize,
    sanitize_cookie,
    sanitize_headers,
)


def test_sanitize_password():
    text = '{"username": "user@email.com", "password": "s3cr3t"}'
    result = sanitize(text)
    assert "s3cr3t" not in result
    assert REDACTED in result


def test_sanitize_tokens():
    text = '{"access_token": "abc123", "refresh_token": "xyz789"}'
    result = sanitize(text)
    assert "abc123" not in result
    assert "xyz789" not in result


def test_sanitize_oauth_tokens():
    text = '{"oauth_token": "abc", "oauth_token_secret": "xyz"}'
    result = sanitize(text)
    assert '"abc"' not in result
    assert '"xyz"' not in result


def test_sanitize_query_params():
    text = "password=s3cr3t&username=user@email.com&other=keep"
    result = sanitize(text)
    assert "s3cr3t" not in result
    assert "user@email.com" not in result
    assert "keep" in result


def test_telemetry_defaults():
    t = Telemetry()
    assert not t.enabled
    assert not t.send_to_logfire
    assert t.callback is None


def test_telemetry_configure_disabled():
    t = Telemetry()
    t.configure(enabled=False)
    assert not t.enabled


def test_telemetry_env_override_disabled(monkeypatch):
    monkeypatch.setenv("GARTH_TELEMETRY_ENABLED", "false")
    t = Telemetry()
    assert not t.enabled


def test_telemetry_configure_all_params():
    callback = lambda data: None  # noqa: E731
    t = Telemetry()
    t.configure(
        enabled=True,
        send_to_logfire=False,
        token="test_token",
        callback=callback,
    )
    assert t.enabled
    assert not t.send_to_logfire
    assert t.token == "test_token"
    assert t.callback == callback


def test_sanitize_cookie():
    cookie = "GARMIN-SSO=abc123; Path=/; Secure"
    result = sanitize_cookie(cookie)
    assert "abc123" not in result
    assert REDACTED in result


def test_sanitize_headers():
    headers = {
        "Authorization": "Bearer token123",
        "Content-Type": "application/json",
        "Cookie": "session=abc",
    }
    result = sanitize_headers(headers)
    assert result["Authorization"] == REDACTED
    assert result["Cookie"] == REDACTED
    assert result["Content-Type"] == "application/json"


def test_sanitize_headers_case_insensitive():
    headers = {"authorization": "Bearer token"}
    result = sanitize_headers(headers)
    assert result["authorization"] == REDACTED


def test_session_id_unique():
    t1 = Telemetry()
    t2 = Telemetry()
    assert t1.session_id != t2.session_id
