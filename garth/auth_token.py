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
    expires: int
    refresh_token_expires_in: int
    refresh_token_expires: int

    @classmethod
    def login(cls, *args, **kwargs) -> tuple["AuthToken", str]:
        token, username = sso.login(*args, **kwargs)
        return cls(**token), username

    def refresh(self, **kwargs):
        if self.refresh_expired:
            token = sso.exchange(**kwargs)
        else:
            token = self.__class__(**sso.refresh(self.refresh_token, **kwargs))
        self.__dict__.update(token.__dict__)

    @property
    def expired(self):
        return self.expires < time.time()

    @property
    def refresh_expired(self):
        return self.refresh_token_expires < time.time()

    def __str__(self):
        return f"{self.token_type} {self.access_token}"
