import time

import pytest

from garth.auth_token import AuthToken


@pytest.fixture
def auth_token() -> AuthToken:
    token = AuthToken(
        scope="CONNECT_READ CONNECT_WRITE",
        jti="xxx",
        token_type="Bearer",
        access_token="yyy",
        refresh_token="zzz",
        expires_in=3599,
        expires_at=int(time.time() + 3599),
        refresh_token_expires_in=7199,
        refresh_token_expires_at=int(time.time() + 7199),
    )
    return token


def test_expired(auth_token: AuthToken):
    auth_token.expires_at = int(time.time() - 1)
    assert auth_token.expired is True
