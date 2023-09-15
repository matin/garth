from datetime import date, datetime
from typing import List, Optional, Union

from pydantic.dataclasses import dataclass

from .. import http
from ..utils import camel_to_snake_dict


@dataclass(frozen=True)
class Baseline:
    low_upper: int
    balanced_low: int
    balanced_upper: int
    marker_value: float


@dataclass(frozen=True)
class HRVSummary:
    calendar_date: date
    weekly_avg: int
    last_night_avg: int
    last_night_5_min_high: int
    baseline: Baseline
    status: str
    feedback_phrase: str
    create_time_stamp: datetime


@dataclass(frozen=True)
class HRVReading:
    hrv_value: int
    reading_time_gmt: datetime
    reading_time_local: datetime


@dataclass(frozen=True)
class HRVData:
    user_profile_pk: int
    hrv_summary: HRVSummary
    hrv_readings: List[HRVReading]
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
        cls, day: Union[date, str], *, client: Optional[http.Client] = None
    ) -> Optional["HRVData"]:
        client = client or http.client
        path = f"/hrv-service/hrv/{day}"
        hrv_data = client.connectapi(path)
        if not hrv_data:
            return None
        hrv_data = camel_to_snake_dict(hrv_data)
        assert isinstance(hrv_data, dict)
        return cls(**hrv_data)
