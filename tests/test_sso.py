import time

import pytest

from garth import sso
from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.exc import GarthException, GarthHTTPError
from garth.http import Client


@pytest.mark.vcr
def test_login_email_password_fail(client: Client):
    with pytest.raises(GarthHTTPError):
        sso.login("user@example.com", "wrong_p@ssword", client=client)


@pytest.mark.vcr
def test_login_success(client: Client):
    oauth1, oauth2 = sso.login(
        "user@example.com", "correct_password", client=client
    )

    assert oauth1
    assert isinstance(oauth1, OAuth1Token)
    assert oauth2
    assert isinstance(oauth2, OAuth2Token)


@pytest.mark.vcr
def test_login_success_mfa(monkeypatch, client: Client):
    def mock_input(_):
        return "671091"

    monkeypatch.setattr("builtins.input", mock_input)
    oauth1, oauth2 = sso.login(
        "user@example.com", "correct_password", client=client
    )

    assert oauth1
    assert isinstance(oauth1, OAuth1Token)
    assert oauth2
    assert isinstance(oauth2, OAuth2Token)


@pytest.mark.vcr
def test_login_success_mfa_async(monkeypatch, client: Client):
    def mock_input(_):
        return "031174"

    async def prompt_mfa():
        return input("MFA code: ")

    monkeypatch.setattr("builtins.input", mock_input)
    oauth1, oauth2 = sso.login(
        "user@example.com",
        "correct_password",
        client=client,
        prompt_mfa=prompt_mfa,
    )

    assert oauth1
    assert isinstance(oauth1, OAuth1Token)
    assert oauth2
    assert isinstance(oauth2, OAuth2Token)


@pytest.mark.vcr
def test_login_mfa_fail(client: Client):
    with pytest.raises(GarthException):
        oauth1, oauth2 = sso.login(
            "user@example.com",
            "correct_password",
            client=client,
            prompt_mfa=lambda: "123456",
        )


@pytest.mark.vcr
def test_login_return_on_mfa(client: Client):
    result = sso.login(
        "user@example.com",
        "correct_password",
        client=client,
        return_on_mfa=True,
    )

    assert isinstance(result, tuple)
    result_type, client_state = result

    assert isinstance(client_state, dict)
    assert result_type == "needs_mfa"
    assert "signin_params" in client_state
    assert "client" in client_state

    code = "123456"  # obtain from custom login

    # test resuming the login
    oauth1, oauth2 = sso.resume_login(client_state, code)

    assert oauth1
    assert isinstance(oauth1, OAuth1Token)
    assert oauth2
    assert isinstance(oauth2, OAuth2Token)


def test_set_expirations(oauth2_token_dict: dict):
    token = sso.set_expirations(oauth2_token_dict)
    assert (
        token["expires_at"] - time.time() - oauth2_token_dict["expires_in"] < 1
    )
    assert (
        token["refresh_token_expires_at"]
        - time.time()
        - oauth2_token_dict["refresh_token_expires_in"]
        < 1
    )


@pytest.mark.vcr
def test_exchange(authed_client: Client):
    assert authed_client.oauth1_token and isinstance(
        authed_client.oauth1_token, OAuth1Token
    )
    oauth1_token = authed_client.oauth1_token
    oauth2_token = sso.exchange(oauth1_token, client=authed_client)
    assert not oauth2_token.expired
    assert not oauth2_token.refresh_expired
    assert oauth2_token.token_type.title() == "Bearer"
    assert authed_client.oauth2_token != oauth2_token


def test_get_csrf_token():
    html = """
    <html>
    <head>
    </head>
    <body>
    <h1>Success</h1>
    <input name="_csrf"    value="foo">
    </body>
    </html>
    """
    assert sso.get_csrf_token(html) == "foo"


def test_get_csrf_token_fail():
    html = """
    <html>
    <head>
    </head>
    <body>
    <h1>Success</h1>
    </body>
    </html>
    """
    with pytest.raises(GarthException):
        sso.get_csrf_token(html)


def test_get_title():
    html = """
    <html>
    <head>
    <title>Success</title>
    </head>
    <body>
    <h1>Success</h1>
    </body>
    </html>
    """
    assert sso.get_title(html) == "Success"


def test_get_title_fail():
    html = """
    <html>
    <head>
    </head>
    <body>
    <h1>Success</h1>
    </body>
    </html>
    """
    with pytest.raises(GarthException):
        sso.get_title(html)
