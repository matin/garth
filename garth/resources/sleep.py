from datetime import date
from typing import ClassVar

from pydantic.dataclasses import dataclass

from .. import http
from ..stats import Stats
from ..utils import camel_to_snake_dict


@dataclass(frozen=True)
class DailySleep(Stats):
    calendar_date: date

    _path: ClassVar[str] = "/wellness-service/stats/daily/sleep/score"
    _page_size: ClassVar[int] = 28


@dataclass(frozen=True)
class Score:
    qualifier_key: str
    optimal_start: float | None = None
    optimal_end: float | None = None
    value: int | None = None
    ideal_start_in_seconds: float | None = None
    ideal_end_in_seconds: float | None = None


@dataclass(frozen=True)
class SleepScores:
    total_duration: Score
    stress: Score
    awake_count: Score
    overall: Score
    rem_percentage: Score
    restlessness: Score
    light_percentage: Score
    deep_percentage: Score


@dataclass(frozen=True)
class DailySleepDTO:
    id: int
    user_profile_pk: int
    calendar_date: str
    sleep_time_seconds: int
    nap_time_seconds: int
    sleep_window_confirmed: bool
    sleep_window_confirmation_type: str
    sleep_start_timestamp_gmt: int
    sleep_end_timestamp_gmt: int
    sleep_start_timestamp_local: int
    sleep_end_timestamp_local: int
    auto_sleep_start_timestamp_gmt: int | None
    auto_sleep_end_timestamp_gmt: int | None
    sleep_quality_type_pk: int | None
    sleep_result_type_pk: int | None
    unmeasurable_sleep_seconds: int
    deep_sleep_seconds: int
    light_sleep_seconds: int
    rem_sleep_seconds: int
    awake_sleep_seconds: int
    device_rem_capable: bool
    retro: bool
    sleep_from_device: bool
    average_sp_o2_value: float
    lowest_sp_o2_value: int
    highest_sp_o2_value: int
    average_sp_o2_hr_sleep: float
    average_respiration_value: float
    lowest_respiration_value: float
    highest_respiration_value: float
    awake_count: int
    avg_sleep_stress: float
    age_group: str
    sleep_score_feedback: str
    sleep_score_insight: str
    sleep_scores: SleepScores
    sleep_version: int


@dataclass(frozen=True)
class SleepMovement:
    start_gmt: str
    end_gmt: str
    activity_level: float


@dataclass(frozen=True)
class SleepData:
    daily_sleep_dto: DailySleepDTO
    sleep_movement: list[SleepMovement]

    @classmethod
    def get(cls, day: date | str, *, client: http.Client | None = None):
        client = client or http.client
        path = (
            f"/wellness-service/wellness/dailySleepData/{client.username}?"
            f"nonSleepBufferMinutes=60&date={day}"
        )
        sleep_data = client.connectapi(path)
        sleep_data = camel_to_snake_dict(sleep_data)
        return cls(**sleep_data)
