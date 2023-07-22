import time

import pytest

from garth.auth_token import AuthToken


@pytest.mark.vcr
def test_login_success(monkeypatch, client):
    def mock_input(_):
        return "327751"

    monkeypatch.setattr("builtins.input", mock_input)
    token = AuthToken.login(
        "user@example.com", "correct_password", client=client
    )
    assert not token.expired
    assert not token.refresh_expired
    assert token.token_type == "Bearer"


def test_expired(auth_token: AuthToken):
    auth_token.expires_at = int(time.time() - 1)
    assert auth_token.expired is True


def test_refresh_expired(auth_token: AuthToken):
    auth_token.refresh_token_expires_at = int(time.time() - 1)
    assert auth_token.refresh_expired is True


def test_str(auth_token: AuthToken):
    assert str(auth_token) == "Bearer bar"
