from datetime import date
from typing import ClassVar

from pydantic.dataclasses import dataclass

from ..stats import Stats


@dataclass(frozen=True)
class DailySleep(Stats):
    calendar_date: date

    _path: ClassVar[str] = "/wellness-service/stats/daily/sleep/score"
    _page_size: ClassVar[int] = 28
