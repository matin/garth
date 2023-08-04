import time

from garth.auth_tokens import OAuth2Token


def test_is_expired(oauth2_token: OAuth2Token):
    oauth2_token.expires_at = int(time.time() - 1)
    assert oauth2_token.expired is True


def test_refresh_is_expired(oauth2_token: OAuth2Token):
    oauth2_token.refresh_token_expires_at = int(time.time() - 1)
    assert oauth2_token.refresh_expired is True


def test_str(oauth2_token: OAuth2Token):
    assert str(oauth2_token) == "Bearer bar"
