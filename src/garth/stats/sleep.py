from typing import ClassVar

from pydantic.dataclasses import dataclass

from ._base import Stats


@dataclass
class DailySleep(Stats):
    value: int | None

    _path: ClassVar[str] = (
        "/wellness-service/stats/daily/sleep/score/{start}/{end}"
    )
    _page_size: ClassVar[int] = 28
