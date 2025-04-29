from datetime import datetime, timezone

from pydantic.dataclasses import dataclass

from .. import http
from ..utils import camel_to_snake_dict, remove_dto_from_dict


@dataclass(frozen=True)
class ActivityType:
    type_id: int
    type_key: str
    parent_type_id: int | None = None


@dataclass(frozen=True)
class Summary:
    distance: float
    duration: float
    moving_duration: float
    average_speed: float
    max_speed: float
    calories: float
    average_hr: float
    max_hr: float
    start_time_gmt: datetime
    start_time_local: datetime
    start_latitude: float
    start_longitude: float
    elapsed_duration: float
    elevation_gain: float
    elevation_loss: float
    max_elevation: float
    min_elevation: float
    average_moving_speed: float
    bmr_calories: float
    average_run_cadence: float
    max_run_cadence: float
    average_temperature: float
    max_temperature: float
    min_temperature: float
    average_power: float
    max_power: float
    min_power: float
    normalized_power: float
    total_work: float
    ground_contact_time: float
    stride_length: float
    vertical_oscillation: float
    training_effect: float
    anaerobic_training_effect: float
    aerobic_training_effect_message: str
    anaerobic_training_effect_message: str
    vertical_ratio: float
    end_latitude: float
    end_longitude: float
    max_vertical_speed: float
    water_estimated: float
    training_effect_label: str
    activity_training_load: float
    min_activity_lap_duration: float
    moderate_intensity_minutes: float
    vigorous_intensity_minutes: float
    steps: int
    begin_potential_stamina: float
    end_potential_stamina: float
    min_available_stamina: float
    avg_grade_adjusted_speed: float
    difference_body_battery: float


@dataclass(frozen=True)
class Activity:
    activity_id: int
    activity_name: str
    activity_type: ActivityType
    summary: Summary
    average_running_cadence_in_steps_per_minute: float | None = None
    max_running_cadence_in_steps_per_minute: float | None = None
    steps: int | None = None

    def _get_localized_datetime(
        self, gmt_time: datetime, local_time: datetime
    ) -> datetime:
        local_diff = local_time - gmt_time
        local_offset = timezone(local_diff)
        gmt_time = datetime.fromtimestamp(
            gmt_time.timestamp() / 1000, timezone.utc
        )
        return gmt_time.astimezone(local_offset)

    @property
    def activity_start(self) -> datetime:
        return self._get_localized_datetime(
            self.summary.start_time_gmt, self.summary.start_time_local
        )

    @classmethod
    def get(
        cls,
        id: int,
        *,
        client: http.Client | None = None,
    ):
        client = client or http.client
        path = f"/activity-service/activity/{id}"
        activity_data = client.connectapi(path)
        assert activity_data
        activity_data = camel_to_snake_dict(activity_data)
        activity_data = remove_dto_from_dict(activity_data)
        assert isinstance(activity_data, dict)
        return cls(**activity_data)

    @classmethod
    def list(cls, *args, **kwargs):
        data = super().list(*args, **kwargs)
        return sorted(data, key=lambda x: x.activity_start)
