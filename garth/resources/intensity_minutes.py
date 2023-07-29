from typing import ClassVar

from pydantic.dataclasses import dataclass

from ..stats import Stats

BASE_PATH = "/usersummary-service/stats/im"


@dataclass(frozen=True)
class DailyIntensityMinutes(Stats):
    weekly_goal: int
    moderate_value: int
    vigorous_value: int

    _path: ClassVar[str] = f"{BASE_PATH}/daily/{{start}}/{{end}}"
    _page_size: ClassVar[int] = 28


@dataclass(frozen=True)
class WeeklyIntensityMinutes(Stats):
    weekly_goal: int
    moderate_value: int
    vigorous_value: int

    _path: ClassVar[str] = f"{BASE_PATH}/weekly/{{start}}/{{end}}"
    _page_size: ClassVar[int] = 52
