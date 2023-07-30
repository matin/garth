from datetime import date, datetime, timedelta
from typing import ClassVar

from pydantic.dataclasses import dataclass

from .. import http
from ..utils import camel_to_snake_dict, format_end_date


@dataclass(frozen=True)
class HRVBaseline:
    low_upper: int
    balanced_low: int
    balanced_upper: int
    marker_value: float


@dataclass(frozen=True)
class DailyHRV:
    calendar_date: date
    weekly_avg: int
    last_night_avg: int
    last_night_5_min_high: int
    baseline: HRVBaseline
    status: str
    feedback_phrase: str
    create_time_stamp: datetime

    _path: ClassVar[str] = "/hrv-service/hrv/daily/{start}/{end}"

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        period: int = 28,
        *,
        client: http.Client | None = None,
    ) -> list["DailyHRV"]:
        client = client or http.client
        end = format_end_date(end)
        start = end - timedelta(days=period - 1)
        path = cls._path.format(start=start, end=end)
        daily_hrv = client.connectapi(path)
        daily_hrv = camel_to_snake_dict(daily_hrv)["hrv_summaries"]
        return [cls(**hrv) for hrv in daily_hrv]
