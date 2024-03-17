from typing import ClassVar, Optional

from pydantic.dataclasses import dataclass

from ._base import Stats


@dataclass(frozen=True)
class DailySleep(Stats):
    value: Optional[int]

    _path: ClassVar[
        str
    ] = "/wellness-service/stats/daily/sleep/score/{start}/{end}"
    _page_size: ClassVar[int] = 28
