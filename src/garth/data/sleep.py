from datetime import date, datetime
from typing import Optional, Union

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, get_localized_datetime
from ._base import Data


@dataclass
class Score:
    qualifier_key: str
    optimal_start: Optional[float] = None
    optimal_end: Optional[float] = None
    value: Optional[int] = None
    ideal_start_in_seconds: Optional[float] = None
    ideal_end_in_seconds: Optional[float] = None


@dataclass
class SleepScores:
    total_duration: Score
    stress: Score
    awake_count: Score
    overall: Score
    rem_percentage: Score
    restlessness: Score
    light_percentage: Score
    deep_percentage: Score


@dataclass
class DailySleepDTO:
    id: int
    user_profile_pk: int
    calendar_date: date
    sleep_time_seconds: int
    nap_time_seconds: int
    sleep_window_confirmed: bool
    sleep_window_confirmation_type: str
    sleep_start_timestamp_gmt: int
    sleep_end_timestamp_gmt: int
    sleep_start_timestamp_local: int
    sleep_end_timestamp_local: int
    device_rem_capable: bool
    retro: bool
    unmeasurable_sleep_seconds: Optional[int] = None
    deep_sleep_seconds: Optional[int] = None
    light_sleep_seconds: Optional[int] = None
    rem_sleep_seconds: Optional[int] = None
    awake_sleep_seconds: Optional[int] = None
    sleep_from_device: Optional[bool] = None
    sleep_version: Optional[int] = None
    awake_count: Optional[int] = None
    sleep_scores: Optional[SleepScores] = None
    auto_sleep_start_timestamp_gmt: Optional[int] = None
    auto_sleep_end_timestamp_gmt: Optional[int] = None
    sleep_quality_type_pk: Optional[int] = None
    sleep_result_type_pk: Optional[int] = None
    average_sp_o2_value: Optional[float] = None
    lowest_sp_o2_value: Optional[int] = None
    highest_sp_o2_value: Optional[int] = None
    average_sp_o2_hr_sleep: Optional[float] = None
    average_respiration_value: Optional[float] = None
    lowest_respiration_value: Optional[float] = None
    highest_respiration_value: Optional[float] = None
    avg_sleep_stress: Optional[float] = None
    age_group: Optional[str] = None
    sleep_score_feedback: Optional[str] = None
    sleep_score_insight: Optional[str] = None

    @property
    def sleep_start(self) -> datetime:
        return get_localized_datetime(
            self.sleep_start_timestamp_gmt, self.sleep_start_timestamp_local
        )

    @property
    def sleep_end(self) -> datetime:
        return get_localized_datetime(
            self.sleep_end_timestamp_gmt, self.sleep_end_timestamp_local
        )


@dataclass
class SleepMovement:
    start_gmt: datetime
    end_gmt: datetime
    activity_level: float


@dataclass
class SleepData(Data):
    daily_sleep_dto: DailySleepDTO
    sleep_movement: Optional[list[SleepMovement]] = None

    @classmethod
    def get(
        cls,
        day: Union[date, str],
        *,
        buffer_minutes: int = 60,
        client: Optional[http.Client] = None,
    ) -> Optional[Self]:
        client = client or http.client
        path = (
            f"/wellness-service/wellness/dailySleepData/{client.username}?"
            f"nonSleepBufferMinutes={buffer_minutes}&date={day}"
        )
        sleep_data = client.connectapi(path)
        assert sleep_data
        sleep_data = camel_to_snake_dict(sleep_data)
        assert isinstance(sleep_data, dict)
        return (
            cls(**sleep_data) if sleep_data["daily_sleep_dto"]["id"] else None
        )

    @classmethod
    def list(cls, *args, **kwargs) -> list[Self]:
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda x: x.daily_sleep_dto.calendar_date)
