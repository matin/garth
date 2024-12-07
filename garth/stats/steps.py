from typing import ClassVar

from pydantic.dataclasses import dataclass

from ._base import Stats


BASE_PATH = "/usersummary-service/stats/steps"


@dataclass(frozen=True)
class DailySteps(Stats):
    total_steps: int
    total_distance: int
    step_goal: int

    _path: ClassVar[str] = f"{BASE_PATH}/daily/{{start}}/{{end}}"
    _page_size: ClassVar[int] = 28


@dataclass(frozen=True)
class WeeklySteps(Stats):
    total_steps: int
    average_steps: float
    average_distance: float
    total_distance: float
    wellness_data_days_count: int

    _path: ClassVar[str] = f"{BASE_PATH}/weekly/{{end}}/{{period}}"
    _page_size: ClassVar[int] = 52
