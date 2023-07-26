from datetime import date, timedelta
from typing import ClassVar

from pydantic.dataclasses import dataclass

from .. import http
from ..utils import camel_to_snake_dict, format_end_date

BASE_PATH = "/usersummary-service/stats/stress"


@dataclass(frozen=True)
class DailyStress:
    calendar_date: date
    overall_stress_level: int
    rest_stress_duration: int | None
    low_stress_duration: int | None
    medium_stress_duration: int | None
    high_stress_duration: int | None

    _path: ClassVar[str] = f"{BASE_PATH}/daily"
    _page_size: ClassVar[int] = 28

    @classmethod
    def get(
        cls,
        end: date | str | None = None,
        days: int = 1,
        *,
        client: http.Client | None = None,
    ) -> list["DailyStress"]:
        client = client or http.client
        end = format_end_date(end)
        # paginate for more than 28 days
        if days > cls._page_size:
            page = cls.get(end, cls._page_size, client=client)
            if page:
                page = (
                    cls.get(
                        end - timedelta(days=cls._page_size),
                        days - cls._page_size,
                        client=client,
                    )
                    + page
                )
            return page
        start = end - timedelta(days=days - 1)
        path = f"{cls._path}/{start}/{end}"
        daily_stress = client.connectapi(path)
        daily_stress = [
            camel_to_snake_dict(day | day.pop("values"))
            for day in daily_stress
        ]
        return [cls(**day) for day in daily_stress]


@dataclass(frozen=True)
class WeeklyStress:
    calendar_date: date
    value: int

    _path: ClassVar[str] = f"{BASE_PATH}/weekly"
    _page_size: ClassVar[int] = 52

    @classmethod
    def get(
        cls,
        end: date | str | None = None,
        weeks: int = 1,
        *,
        client: http.Client | None = None,
    ) -> list["WeeklyStress"]:
        client = client or http.client
        end = format_end_date(end)
        # paginate for more than 52 weeks
        if weeks > cls._page_size:
            page = cls.get(end, cls._page_size, client=client)
            if page:
                page = (
                    cls.get(
                        end - timedelta(weeks=cls._page_size),
                        weeks - cls._page_size,
                        client=client,
                    )
                    + page
                )
            return page
        path = f"{cls._path}/{end}/{weeks}"
        weekly_stress = client.connectapi(path)
        weekly_stress = [camel_to_snake_dict(week) for week in weekly_stress]
        return [cls(**week) for week in weekly_stress]
