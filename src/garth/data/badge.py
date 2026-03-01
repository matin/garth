import builtins
from datetime import datetime

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict


@dataclass(frozen=True)
class Badge:
    """Garmin Connect badges data.

    Retrieve badges by ID or full list.

    Example:
        >>> badge = Badge.get(55, client=authed_client).annual
        >>> badge.badge_name
        'Strong Start'
        >>> badge.earned_by_me
        True
    """

    badge_id: int
    badge_key: str
    badge_name: str
    badge_category_id: int
    badge_difficulty_id: int
    badge_points: int
    badge_type_ids: builtins.list["int"]
    premium: bool
    earned_by_me: bool
    badge_assoc_type_id: int
    badge_assoc_type: str
    user_profile_id: int | None = None
    full_name: str | None = None
    display_name: str | None = None
    badge_is_viewed: bool | None = None
    badge_uuid: str | None = None
    badge_series_id: int | None = None
    badge_start_date: datetime | None = None
    badge_end_date: datetime | None = None
    badge_earned_date: datetime | None = None
    badge_earned_number: int | None = None
    badge_limit_count: int | None = None
    badge_progress_value: int | float | None = None
    badge_target_value: int | float | None = None
    badge_unit_id: int | None = None
    badge_assoc_data_id: str | None = None
    badge_assoc_data_name: str | None = None
    create_date: datetime | None = None

    CATEGORY_ACTIVITIES = 1
    CATEGORY_RUNNING = 2
    CATEGORY_CYCLING = 3
    CATEGORY_CHALLENGES = 4
    CATEGORY_STEPS = 5
    CATEGORY_CONNECT_FEATURES = 6
    CATEGORY_HEALTH = 7
    CATEGORY_TACX_MULTI_STAGE = 8
    CATEGORY_DIVING = 9

    TYPE_ONE_TIME = 1
    TYPE_TRAINING_CLASS = 2
    TYPE_REPEATABLE = 3
    TYPE_CUMULATIVE = 4
    TYPE_LIMITED_ANNUAL = 5
    TYPE_LIMITED_SINGLE = 6
    TYPE_SERIES_EVENTS = 7

    DIFFICULTY_EASY = 1
    DIFFICULTY_MEDIUM = 2
    DIFFICULTY_HARD = 3
    DIFFICULTY_ELITE = 4

    ASSOC_TYPE_ACTIVITY = 1
    ASSOC_TYPE_GROUP_CHALLENGE = 2
    ASSOC_TYPE_ADHOC_CHALLENGE = 3
    ASSOC_TYPE_DAY = 4
    ASSOC_TYPE_NO_LINK = 5
    ASSOC_TYPE_ACTIVITY_DAY = 6
    ASSOC_TYPE_VIVOFITJR_CHALLENGE = 7
    ASSOC_TYPE_VIVOFITJR_TEAM_CHALLENGE = 8
    ASSOC_TYPE_BADGE_CHALLENGE = 9
    ASSOC_TYPE_EVENT = 10
    ASSOC_TYPE_SCORECARD = 11

    UNIT_MI_KM = 1
    UNIT_FT_M = 2
    UNIT_ACTIVITIES = 3
    UNIT_DAYS = 4
    UNIT_STEPS = 5
    UNIT_MI = 6
    UNIT_SECONDS = 7
    UNIT_CHALLENGES = 8
    UNIT_KILOCALORIES = 9
    UNIT_WEEKS = 10
    UNIT_LIKES = 11

    @property
    def limited_time(self) -> bool:
        return Badge.TYPE_LIMITED_SINGLE in self.badge_type_ids

    @property
    def annual(self) -> bool:
        return Badge.TYPE_LIMITED_ANNUAL in self.badge_type_ids

    @property
    def repeatable(self) -> bool:
        return Badge.TYPE_REPEATABLE in self.badge_type_ids

    @property
    def cumulative(self) -> bool:
        return Badge.TYPE_CUMULATIVE in self.badge_type_ids

    @property
    def month_challenge(self) -> bool:
        return (
            self.badge_category_id == Badge.CATEGORY_CHALLENGES
            and self.limited_time
        )

    @property
    def expedition(self) -> bool:
        return self.badge_assoc_type_id == Badge.ASSOC_TYPE_BADGE_CHALLENGE

    def reload(self, client: http.Client | None = None):
        """Get actual data for Badge
        Useful to retrieve actual information for repeatable badges from list response
        """
        return Badge.get(self.badge_id, client or http.client)

    @classmethod
    def get(cls, id: int, client: http.Client | None = None) -> Self:
        """Get badge by ID.

        Args:
            id: The Garmin badge ID
            client: Optional HTTP client (uses default if not provided)

        Returns:
            Badge instance with full details
        """
        client = client or http.client
        path = f"/badge-service/badge/detail/v2/{id}"
        data = client.connectapi(path)
        assert data, f"No data returned from {path}"
        assert isinstance(data, dict), (
            f"Expected dict from {path}, got {type(data).__name__}"
        )
        data = camel_to_snake_dict(data)
        return cls(**data)

    @classmethod
    def list(
        cls,
        client: http.Client | None = None,
    ) -> list[Self]:
        """List of badges, combines earned and available lists.
        Earned and repeatable badges contain data for the first receiving
        For actual progress they should be loaded directly by get or reload methods

        Returns:
            List of Badge instances
        """
        client = client or http.client

        path = "/badge-service/badge/earned"
        earned = client.connectapi(path)
        assert isinstance(earned, list), (
            f"Expected list from {path}, got {type(earned).__name__}"
        )

        path = "/badge-service/badge/available?showExclusiveBadge=true"
        available = client.connectapi(path)
        assert isinstance(available, list), (
            f"Expected list from {path}, got {type(available).__name__}"
        )

        data = earned + available

        badges = []
        for item in data:
            item = camel_to_snake_dict(item)
            badges.append(cls(**item))
        return badges
