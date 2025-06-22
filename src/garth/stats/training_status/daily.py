from datetime import date, datetime
from typing import ClassVar

from pydantic.dataclasses import dataclass

from .._base import Stats


@dataclass
class DailyTrainingStatus(Stats):
    since_date: date | None = None
    weekly_training_load: int | None = None
    training_status: int | None = None
    timestamp: datetime | None = None
    device_id: int | None = None
    load_tunnel_min: int | None = None
    load_tunnel_max: int | None = None
    load_level_trend: str | int | None = None
    sport: str | None = None
    sub_sport: str | None = None
    fitness_trend_sport: str | None = None
    fitness_trend: int | None = None
    training_status_feedback_phrase: str | None = None
    training_paused: bool | None = None
    primary_training_device: bool | None = None
    acwr_percent: int | None = None
    acwr_status: str | None = None
    acwr_status_feedback: str | None = None
    daily_training_load_acute: int | None = None
    max_training_load_chronic: float | None = None
    min_training_load_chronic: float | None = None
    daily_training_load_chronic: int | None = None
    daily_acute_chronic_workload_ratio: float | None = None

    _path: ClassVar[str] = (
        "/mobile-gateway/usersummary/trainingstatus/latest/{end}"
    )
    _page_size: ClassVar[int] = 28
    _period_type: ClassVar[str] = "days"

    @classmethod
    def _parse_response(cls, response):
        """Extract training data from the daily API response structure."""
        if not isinstance(response, dict):
            return []

        data_section = response.get("mostRecentTrainingStatus", {})
        if not isinstance(data_section, dict):
            return []

        payload = data_section.get("payload", {})
        if not isinstance(payload, dict):
            return []

        latest_data = payload.get("latestTrainingStatusData", {})
        if not isinstance(latest_data, dict):
            return []

        # Get the first device's data (assumes single device for now)
        for device_data in latest_data.values():
            if isinstance(device_data, dict):
                # Flatten the acuteTrainingLoadDTO data
                acute_load = device_data.pop("acuteTrainingLoadDTO", {})
                if isinstance(acute_load, dict):
                    device_data.update(acute_load)
                return [device_data]

        return []
