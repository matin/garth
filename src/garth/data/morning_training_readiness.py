from datetime import date, datetime
from typing import Any, cast

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date
from ._base import Data


@dataclass
class MorningTrainingReadinessData(Data):
    user_profile_pk: int
    calendar_date: date
    score: int
    recovery_time: float
    recovery_time_factor_feedback: str
    recovery_time_factor_percent: int
    acute_load: int
    hrv_factor_feedback: str
    hrv_factor_percent: int
    hrv_weekly_average: int
    sleep_history_factor_feedback: str
    sleep_history_factor_percent: int
    sleep_score: int
    sleep_score_factor_feedback: str
    sleep_score_factor_percent: int
    stress_history_factor_feedback: str
    stress_history_factor_percent: int
    feedback_short: str
    timestamp: datetime
    timestamp_local: datetime

    @classmethod
    def get(
        cls,
        day: date | str | None = None,
        *,
        client: http.Client | None = None,
    ) -> Self | None:
        client = client or http.client
        day = format_end_date(day)
        path = f"/metrics-service/metrics/trainingreadiness/{day}"
        raw_data = client.connectapi(path)

        if not raw_data:
            return None  # pragma: no cover

        data = cast(list[dict[str, Any]], raw_data)

        # Extract only the part with morning readiness
        morning_readiness_data = next(
            (
                entry
                for entry in data
                if entry.get("inputContext") == "AFTER_WAKEUP_RESET"
            ),
            None,
        )

        if not morning_readiness_data:
            return None  # pragma: no cover

        morning_readiness_data = camel_to_snake_dict(morning_readiness_data)
        return cls(**morning_readiness_data)

    @classmethod
    def list(cls, *args, **kwargs) -> list[Self]:
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda d: d.calendar_date)
