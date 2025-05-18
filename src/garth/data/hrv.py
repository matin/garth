from datetime import date, datetime

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict
from ._base import Data


@dataclass
class Baseline:
    low_upper: int
    balanced_low: int
    balanced_upper: int
    marker_value: float


@dataclass
class HRVSummary:
    calendar_date: date
    weekly_avg: int
    last_night_avg: int | None
    last_night_5_min_high: int
    baseline: Baseline
    status: str
    feedback_phrase: str
    create_time_stamp: datetime


@dataclass
class HRVReading:
    hrv_value: int
    reading_time_gmt: datetime
    reading_time_local: datetime


@dataclass
class HRVData(Data):
    user_profile_pk: int
    hrv_summary: HRVSummary
    hrv_readings: list[HRVReading]
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime
    sleep_start_timestamp_gmt: datetime
    sleep_end_timestamp_gmt: datetime
    sleep_start_timestamp_local: datetime
    sleep_end_timestamp_local: datetime

    @classmethod
    def get(
        cls, day: date | str, *, client: http.Client | None = None
    ) -> Self | None:
        client = client or http.client
        path = f"/hrv-service/hrv/{day}"
        hrv_data = client.connectapi(path)
        if not hrv_data:
            return None
        hrv_data = camel_to_snake_dict(hrv_data)
        assert isinstance(hrv_data, dict)
        return cls(**hrv_data)

    @classmethod
    def list(cls, *args, **kwargs) -> list[Self]:
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda d: d.hrv_summary.calendar_date)
