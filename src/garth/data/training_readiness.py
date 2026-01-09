from datetime import date, datetime
from typing import Any, cast

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date
from ._base import Data


@dataclass
class TrainingReadinessData(Data):
    user_profile_pk: int
    calendar_date: date
    timestamp: datetime
    timestamp_local: datetime
    device_id: int
    level: str
    feedback_long: str
    feedback_short: str
    score: int
    sleep_score: int | None
    sleep_score_factor_percent: int
    sleep_score_factor_feedback: str
    recovery_time: float
    recovery_time_factor_percent: int
    recovery_time_factor_feedback: str
    acwr_factor_percent: int
    acwr_factor_feedback: str
    acute_load: int
    stress_history_factor_percent: int
    stress_history_factor_feedback: str
    hrv_factor_percent: int
    hrv_factor_feedback: str
    hrv_weekly_average: int
    sleep_history_factor_percent: int
    sleep_history_factor_feedback: str
    valid_sleep: bool
    input_context: str | None
    primary_activity_tracker: bool
    recovery_time_change_phrase: str | None = None

    @classmethod
    def get(
        cls,
        day: date | str | None = None,
        *,
        client: http.Client | None = None,
    ) -> list[Self] | None:
        client = client or http.client
        day = format_end_date(day)
        path = f"/metrics-service/metrics/trainingreadiness/{day}"
        raw_data = client.connectapi(path)

        if not raw_data:
            return None

        data = cast(list[dict[str, Any]], raw_data)
        return [cls(**camel_to_snake_dict(entry)) for entry in data]

    @classmethod
    def list(cls, *args, **kwargs) -> list[Self]:
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda d: (d.calendar_date, d.timestamp))
