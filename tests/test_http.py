import tempfile
import time
from typing import Any, cast

import pytest

from garth import sso
from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.exc import GarthException, GarthHTTPError
from garth.http import Client, _Response


def test_dump_and_load(authed_client: Client):
    with tempfile.TemporaryDirectory() as tempdir:
        authed_client.dump(tempdir)

        new_client = Client()
        new_client.load(tempdir)

        assert new_client.oauth1_token == authed_client.oauth1_token
        assert new_client.oauth2_token == authed_client.oauth2_token


def test_dumps_and_loads(authed_client: Client):
    s = authed_client.dumps()
    new_client = Client()
    new_client.loads(s)
    assert new_client.oauth1_token == authed_client.oauth1_token
    assert new_client.oauth2_token == authed_client.oauth2_token


def test_auto_resume_garth_home(
    authed_client: Client, monkeypatch: pytest.MonkeyPatch
):
    with tempfile.TemporaryDirectory() as tempdir:
        authed_client.dump(tempdir)
        monkeypatch.setenv("GARTH_HOME", tempdir)
        monkeypatch.delenv("GARTH_TOKEN", raising=False)

        client = Client()
        assert client.oauth1_token == authed_client.oauth1_token
        assert client.oauth2_token == authed_client.oauth2_token


def test_auto_resume_garth_token(
    authed_client: Client, monkeypatch: pytest.MonkeyPatch
):
    token = authed_client.dumps()
    monkeypatch.setenv("GARTH_TOKEN", token)
    monkeypatch.delenv("GARTH_HOME", raising=False)

    client = Client()
    assert client.oauth1_token == authed_client.oauth1_token
    assert client.oauth2_token == authed_client.oauth2_token


def test_auto_resume_garth_home_missing_tokens(
    monkeypatch: pytest.MonkeyPatch,
):
    with tempfile.TemporaryDirectory() as tempdir:
        monkeypatch.setenv("GARTH_HOME", tempdir)
        monkeypatch.delenv("GARTH_TOKEN", raising=False)

        client = Client()
        assert client._garth_home == tempdir
        assert client.oauth1_token is None
        assert client.oauth2_token is None


