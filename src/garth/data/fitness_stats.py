from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date


@dataclass
class FitnessActivity:
    """Activity data from fitness stats with coaching information.

    This class retrieves activities with their adaptive coaching status,
    workout type, and training effects from the fitness stats service.

    Example:
        >>> activities = FitnessActivity.list("2026-01-15", days=7)
        >>> coaching = [a for a in activities if a.workout_type]
        >>> coaching[0].adaptive_coaching_workout_status
        'COMPLETED_VIA_ACTIVITY'
    """

    activity_id: int
    start_local: datetime
    activity_type: str
    workout_group_enumerator: int
    aerobic_training_effect: float | None = None
    parent_id: int | None = None
    workout_type: str | None = None
    adaptive_coaching_workout_status: str | None = None
    multisport_set: Any | None = None

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        days: int = 7,
        *,
        client: http.Client | None = None,
    ) -> list[Self]:
        """List activities with fitness stats and coaching data.

        Args:
            end: End date for the range (default: today)
            days: Number of days to look back (default: 7)
            client: Optional HTTP client (uses default if not provided)

        Returns:
            List of FitnessActivity instances
        """
        client = client or http.client
        end_date = format_end_date(end)
        start_date = end_date - date.resolution * (days - 1)

        path = "/fitnessstats-service/activity/all"
        params = {
            "startDate": str(start_date),
            "endDate": str(end_date),
            "standardizedUnits": "true",
            "metric": [
                "activityType",
                "workoutType",
                "aerobicTrainingEffect",
                "adaptiveCoachingWorkoutStatus",
                "parentId",
                "workoutGroupEnumerator",
            ],
        }
        data = client.connectapi(path, params=params)
        assert isinstance(data, list), (
            f"Expected list from {path}, got {type(data).__name__}"
        )

        activities = []
        for item in data:
            item = camel_to_snake_dict(item)
            activities.append(cls(**item))

        return sorted(activities, key=lambda x: x.start_local)
