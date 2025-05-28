from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, List

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import format_end_date
from .daily_body_battery_stress import BodyBatteryReading


@dataclass
class BodyBatteryEvent:
    """Body Battery event data."""

    event_type: str
    event_start_time_gmt: datetime
    timezone_offset: int
    duration_in_milliseconds: int
    body_battery_impact: int
    feedback_type: str
    short_feedback: str


@dataclass
class BodyBatteryData:
    """Legacy Body Battery events data (sleep events only)."""

    event: BodyBatteryEvent | None = None
    activity_name: str | None = None
    activity_type: str | None = None
    activity_id: str | None = None
    average_stress: float | None = None
    stress_values_array: List[List[int]] | None = None
    body_battery_values_array: List[List[Any]] | None = None

    @property
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
    def current_level(self) -> int | None:
        """Get the latest Body Battery level."""
        readings = self.body_battery_readings
        return readings[-1].level if readings else None

    @property
    def max_level(self) -> int | None:
        """Get the maximum Body Battery level for the day."""
        readings = self.body_battery_readings
        return max(reading.level for reading in readings) if readings else None

    @property
    def min_level(self) -> int | None:
        """Get the minimum Body Battery level for the day."""
        readings = self.body_battery_readings
        return min(reading.level for reading in readings) if readings else None

    @classmethod
    def get(
        cls,
        date_str: str | date | None = None,
        *,
        client: http.Client | None = None,
    ) -> List[Self]:
        """Get Body Battery events for a specific date."""
        client = client or http.client
        date_str = format_end_date(date_str)

        path = f"/wellness-service/wellness/bodyBattery/events/{date_str}"
        response = client.connectapi(path)

        if not isinstance(response, list):
            return []

        events = []
        for item in response:
            # Parse event data
            event_data = item.get("event")
            event = None
            if event_data:
                event = BodyBatteryEvent(
                    event_type=event_data.get("eventType", ""),
                    event_start_time_gmt=datetime.fromisoformat(
                        event_data.get("eventStartTimeGmt", "").replace(
                            "Z", "+00:00"
                        )
                    ),
                    timezone_offset=event_data.get("timezoneOffset", 0),
                    duration_in_milliseconds=event_data.get(
                        "durationInMilliseconds", 0
                    ),
                    body_battery_impact=event_data.get("bodyBatteryImpact", 0),
                    feedback_type=event_data.get("feedbackType", ""),
                    short_feedback=event_data.get("shortFeedback", ""),
                )

            events.append(
                cls(
                    event=event,
                    activity_name=item.get("activityName"),
                    activity_type=item.get("activityType"),
                    activity_id=item.get("activityId"),
                    average_stress=item.get("averageStress"),
                    stress_values_array=item.get("stressValuesArray"),
                    body_battery_values_array=item.get(
                        "bodyBatteryValuesArray"
                    ),
                )
            )

        return events

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        period: int = 1,
        *,
        client: http.Client | None = None,
    ) -> List[Self]:
        """Get Body Battery data for multiple days."""
        end_date = format_end_date(end)
        all_events = []

        for i in range(period):
            date_to_fetch = end_date - timedelta(days=i)
            events = cls.get(date_to_fetch, client=client)
            all_events.extend(events)

        return all_events