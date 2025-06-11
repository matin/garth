from datetime import date, timedelta
from typing import ClassVar

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date


BASE_PATH = "/mobile-gateway/usersummary/trainingstatus"


@dataclass
class TrainingStatus:
    calendar_date: date
    since_date: str | None = None
    weekly_training_load: int | None = None
    training_status: int | None = None
    timestamp: int | None = None
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

    _page_size: ClassVar[int]
    _path: ClassVar[str]
    _data_key: ClassVar[str]

    @classmethod
    def _extract_training_data(
        cls, response: dict, data_key: str
    ) -> list[dict]:
        """Extract training data from the nested API response structure."""
        if not isinstance(response, dict):
            return []

        data_section = response.get(data_key, {})
        if not isinstance(data_section, dict):
            return []

        payload = data_section.get("payload", {})
        if not isinstance(payload, dict):
            return []

        # For daily endpoint, get latest training status data
        if data_key == "mostRecentTrainingStatus":
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

        # For weekly/monthly endpoints, get report data
        report_data = payload.get("reportData", {})
        if not isinstance(report_data, dict):
            return []

        # Get the first device's data (assumes single device for now)
        for device_id, device_data in report_data.items():
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

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        period: int = 1,
        *,
        client: http.Client | None = None,
    ) -> list[Self]:
        client = client or http.client
        end = format_end_date(end)
        period_type = "days" if "daily" in cls._path else "weeks"

        if period > cls._page_size:
            page = cls.list(end, cls._page_size, client=client)
            if not page:
                return []
            page = (
                cls.list(
                    end - timedelta(**{period_type: cls._page_size}),
                    period - cls._page_size,
                    client=client,
                )
                + page
            )
            return page

        start = end - timedelta(**{period_type: period - 1})
        path = cls._path.format(start=start, end=end, period=period)
        response = client.connectapi(path)
        if not isinstance(response, dict):
            return []

        # Extract training data based on the endpoint type
        data_key = cls._data_key
        training_data = cls._extract_training_data(response, data_key)

        if not training_data:
            return []

        # Convert to snake_case and create instances
        training_data = [camel_to_snake_dict(item) for item in training_data]
        return [cls(**item) for item in training_data]


@dataclass
class DailyTrainingStatus(TrainingStatus):
    _path: ClassVar[str] = f"{BASE_PATH}/latest/{{end}}"
    _data_key: ClassVar[str] = "mostRecentTrainingStatus"
    _page_size: ClassVar[int] = 28


@dataclass
class WeeklyTrainingStatus(TrainingStatus):
    _path: ClassVar[str] = f"{BASE_PATH}/weekly/{{start}}/{{end}}"
    _data_key: ClassVar[str] = "weeklyTrainingStatus"
    _page_size: ClassVar[int] = 52


@dataclass
class MonthlyTrainingStatus(TrainingStatus):
    _path: ClassVar[str] = f"{BASE_PATH}/monthly/{{start}}/{{end}}"
    _data_key: ClassVar[str] = "monthlyTrainingStatus"
    _page_size: ClassVar[int] = 12