def test_auto_resume_both_set_raises(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("GARTH_HOME", "/some/path")
    monkeypatch.setenv("GARTH_TOKEN", "some_token")

    with pytest.raises(GarthException, match="cannot both be set"):
        Client()


def test_load_browser_tokens_warns(caplog):
    """Loading browser-backed tokens should warn the user."""
    browser_oauth1 = OAuth1Token(
        oauth_token=sso.BROWSER_TOKEN_SENTINEL,
        oauth_token_secret=sso.BROWSER_TOKEN_SENTINEL,
        domain="garmin.com",
    )
    browser_oauth2 = sso._placeholder_oauth2()

    with tempfile.TemporaryDirectory() as tempdir:
        # Save browser tokens
        client = Client()
        client.configure(
            oauth1_token=browser_oauth1,
            oauth2_token=browser_oauth2,
        )
        client.dump(tempdir)

        # Load them back — should warn
        import logging
        with caplog.at_level(logging.WARNING, logger="garth.http"):
            new_client = Client()
            new_client.load(tempdir)

        assert "browser-session" in caplog.text
        assert "call login()" in caplog.text


def test_loads_browser_tokens_warns(caplog):
    """Loading browser-backed tokens from string should warn."""
    browser_oauth1 = OAuth1Token(
        oauth_token=sso.BROWSER_TOKEN_SENTINEL,
        oauth_token_secret=sso.BROWSER_TOKEN_SENTINEL,
        domain="garmin.com",
    )
    browser_oauth2 = sso._placeholder_oauth2()

    client = Client()
    client.configure(
        oauth1_token=browser_oauth1,
        oauth2_token=browser_oauth2,
    )
    token_str = client.dumps()

    import logging
    with caplog.at_level(logging.WARNING, logger="garth.http"):
        new_client = Client()
        new_client.loads(token_str)

    assert "browser-session" in caplog.text


def test_configure_oauth2_token(
    client: Client, oauth2_token: OAuth2Token
):
    assert client.oauth2_token is None
    client.configure(oauth2_token=oauth2_token)
    assert client.oauth2_token == oauth2_token


def test_configure_domain(client: Client):
    assert client.domain == "garmin.com"
    client.configure(domain="garmin.cn")
    assert client.domain == "garmin.cn"


def test_configure_timeout(client: Client):
    assert client.timeout == 10
    client.configure(timeout=99)
    assert client.timeout == 99


def test_configure_retry(client: Client):
    assert client.retries == 3
    client.configure(retries=99)
    assert client.retries == 99


def test_configure_proxies_warns(client: Client, caplog):
    """Proxies should emit a warning with browser transport."""
    import logging
    with caplog.at_level(logging.WARNING, logger="garth.http"):
        client.configure(proxies={"https": "http://localhost"})
    assert "proxies" in caplog.text


def test_configure_ssl_verify_warns(client: Client, caplog):
    """ssl_verify should emit a warning with browser transport."""
    import logging
    with caplog.at_level(logging.WARNING, logger="garth.http"):
        client.configure(ssl_verify=False)
    assert "ssl_verify" in caplog.text


def test_request_requires_login(client: Client):
    with pytest.raises(GarthException, match="Not logged in"):
        client.request("GET", "connectapi", "/test-path")


def test_response_class():
    resp = _Response(200, '{"key": "value"}', "https://example.com")
    assert resp.ok
    assert resp.status_code == 200
    assert resp.json() == {"key": "value"}
    assert resp.content == b'{"key": "value"}'
    resp.raise_for_status()


def test_response_error():
    resp = _Response(403, "Forbidden", "https://example.com")
    assert not resp.ok
    with pytest.raises(GarthHTTPError, match="403"):
        resp.raise_for_status()


@pytest.mark.vcr
def test_connectapi(authed_client: Client):
    stress = cast(
        list[dict[str, Any]],
        authed_client.connectapi(
            "/usersummary-service/stats/stress/daily/"
            "2023-07-21/2023-07-21"
        ),
    )
    assert stress
    assert isinstance(stress, list)
    assert len(stress) == 1
    assert stress[0]["calendarDate"] == "2023-07-21"
    assert list(stress[0]["values"].keys()) == [
        "highStressDuration",
        "lowStressDuration",
        "overallStressLevel",
        "restStressDuration",
        "mediumStressDuration",
    ]


@pytest.mark.vcr
def test_username(authed_client: Client):
    assert authed_client._user_profile is None
    assert authed_client.username
    assert authed_client._user_profile


@pytest.mark.vcr
def test_profile_alias(authed_client: Client):
    assert authed_client._user_profile is None
    profile = authed_client.profile
    assert profile == authed_client.user_profile
    assert authed_client._user_profile is not None


def test_download(authed_client: Client, monkeypatch):
    """Download returns bytes via browser fetch."""
    class MockPage:
        def evaluate(self, js, args):
            import base64
            data = base64.b64encode(
                b"\x50\x4b\x03\x04test"
            ).decode()
            return {"status": 200, "data": data}

    monkeypatch.setattr(sso, "get_page", lambda: MockPage())
    monkeypatch.setattr(sso, "get_csrf", lambda: "test_csrf")

    result = authed_client.download(
        "/download-service/files/activity/11998957007"
    )
    assert result
    assert isinstance(result, bytes)
    assert result[:4] == b"\x50\x4b\x03\x04"


def test_upload_rejects_multiple_files(
    authed_client: Client, monkeypatch
):
    """Upload should reject multiple files."""
    class MockPage:
        def evaluate(self, js, args):
            return {"status": 200, "text": "{}", "url": ""}

    monkeypatch.setattr(sso, "get_page", lambda: MockPage())
    monkeypatch.setattr(sso, "get_csrf", lambda: "test_csrf")

    import io
    files = {
        "file1": ("a.fit", io.BytesIO(b"data1")),
        "file2": ("b.fit", io.BytesIO(b"data2")),
    }
    with pytest.raises(GarthException, match="single file"):
        authed_client.request(
            "POST", "connectapi", "/upload", files=files
        )


@pytest.fixture
def garth_home_client(monkeypatch: pytest.MonkeyPatch):
    """Client with GARTH_HOME set to a temp dir."""
    import garth.sso

    with tempfile.TemporaryDirectory() as tempdir:
        monkeypatch.setenv("GARTH_HOME", tempdir)
        monkeypatch.delenv("GARTH_TOKEN", raising=False)

        client = Client()
        mock_oauth1 = OAuth1Token(
            oauth_token="test_token",
            oauth_token_secret="test_secret",
            domain="garmin.com",
        )
        mock_oauth2 = OAuth2Token(
            scope="CONNECT_READ",
            jti="test_jti",
            token_type="Bearer",
            access_token="test_access",
            refresh_token="test_refresh",
            expires_in=3600,
            refresh_token_expires_in=7200,
            expires_at=int(time.time() + 3600),
            refresh_token_expires_at=int(time.time() + 7200),
        )
        yield (
            client, tempdir, mock_oauth1, mock_oauth2, garth.sso
        )


def _assert_tokens_saved(tempdir, mock_oauth1, mock_oauth2):
    loaded = Client()
    loaded.load(tempdir)
    assert loaded.oauth1_token == mock_oauth1
    assert loaded.oauth2_token == mock_oauth2


def test_auto_save_on_login(garth_home_client, monkeypatch):
    client, tempdir, mock_oauth1, mock_oauth2, sso_mod = (
        garth_home_client
    )
    monkeypatch.setattr(
        sso_mod,
        "login",
        lambda *a, **kw: (mock_oauth1, mock_oauth2),
    )

    client.login("user@example.com", "password")
    _assert_tokens_saved(tempdir, mock_oauth1, mock_oauth2)


def test_auto_persist_on_refresh(
    authed_client: Client, monkeypatch: pytest.MonkeyPatch
):
    with tempfile.TemporaryDirectory() as tempdir:
        authed_client.dump(tempdir)
        monkeypatch.setenv("GARTH_HOME", tempdir)
        monkeypatch.delenv("GARTH_TOKEN", raising=False)

        client = Client()
        assert client._garth_home == tempdir

        new_oauth2 = OAuth2Token(
            scope="CONNECT_READ CONNECT_WRITE",
            jti="new_jti",
            token_type="Bearer",
            access_token="new_access_token",
            refresh_token="new_refresh_token",
            expires_in=7200,
            refresh_token_expires_in=14400,
            expires_at=int(time.time() + 7200),
            refresh_token_expires_at=int(time.time() + 14400),
        )

        import garth.sso
        monkeypatch.setattr(
            garth.sso,
            "exchange",
            lambda *args, **kwargs: new_oauth2,
        )

        import os
        oauth1_path = os.path.join(tempdir, "oauth1_token.json")
        oauth1_mtime_before = os.path.getmtime(oauth1_path)
        time.sleep(0.01)

        client.refresh_oauth2()

        oauth1_mtime_after = os.path.getmtime(oauth1_path)
        assert oauth1_mtime_before == oauth1_mtime_after

        fresh_client = Client()
        fresh_client.load(tempdir)
        assert fresh_client.oauth2_token == new_oauth2
