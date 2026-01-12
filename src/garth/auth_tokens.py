import time
from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass(repr=False)
class OAuth1Token:
    oauth_token: str
    oauth_token_secret: str
    mfa_token: str | None = None
    mfa_expiration_timestamp: datetime | None = None
    domain: str | None = None

    def __repr__(self):
        return (
            f"OAuth1Token(oauth_token={self.oauth_token!r}, "
            f"oauth_token_secret='***', "
            f"mfa_token={self.mfa_token!r}, "
            f"mfa_expiration_timestamp={self.mfa_expiration_timestamp!r}, "
            f"domain={self.domain!r})"
        )


@dataclass(repr=False)
class OAuth2Token:
    scope: str
    jti: str
    token_type: str
    access_token: str
    refresh_token: str
    expires_in: int
    expires_at: int
    refresh_token_expires_in: int
    refresh_token_expires_at: int

    @property
    def expired(self):
        return self.expires_at < time.time()

    @property
    def refresh_expired(self):
        return self.refresh_token_expires_at < time.time()

    def __repr__(self):
        return (
            f"OAuth2Token(scope={self.scope!r}, "
            f"jti={self.jti!r}, "
            f"token_type={self.token_type!r}, "
            f"access_token='***', "
            f"refresh_token='***', "
            f"expires_in={self.expires_in!r}, "
            f"expires_at={self.expires_at!r}, "
            f"refresh_token_expires_in={self.refresh_token_expires_in!r}, "
            f"refresh_token_expires_at={self.refresh_token_expires_at!r})"
        )

    def __str__(self):
        return f"{self.token_type.title()} {self.access_token}"
