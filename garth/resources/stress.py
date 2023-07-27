from typing import ClassVar

from pydantic.dataclasses import dataclass

from ..stats import Stats

BASE_PATH = "/usersummary-service/stats/stress"


@dataclass(frozen=True)
class DailyStress(Stats):
    overall_stress_level: int
    rest_stress_duration: int | None
    low_stress_duration: int | None
    medium_stress_duration: int | None
    high_stress_duration: int | None

    _path: ClassVar[str] = f"{BASE_PATH}/daily"
    _page_size: ClassVar[int] = 28


@dataclass(frozen=True)
class WeeklyStress(Stats):
    value: int

    _path: ClassVar[str] = f"{BASE_PATH}/weekly"
    _page_size: ClassVar[int] = 52
