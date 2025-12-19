from typing import Any

from pydantic.dataclasses import dataclass


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


def parse_body_battery_readings(
    body_battery_values_array: list[list[Any]] | None,
) -> list[BodyBatteryReading]:
    """Convert body battery values array to structured readings."""
    readings = []
    for values in body_battery_values_array or []:
        # Each reading requires 4 values: timestamp, status, level, version
        if len(values) >= 4:
            timestamp, status, level, version, *_ = values
            if level is None or status is None:
                continue
            readings.append(
                BodyBatteryReading(
                    timestamp=timestamp,
                    status=status,
                    level=level,
                    version=version,
                )
            )
    # Sort readings by timestamp to ensure chronological order
    return sorted(readings, key=lambda reading: reading.timestamp)


def parse_stress_readings(
    stress_values_array: list[list[int]] | None,
) -> list[StressReading]:
    """Convert stress values array to structured readings."""
    readings = []
    for values in stress_values_array or []:
        # Each reading requires 2 values: timestamp, stress_level
        if len(values) >= 2:
            readings.append(
                StressReading(timestamp=values[0], stress_level=values[1])
            )
    # Sort readings by timestamp to ensure chronological order
    return sorted(readings, key=lambda reading: reading.timestamp)
