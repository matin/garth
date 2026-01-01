from datetime import date, datetime

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, get_localized_datetime
from ._base import Data


@dataclass
class Score:
    qualifier_key: str
    optimal_start: float | None = None
    optimal_end: float | None = None
    value: int | None = None
    ideal_start_in_seconds: float | None = None
    ideal_end_in_seconds: float | None = None


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
    unmeasurable_sleep_seconds: int | None = None
    deep_sleep_seconds: int | None = None
    light_sleep_seconds: int | None = None
    rem_sleep_seconds: int | None = None
    awake_sleep_seconds: int | None = None
    sleep_from_device: bool | None = None
    sleep_version: int | None = None
    awake_count: int | None = None
    sleep_scores: SleepScores | None = None
    auto_sleep_start_timestamp_gmt: int | None = None
    auto_sleep_end_timestamp_gmt: int | None = None
    sleep_quality_type_pk: int | None = None
    sleep_result_type_pk: int | None = None
    average_sp_o2_value: float | None = None
    lowest_sp_o2_value: int | None = None
    highest_sp_o2_value: int | None = None
    average_sp_o2_hr_sleep: float | None = None
    average_respiration_value: float | None = None
    lowest_respiration_value: float | None = None
    highest_respiration_value: float | None = None
    avg_sleep_stress: float | None = None
    age_group: str | None = None
    sleep_score_feedback: str | None = None
    sleep_score_insight: str | None = None

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
    sleep_movement: list[SleepMovement] | None = None

    @classmethod
    def get(
        cls,
        day: date | str,
        *,
        buffer_minutes: int = 60,
        client: http.Client | None = None,
    ) -> Self | None:
        client = client or http.client
        path = (
            f"/wellness-service/wellness/dailySleepData/{client.username}?"
            f"nonSleepBufferMinutes={buffer_minutes}&date={day}"
        )
        sleep_data = client.connectapi(path)
        assert sleep_data
        assert isinstance(sleep_data, dict), (
            f"Expected dict from {path}, got {type(sleep_data).__name__}"
        )
        sleep_data = camel_to_snake_dict(sleep_data)
        return (
            cls(**sleep_data) if sleep_data["daily_sleep_dto"]["id"] else None
        )

    @classmethod
    def list(cls, *args, **kwargs) -> list[Self]:
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda x: x.daily_sleep_dto.calendar_date)
