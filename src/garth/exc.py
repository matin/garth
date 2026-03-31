from dataclasses import dataclass


@dataclass
class GarthException(Exception):
    """Base exception for all garth exceptions."""

    msg: str

    def __str__(self) -> str:
        return self.msg


@dataclass
class GarthHTTPError(GarthException):
    error: Exception

    def __str__(self) -> str:
        return f"{self.msg}: {self.error}"
