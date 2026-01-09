from __future__ import annotations

import builtins
from datetime import date, datetime, timezone

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date
from ._base import Data


@dataclass
class HeartRateReading:
    """A single heart rate reading with timestamp and value."""

    timestamp: datetime
    heart_rate: int


@dataclass
class DailyHeartRate(Data):
    """Daily heart rate data from Garmin Connect.

    Contains resting heart rate, min/max values, and time-series readings
    throughout the day.

    Example:
        >>> hr = DailyHeartRate.get("2024-01-15")
        >>> hr.resting_heart_rate
        52
        >>> hr.max_heart_rate
        145
        >>> len(hr.readings)
        720
    """

    user_profile_pk: int
    calendar_date: date
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime
    max_heart_rate: int
    min_heart_rate: int
    resting_heart_rate: int
    last_seven_days_avg_resting_heart_rate: int
    heart_rate_values: builtins.list[builtins.list[int | None]]
    heart_rate_value_descriptors: builtins.list[dict] | None = None

    @property
    def readings(self) -> builtins.list[HeartRateReading]:
        """Convert raw heart rate values to HeartRateReading objects.

        Filters out readings where heart rate is None.
        """
        return [
            HeartRateReading(
                timestamp=datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
                heart_rate=hr,
            )
            for ts, hr in self.heart_rate_values
            if ts is not None and hr is not None
        ]

    @classmethod
    def get(
        cls,
        day: date | str | None = None,
        *,
        client: http.Client | None = None,
    ) -> Self | None:
        client = client or http.client
        day = format_end_date(day)
        path = f"/wellness-service/wellness/dailyHeartRate/?date={day}"
        hr_data = client.connectapi(path)
        if not hr_data:
            return None  # pragma: no cover
        assert isinstance(hr_data, dict), (
            f"Expected dict from {path}, got {type(hr_data).__name__}"
        )
        hr_data = camel_to_snake_dict(hr_data)
        return cls(**hr_data)

    @classmethod
    def list(cls, *args, **kwargs) -> builtins.list[Self]:
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda d: d.calendar_date)
