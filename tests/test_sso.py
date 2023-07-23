import time

import pytest
from requests import HTTPError

from garth import sso
from garth.auth_token import AuthToken
from garth.exc import GarthException
from garth.http import Client


@pytest.mark.vcr
def test_login_email_password_fail(client: Client):
    with pytest.raises(HTTPError):
        sso.login("user@example.com", "wrong_p@ssword", client=client)


@pytest.mark.vcr
def test_login_success(monkeypatch, client: Client):
    def mock_input(_):
        return "327751"

    monkeypatch.setattr("builtins.input", mock_input)
    sso.login("user@example.com", "correct_password", client=client)


def test_set_expirations(auth_token_dict: dict):
    token = sso.set_expirations(auth_token_dict)
    assert (
        token["expires_at"] - time.time() - auth_token_dict["expires_in"] < 1
    )
    assert (
        token["refresh_token_expires_at"]
        - time.time()
        - auth_token_dict["refresh_token_expires_in"]
        < 1
    )


@pytest.mark.vcr
def test_exchange(authed_client: Client):
    token = sso.exchange(authed_client)
    auth_token = AuthToken(**token)
    assert not auth_token.expired
    assert not auth_token.refresh_expired
    assert auth_token.token_type.title() == "Bearer"
    assert authed_client.auth_token != auth_token


@pytest.mark.vcr
def test_refresh(authed_client: Client):
    assert authed_client.auth_token is not None
    refresh_token = authed_client.auth_token.refresh_token
    token = sso.refresh(refresh_token, authed_client)
    auth_token = AuthToken(**token)
    assert not auth_token.expired
    assert not auth_token.refresh_expired
    assert auth_token.token_type.title() == "Bearer"
    assert authed_client.auth_token != auth_token


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
