from __future__ import annotations

from datetime import datetime

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, remove_dto_suffix_from_dict


@dataclass
class ActivityType:
    type_id: int
    type_key: str
    parent_type_id: int | None = None
    is_hidden: bool | None = None
    restricted: bool | None = None
    trimmable: bool | None = None


@dataclass
class EventType:
    type_id: int
    type_key: str
    sort_order: int | None = None


@dataclass
class Summary:
    """Summary metrics for an activity.

    Most fields are optional since different activity types return different
    metrics. For example, running activities have cadence data while swimming
    activities have stroke data.
    """

    start_time_local: datetime | None = None
    start_time_gmt: datetime | None = None
    start_latitude: float | None = None
    start_longitude: float | None = None
    end_latitude: float | None = None
    end_longitude: float | None = None
    distance: float | None = None
    duration: float | None = None
    moving_duration: float | None = None
    elapsed_duration: float | None = None
    elevation_gain: float | None = None
    elevation_loss: float | None = None
    max_elevation: float | None = None
    min_elevation: float | None = None
    average_speed: float | None = None
    average_moving_speed: float | None = None
    max_speed: float | None = None
    calories: float | None = None
    bmr_calories: float | None = None
    average_hr: float | None = None
    max_hr: float | None = None
    min_hr: float | None = None
    average_run_cadence: float | None = None
    max_run_cadence: float | None = None
    average_temperature: float | None = None
    max_temperature: float | None = None
    min_temperature: float | None = None
    average_power: float | None = None
    max_power: float | None = None
    min_power: float | None = None
    normalized_power: float | None = None
    total_work: float | None = None
    ground_contact_time: float | None = None
    stride_length: float | None = None
    vertical_oscillation: float | None = None
    training_effect: float | None = None
    anaerobic_training_effect: float | None = None
    aerobic_training_effect_message: str | None = None
    anaerobic_training_effect_message: str | None = None
    vertical_ratio: float | None = None
    max_vertical_speed: float | None = None
    water_estimated: float | None = None
    training_effect_label: str | None = None
    activity_training_load: float | None = None
    min_activity_lap_duration: float | None = None
    moderate_intensity_minutes: float | None = None
    vigorous_intensity_minutes: float | None = None
    steps: int | None = None
    begin_potential_stamina: float | None = None
    end_potential_stamina: float | None = None
    min_available_stamina: float | None = None
    avg_grade_adjusted_speed: float | None = None
    difference_body_battery: float | None = None
    # Swimming-specific fields
    average_swim_cadence_in_strokes_per_minute: float | None = None
    average_swolf: float | None = None
    avg_stroke_distance: float | None = None


@dataclass
class Activity:
    """Garmin Connect activity data.

    Retrieve individual activities by ID or list recent activities.

    Example:
        >>> activity = Activity.get(12345678901)
        >>> activity.activity_name
        'Morning Run'
        >>> activity.summary.distance
        5000.0

        >>> activities = Activity.list(limit=10)
        >>> len(activities)
        10
    """

    activity_id: int
    activity_name: str
    activity_type: ActivityType
    start_time_local: datetime | None = None
    start_time_gmt: datetime | None = None
    user_profile_id: int | None = None
    is_multi_sport_parent: bool | None = None
    event_type: EventType | None = None
    summary: Summary | None = None
    location_name: str | None = None
    # Fields from list endpoint (not present in detail endpoint)
    distance: float | None = None
    duration: float | None = None
    elapsed_duration: float | None = None
    moving_duration: float | None = None
    elevation_gain: float | None = None
    elevation_loss: float | None = None
    average_speed: float | None = None
    max_speed: float | None = None
    calories: float | None = None
    average_hr: float | None = None
    max_hr: float | None = None
    owner_id: int | None = None
    owner_display_name: str | None = None
    owner_full_name: str | None = None
    steps: int | None = None
    average_running_cadence_in_steps_per_minute: float | None = None
    max_running_cadence_in_steps_per_minute: float | None = None

    @classmethod
    def get(
        cls,
        activity_id: int,
        *,
        client: http.Client | None = None,
    ) -> Self:
        """Get detailed activity data by activity ID.

        Args:
            activity_id: The Garmin activity ID
            client: Optional HTTP client (uses default if not provided)

        Returns:
            Activity instance with full details including summary metrics
        """
        client = client or http.client
        path = f"/activity-service/activity/{activity_id}"
        data = client.connectapi(path)
        assert data, f"No data returned from {path}"
        assert isinstance(data, dict), (
            f"Expected dict from {path}, got {type(data).__name__}"
        )
        data = camel_to_snake_dict(data)
        data = remove_dto_suffix_from_dict(data)
        return cls(**data)

    @classmethod
    def list(
        cls,
        limit: int = 20,
        start: int = 0,
        *,
        client: http.Client | None = None,
    ) -> list[Self]:
        """List recent activities with pagination.

        Args:
            limit: Maximum number of activities to return (default 20)
            start: Offset for pagination (default 0)
            client: Optional HTTP client (uses default if not provided)

        Returns:
            List of Activity instances (simplified, without full summary)
        """
        client = client or http.client
        path = "/activitylist-service/activities/search/activities"
        data = client.connectapi(path, params={"limit": limit, "start": start})
        assert isinstance(data, list), (
            f"Expected list from {path}, got {type(data).__name__}"
        )
        activities = []
        for item in data:
            item = camel_to_snake_dict(item)
            activities.append(cls(**item))
        return activities

    @classmethod
    def update(
        cls,
        activity_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
        client: http.Client | None = None,
    ) -> None:
        """Update an activity's name and/or description.

        Args:
            activity_id: The Garmin activity ID to update
            name: New name for the activity (optional)
            description: New description for the activity (optional)
            client: Optional HTTP client (uses default if not provided)

        Raises:
            ValueError: If neither name nor description is provided

        Example:
            >>> Activity.update(12345678901, name="Morning Run")
            >>> Activity.update(12345678901, description="Great weather!")
        """
        if name is None and description is None:
            raise ValueError(
                "At least one of 'name' or 'description' required"
            )
        client = client or http.client
        payload: dict[str, int | str] = {"activityId": activity_id}
        if name is not None:
            payload["activityName"] = name
        if description is not None:
            payload["description"] = description
        path = f"/activity-service/activity/{activity_id}"
        client.connectapi(path, method="PUT", json=payload)
