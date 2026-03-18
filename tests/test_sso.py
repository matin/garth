import time

import pytest
import requests

from garth import sso
from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.exc import GarthException, GarthHTTPError
from garth.http import Client


@pytest.mark.vcr
def test_login_email_password_fail(client: Client):
    with pytest.raises(GarthException):
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
    assert "login_params" in client_state
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


def test_parse_sso_response_success():
    resp = {
        "serviceTicketId": "ST-123",
        "responseStatus": {
            "type": "SUCCESSFUL",
            "message": "",
            "httpStatus": "OK",
        },
    }
    result = sso._parse_sso_response(resp, "SUCCESSFUL")
    assert result["serviceTicketId"] == "ST-123"


def test_parse_sso_response_error():
    resp = {
        "responseStatus": {
            "type": "INVALID_CREDENTIALS",
            "message": "Bad password",
            "httpStatus": "UNAUTHORIZED",
        },
    }
    with pytest.raises(GarthException, match="INVALID_CREDENTIALS"):
        sso._parse_sso_response(resp, "SUCCESSFUL")


def test_parse_sso_response_no_expected():
    resp = {
        "responseStatus": {
            "type": "MFA_REQUIRED",
            "message": "",
            "httpStatus": "OK",
        },
    }
    result = sso._parse_sso_response(resp)
    assert result["responseStatus"]["type"] == "MFA_REQUIRED"


def test_get_oauth1_token_retries_on_401(monkeypatch, client: Client):
    from unittest.mock import MagicMock, patch

    mock_resp_401 = MagicMock()
    mock_resp_401.ok = False
    mock_resp_401.status_code = 401

    mock_resp_200 = MagicMock()
    mock_resp_200.ok = True
    mock_resp_200.text = "oauth_token=tok&oauth_token_secret=sec"

    call_count = {"n": 0}

    def mock_get(*a, **kw):
        call_count["n"] += 1
        if call_count["n"] < 3:
            return mock_resp_401
        return mock_resp_200

    with (
        patch.object(
            sso.GarminOAuth1Session, "__init__", lambda *a, **kw: None
        ),
        patch.object(sso.GarminOAuth1Session, "get", mock_get),
        patch.object(sso.GarminOAuth1Session, "mount", lambda *a, **kw: None),
        patch("time.sleep"),
    ):
        result = sso.get_oauth1_token("ticket", client)
        assert result.oauth_token == "tok"
        assert call_count["n"] == 3


def test_get_oauth1_token_raises_after_retries(monkeypatch, client: Client):
    from unittest.mock import MagicMock, patch

    mock_resp = MagicMock()
    mock_resp.ok = False
    mock_resp.status_code = 401
    mock_resp.raise_for_status.side_effect = requests.HTTPError(
        response=mock_resp
    )

    with (
        patch.object(
            sso.GarminOAuth1Session, "__init__", lambda *a, **kw: None
        ),
        patch.object(
            sso.GarminOAuth1Session, "get", lambda *a, **kw: mock_resp
        ),
        patch.object(sso.GarminOAuth1Session, "mount", lambda *a, **kw: None),
        patch("time.sleep"),
    ):
        with pytest.raises(requests.HTTPError):
            sso.get_oauth1_token("ticket", client)


def test_handle_mfa_http_error(monkeypatch, client: Client):
    from unittest.mock import MagicMock

    def mock_post(*a, **kw):
        raise GarthHTTPError(
            msg="MFA verification failed",
            error=requests.HTTPError(response=MagicMock()),
        )

    monkeypatch.setattr(client, "post", mock_post)

    with pytest.raises(GarthHTTPError, match="MFA verification failed"):
        sso.handle_mfa(client, {"clientId": "X"}, lambda: "123456")


def test_login_unexpected_response_type(monkeypatch, client: Client):
    from unittest.mock import MagicMock

    unexpected_json = {
        "responseStatus": {
            "type": "CAPTCHA_REQUIRED",
            "message": "solve captcha",
            "httpStatus": "OK",
        },
    }

    call_count = 0

    def mock_request(method, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        # First call is the cookie GET, second is the login POST
        if call_count == 2:
            mock_resp.json.return_value = unexpected_json
        client.last_resp = mock_resp
        return mock_resp

    monkeypatch.setattr(client, "request", mock_request)

    with pytest.raises(GarthException, match="CAPTCHA_REQUIRED"):
        sso.login("user@example.com", "password", client=client)
