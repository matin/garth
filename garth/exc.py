from dataclasses import dataclass


@dataclass
class GarthException(Exception):
    """Base exception for all garth exceptions."""

    msg: str
