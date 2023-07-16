import time
from dataclasses import dataclass

from . import sso


@dataclass
class AuthToken:
    scope: str
    jti: str
    token_type: str
    access_token: str
    refresh_token: str
    expires_at: float
    refresh_token_expires_at: float
    username: str

    @classmethod
    def login(cls, *args, **kwargs):
        return cls(**sso.login(*args, **kwargs))

    @property
    def expired(self):
        return self.expires_at < time.time()

    def __str__(self):
        return f"{self.token_type} {self.access_token}"
