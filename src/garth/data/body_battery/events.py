import logging
from datetime import date, datetime
from typing import Any

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from ... import http
from ...utils import format_end_date
from .._base import Data
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
class BodyBatteryData(Data):
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
                # Parse event data with validation
                event_data = item.get("event")

                # Validate event_data exists before accessing properties
                if event_data is None:
                    logging.warning(f"Missing event data in item: {item}")
                    event = None
                else:
                    # Validate and parse datetime with explicit error handling
                    event_start_time_str = event_data.get("eventStartTimeGmt")
                    if not event_start_time_str:
                        logging.error(
                            f"Missing eventStartTimeGmt in event data: "
                            f"{event_data}"
                        )
                        raise ValueError(
                            "eventStartTimeGmt is required but missing"
                        )

                    try:
                        event_start_time_gmt = datetime.fromisoformat(
                            event_start_time_str.replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError) as e:
                        logging.error(
                            f"Invalid datetime format "
                            f"'{event_start_time_str}': {e}"
                        )
                        raise ValueError(
                            f"Invalid eventStartTimeGmt format: "
                            f"{event_start_time_str}"
                        ) from e

                    # Validate numeric fields
                    timezone_offset = event_data.get("timezoneOffset", 0)
                    if not isinstance(timezone_offset, (int, float)):
                        logging.warning(
                            f"Invalid timezone_offset type: "
                            f"{type(timezone_offset)}, using 0"
                        )
                        timezone_offset = 0

                    duration_ms = event_data.get("durationInMilliseconds", 0)
                    if not isinstance(duration_ms, (int, float)):
                        logging.warning(
                            f"Invalid durationInMilliseconds type: "
                            f"{type(duration_ms)}, using 0"
                        )
                        duration_ms = 0

                    battery_impact = event_data.get("bodyBatteryImpact", 0)
                    if not isinstance(battery_impact, (int, float)):
                        logging.warning(
                            f"Invalid bodyBatteryImpact type: "
                            f"{type(battery_impact)}, using 0"
                        )
                        battery_impact = 0

                    event = BodyBatteryEvent(
                        event_type=event_data.get("eventType", ""),
                        event_start_time_gmt=event_start_time_gmt,
                        timezone_offset=int(timezone_offset),
                        duration_in_milliseconds=int(duration_ms),
                        body_battery_impact=int(battery_impact),
                        feedback_type=event_data.get("feedbackType", ""),
                        short_feedback=event_data.get("shortFeedback", ""),
                    )

                # Validate data arrays
                stress_values = item.get("stressValuesArray")
                if stress_values is not None and not isinstance(
                    stress_values, list
                ):
                    logging.warning(
                        f"Invalid stressValuesArray type: "
                        f"{type(stress_values)}, using None"
                    )
                    stress_values = None

                battery_values = item.get("bodyBatteryValuesArray")
                if battery_values is not None and not isinstance(
                    battery_values, list
                ):
                    logging.warning(
                        f"Invalid bodyBatteryValuesArray type: "
                        f"{type(battery_values)}, using None"
                    )
                    battery_values = None

                # Validate average_stress
                avg_stress = item.get("averageStress")
                if avg_stress is not None and not isinstance(
                    avg_stress, (int, float)
                ):
                    logging.warning(
                        f"Invalid averageStress type: "
                        f"{type(avg_stress)}, using None"
                    )
                    avg_stress = None

                events.append(
                    cls(
                        event=event,
                        activity_name=item.get("activityName"),
                        activity_type=item.get("activityType"),
                        activity_id=item.get("activityId"),
                        average_stress=avg_stress,
                        stress_values_array=stress_values,
                        body_battery_values_array=battery_values,
                    )
                )

            except ValueError as e:
                # Re-raise validation errors with context
                logging.error(
                    f"Data validation error for Body Battery event item "
                    f"{item}: {e}"
                )
                continue
            except Exception as e:
                # Log unexpected errors with full context
                logging.error(
                    f"Unexpected error parsing Body Battery event item "
                    f"{item}: {e}",
                    exc_info=True,
                )
                continue

        # Log summary of data quality issues
        total_items = len(response)
        parsed_events = len(events)
        if parsed_events < total_items:
            skipped = total_items - parsed_events
            logging.info(
                f"Body Battery events parsing: {parsed_events}/{total_items} "
                f"successful, {skipped} skipped due to data issues"
            )

        return events
