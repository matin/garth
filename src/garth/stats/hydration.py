from typing import ClassVar

from pydantic.dataclasses import dataclass

from ._base import Stats


BASE_PATH = "/usersummary-service/stats/hydration"


@dataclass
class DailyHydration(Stats):
    value_in_ml: float
    goal_in_ml: float

    _path: ClassVar[str] = f"{BASE_PATH}/daily/{{start}}/{{end}}"
    _page_size: ClassVar[int] = 28
