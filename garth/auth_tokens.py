import time
from datetime import datetime

from pydantic.dataclasses import dataclass


@dataclass
class OAuth1Token:
    oauth_token: str
    oauth_token_secret: str
    mfa_token: str | None = None
    mfa_expiration_timestamp: datetime | None = None
    domain: str | None = None


@dataclass
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

    def __str__(self):
        return f"{self.token_type.title()} {self.access_token}"
