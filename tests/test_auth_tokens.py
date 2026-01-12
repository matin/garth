import time

from garth.auth_tokens import OAuth1Token, OAuth2Token


def test_is_expired(oauth2_token: OAuth2Token):
    oauth2_token.expires_at = int(time.time() - 1)
    assert oauth2_token.expired is True


def test_refresh_is_expired(oauth2_token: OAuth2Token):
    oauth2_token.refresh_token_expires_at = int(time.time() - 1)
    assert oauth2_token.refresh_expired is True


def test_str(oauth2_token: OAuth2Token):
    assert str(oauth2_token) == "Bearer bar"


def test_oauth1_repr_hides_secret(oauth1_token: OAuth1Token):
    r = repr(oauth1_token)
    assert "oauth_token_secret='***'" in r
    assert oauth1_token.oauth_token_secret not in r


def test_oauth2_repr_hides_tokens(oauth2_token: OAuth2Token):
    r = repr(oauth2_token)
    assert "access_token='***'" in r
    assert "refresh_token='***'" in r
    assert oauth2_token.access_token not in r
    assert oauth2_token.refresh_token not in r
