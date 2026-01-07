from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict


@dataclass
class UserProfile:
    id: int
    profile_id: int
    garmin_guid: str
    display_name: str
    full_name: str
    user_name: str
    profile_image_type: str | None
    profile_image_url_large: str | None
    profile_image_url_medium: str | None
    profile_image_url_small: str | None
    location: str | None
    facebook_url: str | None
    twitter_url: str | None
    personal_website: str | None
    motivation: str | None
    bio: str | None
    primary_activity: str | None
    favorite_activity_types: list[str]
    running_training_speed: float
    cycling_training_speed: float
    favorite_cycling_activity_types: list[str]
    cycling_classification: str | None
    cycling_max_avg_power: float
    swimming_training_speed: float
    profile_visibility: str
    activity_start_visibility: str
    activity_map_visibility: str
    course_visibility: str
    activity_heart_rate_visibility: str
    activity_power_visibility: str
    badge_visibility: str
    show_age: bool
    show_weight: bool
    show_height: bool
    show_weight_class: bool
    show_age_range: bool
    show_gender: bool
    show_activity_class: bool
    show_vo_2_max: bool
    show_personal_records: bool
    show_last_12_months: bool
    show_lifetime_totals: bool
    show_upcoming_events: bool
    show_recent_favorites: bool
    show_recent_device: bool
    show_recent_gear: bool
    show_badges: bool
    other_activity: str | None
    other_primary_activity: str | None
    other_motivation: str | None
    user_roles: list[str]
    name_approved: bool
    user_profile_full_name: str
    make_golf_scorecards_private: bool
    allow_golf_live_scoring: bool
    allow_golf_scoring_by_connections: bool
    user_level: int
    user_point: int
    level_update_date: str
    level_is_viewed: bool
    level_point_threshold: int
    user_point_offset: int
    user_pro: bool

    @classmethod
    def get(cls, /, client: http.Client | None = None) -> Self:
        client = client or http.client
        profile = client.connectapi("/userprofile-service/socialProfile")
        assert isinstance(profile, dict)
        return cls(**camel_to_snake_dict(profile))
