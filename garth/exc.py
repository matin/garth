from dataclasses import dataclass

from requests import HTTPError


@dataclass(frozen=True)
class GarthException(Exception):
    """Base exception for all garth exceptions."""

    msg: str


@dataclass(frozen=True)
class GarthHTTPError(GarthException):
    error: HTTPError

    def __str__(self) -> str:
        return f"{self.msg}: {self.error}"
