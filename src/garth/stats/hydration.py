from datetime import datetime
from typing import ClassVar

from pydantic.dataclasses import dataclass

from .. import http
from ._base import Stats


BASE_PATH = "/usersummary-service/stats/hydration"


@dataclass
class DailyHydration(Stats):
    value_in_ml: float
    goal_in_ml: float

    _path: ClassVar[str] = f"{BASE_PATH}/daily/{{start}}/{{end}}"
    _page_size: ClassVar[int] = 28

    @staticmethod
    def log(
        value_in_ml: float,
        *,
        timestamp: datetime | None = None,
        client: http.Client | None = None,
    ) -> None:
        """Log hydration intake.

        Args:
            value_in_ml: Amount of water in milliliters
            timestamp: When the hydration was logged (defaults to now)
            client: Optional HTTP client
        """
        client = client or http.client
        if timestamp is None:
            timestamp = datetime.now()

        profile_id = client.user_profile["profileId"]
        client.connectapi(
            "/usersummary-service/usersummary/hydration/log",
            method="PUT",
            json={
                "valueInML": str(value_in_ml),
                "timestampLocal": timestamp.strftime("%Y-%m-%dT%H:%M:%S.0"),
                "userProfileId": str(profile_id),
            },
        )
