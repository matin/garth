import time

import pytest

from garth import sso
from garth.auth_tokens import OAuth1Token, OAuth2Token


def test_set_expirations(oauth2_token_dict: dict):
    token = sso.set_expirations(oauth2_token_dict)
    assert (
        token["expires_at"]
        - time.time()
        - oauth2_token_dict["expires_in"]
        < 1
    )
    assert (
        token["refresh_token_expires_at"]
        - time.time()
        - oauth2_token_dict["refresh_token_expires_in"]
        < 1
    )


def test_exchange_returns_oauth2(oauth1_token: OAuth1Token):
    from garth.http import Client

    client = Client()
    oauth2 = sso.exchange(oauth1_token, client)
    assert isinstance(oauth2, OAuth2Token)
    assert not oauth2.expired
    assert oauth2.token_type == "Bearer"
    assert oauth2.access_token == sso.BROWSER_TOKEN_SENTINEL


def test_placeholder_oauth2():
    token = sso._placeholder_oauth2()
    assert isinstance(token, OAuth2Token)
    assert token.access_token == sso.BROWSER_TOKEN_SENTINEL
    assert not token.expired


def test_is_browser_token():
    oauth1 = OAuth1Token(
        oauth_token=sso.BROWSER_TOKEN_SENTINEL,
        oauth_token_secret=sso.BROWSER_TOKEN_SENTINEL,
        domain="garmin.com",
    )
    assert sso.is_browser_token(oauth1)

    oauth1_real = OAuth1Token(
        oauth_token="real_token",
        oauth_token_secret="real_secret",
        domain="garmin.com",
    )
    assert not sso.is_browser_token(oauth1_real)
    assert not sso.is_browser_token(None)


def test_handle_mfa_not_implemented():
    from garth.http import Client

    client = Client()
    with pytest.raises(NotImplementedError):
        sso.handle_mfa(client, {}, lambda: "123456")


def test_resume_login_not_implemented():
    with pytest.raises(NotImplementedError):
        sso.resume_login({}, "123456")


def test_get_page_returns_none_before_login():
    assert sso.get_page() is None


def test_get_csrf_returns_none_before_login():
    assert sso.get_csrf() is None


def test_close_is_safe_before_login():
    sso.close()


def test_close_clears_all_state():
    sso.close()
    assert sso.get_page() is None
    assert sso.get_csrf() is None
    assert sso._browser is None
    assert sso._cm is None
