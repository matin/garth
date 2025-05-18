from typing import ClassVar

from pydantic.dataclasses import dataclass

from ._base import Stats


BASE_PATH = "/usersummary-service/stats/stress"


@dataclass
class DailyStress(Stats):
    overall_stress_level: int
    rest_stress_duration: int | None = None
    low_stress_duration: int | None = None
    medium_stress_duration: int | None = None
    high_stress_duration: int | None = None

    _path: ClassVar[str] = f"{BASE_PATH}/daily/{{start}}/{{end}}"
    _page_size: ClassVar[int] = 28


@dataclass
class WeeklyStress(Stats):
    value: int

    _path: ClassVar[str] = f"{BASE_PATH}/weekly/{{end}}/{{period}}"
    _page_size: ClassVar[int] = 52
