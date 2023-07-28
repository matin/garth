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
    expires_in: int
    expires_at: int
    refresh_token_expires_in: int
    refresh_token_expires_at: int
    username: str

    @classmethod
    def login(cls, *args, **kwargs) -> "AuthToken":
        return cls(**sso.login(*args, **kwargs))

    def refresh(self, **kwargs):
        if self.refresh_expired:
            token = sso.exchange(**kwargs)
        else:
            token = sso.refresh(self.refresh_token, **kwargs)
        self.__dict__.update(token)

    @property
    def expired(self):
        return self.expires_at < time.time()

    @property
    def refresh_expired(self):
        return self.refresh_token_expires_at < time.time()

    def __str__(self):
        return f"{self.token_type.title()} {self.access_token}"
