from typing import ClassVar

from pydantic.dataclasses import dataclass

from ._base import Stats


BASE_PATH = "/usersummary-service/stats/im"


@dataclass
class DailyIntensityMinutes(Stats):
    weekly_goal: int
    moderate_value: int | None = None
    vigorous_value: int | None = None

    _path: ClassVar[str] = f"{BASE_PATH}/daily/{{start}}/{{end}}"
    _page_size: ClassVar[int] = 28


@dataclass
class WeeklyIntensityMinutes(Stats):
    weekly_goal: int
    moderate_value: int | None = None
    vigorous_value: int | None = None

    _path: ClassVar[str] = f"{BASE_PATH}/weekly/{{start}}/{{end}}"
    _page_size: ClassVar[int] = 52
