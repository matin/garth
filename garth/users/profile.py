from typing import List, Optional

from pydantic.dataclasses import dataclass

from .. import http
from ..utils import camel_to_snake_dict


@dataclass(frozen=True)
class UserProfile:
    id: int
    profile_id: int
    garmin_guid: str
    display_name: str
    full_name: str
    user_name: str
    profile_image_uuid: str
    profile_image_url_large: str
    profile_image_url_medium: str
    profile_image_url_small: str
    location: str
    facebook_url: Optional[str]
    twitter_url: Optional[str]
    personal_website: Optional[str]
    motivation: Optional[str]
    bio: Optional[str]
    primary_activity: Optional[str]
    favorite_activity_types: List[str]
    running_training_speed: float
    cycling_training_speed: float
    favorite_cycling_activity_types: List[str]
    cycling_classification: Optional[str]
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
    other_activity: Optional[str]
    other_primary_activity: Optional[str]
    other_motivation: Optional[str]
    user_roles: List[str]
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
    def get(cls, /, client: Optional[http.Client] = None):
        client = client or http.client
        profile = client.connectapi("/userprofile-service/socialProfile")
        assert isinstance(profile, dict)
        return cls(**camel_to_snake_dict(profile))
