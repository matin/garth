from datetime import date, datetime
from functools import cached_property
from typing import Any

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from ... import http
from ...utils import camel_to_snake_dict, format_end_date
from .._base import Data
from .readings import (
    BodyBatteryReading,
    StressReading,
    parse_body_battery_readings,
    parse_stress_readings,
)


@dataclass
class DailyBodyBatteryStress(Data):
    """Complete daily Body Battery and stress data."""

    user_profile_pk: int
    calendar_date: date
    start_timestamp_gmt: datetime
    end_timestamp_gmt: datetime
    start_timestamp_local: datetime
    end_timestamp_local: datetime
    max_stress_level: int
    avg_stress_level: int
    stress_chart_value_offset: int
    stress_chart_y_axis_origin: int
    stress_values_array: list[list[int]]
    body_battery_values_array: list[list[Any]]

    @cached_property
    def body_battery_readings(self) -> list[BodyBatteryReading]:
        """Convert body battery values array to structured readings."""
        return parse_body_battery_readings(self.body_battery_values_array)

    @property
    def stress_readings(self) -> list[StressReading]:
        """Convert stress values array to structured readings."""
        return parse_stress_readings(self.stress_values_array)

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
        day: date | str | None = None,
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
