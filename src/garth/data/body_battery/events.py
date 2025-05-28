from datetime import date, datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import logging

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from ... import http
from ...utils import date_range, format_end_date
from .readings import BodyBatteryReading, parse_body_battery_readings

MAX_WORKERS = 10


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
    stress_values_array: list[list[int]] | None = None
    body_battery_values_array: list[list[Any]] | None = None

    @property
    def body_battery_readings(self) -> list[BodyBatteryReading]:
        """Convert body battery values array to structured readings."""
        return parse_body_battery_readings(self.body_battery_values_array)

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
    ) -> list[Self]:
        """Get Body Battery events for a specific date."""
        client = client or http.client
        date_str = format_end_date(date_str)

        path = f"/wellness-service/wellness/bodyBattery/events/{date_str}"
        try:
            response = client.connectapi(path)
        except Exception as e:
            logging.warning(f"Failed to fetch Body Battery events: {e}")
            return []

        if not isinstance(response, list):
            return []

        events = []
        for item in response:
            try:
                # Parse event data
                event_data = item.get("event")
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
            except Exception as e:
                logging.warning(f"Failed to parse Body Battery event: {e}")
                continue

        return events

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        days: int = 1,
        *,
        client: http.Client | None = None,
        max_workers: int = MAX_WORKERS,
    ) -> list[Self]:
        """Get Body Battery data for multiple days."""
        client = client or http.client
        end = format_end_date(end)

        def fetch_date(date_):
            events = cls.get(date_, client=client)
            return events if events else []

        dates = date_range(end, days)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            all_events_lists = list(executor.map(fetch_date, dates))
            all_events = []
            for events_list in all_events_lists:
                all_events.extend(events_list)

        return all_events
