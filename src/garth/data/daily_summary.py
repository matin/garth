from datetime import date

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict
from ._base import Data


@dataclass
class DailySummary(Data):
    user_profile_id: int
    calendar_date: date
    total_kilocalories: int | None = None
    active_kilocalories: int | None = None
    total_steps: int | None = None
    total_distance_meters: int | None = None
    min_heart_rate: int | None = None
    max_heart_rate: int | None = None
    min_avg_heart_rate: int | None = None
    max_avg_heart_rate: int | None = None
    resting_heart_rate: int | None = None
    last_seven_days_avg_resting_heart_rate: int | None = None
    max_stress_level: int | None = None
    average_stress_level: int | None = None
    stress_qualifier: str | None = None
    body_battery_at_wake_time: int | None = None
    body_battery_highest_value: int | None = None
    body_battery_lowest_value: int | None = None
    moderate_intensity_minutes: int | None = None
    vigorous_intensity_minutes: int | None = None
    active_seconds: int | None = None
    highly_active_seconds: int | None = None
    sedentary_seconds: int | None = None
    sleeping_seconds: int | None = None
    floors_ascended: float | None = None
    floors_descended: float | None = None
    average_spo_2: int | None = None
    lowest_spo_2: int | None = None
    avg_waking_respiration_value: int | None = None
    highest_respiration_value: int | None = None
    lowest_respiration_value: int | None = None

    @classmethod
    def get(
        cls, day: date | str, *, client: http.Client | None = None
    ) -> Self | None:
        client = client or http.client
        path = f"/usersummary-service/usersummary/daily/?calendarDate={day}"
        daily_summary = client.connectapi(path)
        if not daily_summary:
            return None
        daily_summary = camel_to_snake_dict(daily_summary)
        assert isinstance(daily_summary, dict)
        return cls(**daily_summary)
