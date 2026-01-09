from __future__ import annotations

import builtins
from datetime import date, datetime
from typing import Any

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date
from ._base import Data


@dataclass
class SleepScore:
    qualifier_key: str
    value: int | None = None
    optimal_start: float | None = None
    optimal_end: float | None = None
    ideal_start_in_seconds: float | None = None
    ideal_end_in_seconds: float | None = None


@dataclass
class SleepScores:
    total_duration: SleepScore
    stress: SleepScore
    awake_count: SleepScore
    overall: SleepScore
    rem_percentage: SleepScore
    restlessness: SleepScore
    light_percentage: SleepScore
    deep_percentage: SleepScore


@dataclass
class SleepNeed:
    user_profile_pk: int
    calendar_date: date
    device_id: int
    timestamp_gmt: datetime
    baseline: int
    actual: int
    feedback: str
    training_feedback: str
    sleep_history_adjustment: str
    hrv_adjustment: str
    nap_adjustment: str
    displayed_for_the_day: bool
    preferred_activity_tracker: bool


@dataclass
class SleepDTO:
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
    sleep_scores: SleepScores | None = None
    sleep_need: SleepNeed | None = None
    next_sleep_need: SleepNeed | None = None
    unmeasurable_sleep_seconds: int | None = None
    deep_sleep_seconds: int | None = None
    light_sleep_seconds: int | None = None
    rem_sleep_seconds: int | None = None
    awake_sleep_seconds: int | None = None
    sleep_from_device: bool | None = None
    sleep_version: int | None = None
    awake_count: int | None = None
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
    sleep_score_personalized_insight: str | None = None


@dataclass
class SpO2SleepSummary:
    user_profile_pk: int
    device_id: int
    sleep_measurement_start_gmt: datetime
    sleep_measurement_end_gmt: datetime
    average_sp_o2: float | None = None
    average_sp_o2_hr: float | None = None
    lowest_sp_o2: int | None = None
    alert_threshold_value: int | None = None
    number_of_events_below_threshold: int | None = None
    duration_of_events_below_threshold: int | None = None


@dataclass
class DailySleepData(Data):
    daily_sleep_dto: SleepDTO
    rem_sleep_data: bool
    wellness_sp_o2_sleep_summary_dto: SpO2SleepSummary | None = None
    sleep_movement: builtins.list[Any] | None = None
    sleep_levels: builtins.list[Any] | None = None
    skin_temp_data_exists: bool | None = None
    avg_skin_temp_deviation_c: float | None = None
    avg_skin_temp_deviation_f: float | None = None
    body_battery_change: int | None = None
    skin_temp_calibration_days: int | None = None
    resting_heart_rate: int | None = None

    @classmethod
    def get(
        cls,
        day: date | str | None = None,
        *,
        client: http.Client | None = None,
    ) -> Self | None:
        client = client or http.client
        day = format_end_date(day)
        path = f"/sleep-service/sleep/dailySleepData?date={day}"
        data = client.connectapi(path)
        assert isinstance(data, dict)
        data = camel_to_snake_dict(data)

        if not data["daily_sleep_dto"].get("id"):
            return None

        return cls(**data)

    @classmethod
    def list(cls, *args, **kwargs) -> list[Self]:
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda x: x.daily_sleep_dto.calendar_date)

    @property
    def sleep_need_minutes(self) -> int | None:
        """Get the sleep need in minutes for this day."""
        need = self.daily_sleep_dto.sleep_need
        return need.actual if need else None

    @property
    def next_sleep_need_minutes(self) -> int | None:
        """Get the sleep need in minutes for the next day."""
        need = self.daily_sleep_dto.next_sleep_need
        return need.actual if need else None
