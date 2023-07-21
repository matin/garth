import time

import pytest

from garth.auth_token import AuthToken
from garth.http import Client


@pytest.fixture
def auth_token() -> AuthToken:
    token = AuthToken(
        scope="CONNECT_READ CONNECT_WRITE",
        jti="foo",
        token_type="Bearer",
        access_token="bar",
        refresh_token="baz",
        expires_in=3599,
        expires_at=int(time.time() + 3599),
        refresh_token_expires_in=7199,
        refresh_token_expires_at=int(time.time() + 7199),
    )
    return token


@pytest.fixture
def client():
    return Client()
