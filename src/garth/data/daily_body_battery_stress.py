from __future__ import annotations

from datetime import date, datetime
from functools import cached_property
from typing import Any, List

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date
from ._base import Data


@dataclass
class BodyBatteryReading:
    """Individual Body Battery reading."""

    timestamp: int
    status: str
    level: int
    version: float


@dataclass
class StressReading:
    """Individual stress reading."""

    timestamp: int
    stress_level: int


@dataclass
class DailyBodyBatteryStress(Data):
    """Complete daily Body Battery and stress data."""

    user_profile_pk: int
    calendar_date: str
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime
    max_stress_level: int
    avg_stress_level: int
    stress_chart_value_offset: int
    stress_chart_y_axis_origin: int
    stress_values_array: List[List[int]]
    body_battery_values_array: List[List[Any]]

    @cached_property
    def body_battery_readings(self) -> List[BodyBatteryReading]:
        """Convert body battery values array to structured readings."""
        readings = []
        for values in self.body_battery_values_array or []:
            # Each reading requires 4 values: timestamp, status, level, version
            if len(values) >= 4:
                readings.append(
                    BodyBatteryReading(
                        timestamp=values[0],
                        status=values[1],
                        level=values[2],
                        version=values[3],
                    )
                )
        return readings

    @property
    def stress_readings(self) -> List[StressReading]:
        """Convert stress values array to structured readings."""
        readings = []
        for values in self.stress_values_array or []:
            if len(values) >= 2:
                readings.append(
                    StressReading(timestamp=values[0], stress_level=values[1])
                )
        return readings

    @property
    def current_body_battery(self) -> int | None:
        """Get the latest Body Battery level."""
        readings = self.body_battery_readings
        return readings[-1].level if readings else None

    @property
    def max_body_battery(self) -> int | None:
        """Get the maximum Body Battery level for the day."""
        readings = self.body_battery_readings
        return max(reading.level for reading in readings) if readings else None

    @property
    def min_body_battery(self) -> int | None:
        """Get the minimum Body Battery level for the day."""
        readings = self.body_battery_readings
        return min(reading.level for reading in readings) if readings else None

    @property
    def body_battery_change(self) -> int | None:
        """Calculate the Body Battery change for the day."""
        readings = self.body_battery_readings
        if not readings or len(readings) < 2:
            return None
        return readings[-1].level - readings[0].level

    @classmethod
    def get(
        cls,
        day: date | str,
        *,
        client: http.Client | None = None,
    ) -> Self | None:
        """Get complete Body Battery and stress data for a specific date."""
        client = client or http.client
        date_str = format_end_date(day)

        path = f"/wellness-service/wellness/dailyStress/{date_str}"
        response = client.connectapi(path)

        if not isinstance(response, dict):
            return None

        snake_response = camel_to_snake_dict(response)
        return cls(**snake_response)