from datetime import date, datetime
from typing import ClassVar

from pydantic.dataclasses import dataclass

from .._base import Stats


@dataclass
class MonthlyTrainingStatus(Stats):
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
        "/mobile-gateway/usersummary/trainingstatus/monthly/{start}/{end}"
    )
    _page_size: ClassVar[int] = 12

    @classmethod
    def _parse_response(cls, response):
        """Extract training data from the monthly API response structure."""
        if not isinstance(response, dict):
            return []

        data_section = response.get("monthlyTrainingStatus", {})
        if not isinstance(data_section, dict):
            return []

        payload = data_section.get("payload", {})
        if not isinstance(payload, dict):
            return []

        report_data = payload.get("reportData", {})
        if not isinstance(report_data, dict):
            return []

        # Get the first device's data (assumes single device for now)
        for device_data in report_data.values():
            if isinstance(device_data, list):
                result = []
                for entry in device_data:
                    if isinstance(entry, dict):
                        # Flatten the acuteTrainingLoadDTO data
                        acute_load = entry.pop("acuteTrainingLoadDTO", {})
                        if isinstance(acute_load, dict):
                            entry.update(acute_load)
                        result.append(entry)
                return result

        return []
