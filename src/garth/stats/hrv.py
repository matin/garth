from datetime import date, datetime, timedelta
from typing import Any, ClassVar, cast

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date


@dataclass
class HRVBaseline:
    low_upper: int
    balanced_low: int
    balanced_upper: int
    marker_value: float | None


@dataclass
class DailyHRV:
    calendar_date: date
    weekly_avg: int | None
    last_night_avg: int | None
    last_night_5_min_high: int | None
    baseline: HRVBaseline | None
    status: str
    feedback_phrase: str
    create_time_stamp: datetime

    _path: ClassVar[str] = "/hrv-service/hrv/daily/{start}/{end}"
    _page_size: ClassVar[int] = 28

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        period: int = 28,
        *,
        client: http.Client | None = None,
    ) -> list[Self]:
        client = client or http.client
        end = format_end_date(end)

        # Paginate if period is greater than page size
        if period > cls._page_size:
            page = cls.list(end, cls._page_size, client=client)
            if not page:
                return []
            page = (
                cls.list(
                    end - timedelta(days=cls._page_size),
                    period - cls._page_size,
                    client=client,
                )
                + page
            )
            return page

        start = end - timedelta(days=period - 1)
        path = cls._path.format(start=start, end=end)
        response = client.connectapi(path)
        if response is None:
            return []
        assert isinstance(response, dict), (
            f"Expected dict from {path}, got {type(response).__name__}"
        )
        daily_hrv = camel_to_snake_dict(response)["hrv_summaries"]
        daily_hrv = cast(list[dict[str, Any]], daily_hrv)
        return [cls(**hrv) for hrv in daily_hrv]
