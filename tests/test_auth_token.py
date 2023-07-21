import time

from garth.auth_token import AuthToken


def test_expired(auth_token: AuthToken):
    auth_token.expires_at = int(time.time() - 1)
    assert auth_token.expired is True


def test_refresh_expired(auth_token: AuthToken):
    auth_token.refresh_token_expires_at = int(time.time() - 1)
    assert auth_token.refresh_expired is True


def test_str(auth_token: AuthToken):
    assert str(auth_token) == "Bearer bar"
