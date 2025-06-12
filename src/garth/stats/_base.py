from datetime import date, timedelta
from typing import ClassVar

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from .. import http
from ..utils import camel_to_snake_dict, format_end_date


@dataclass
class Stats:
    calendar_date: date

    _path: ClassVar[str]
    _page_size: ClassVar[int]
    _period_type: ClassVar[str | None] = None

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        period: int = 1,
        *,
        client: http.Client | None = None,
    ) -> list[Self]:
        client = client or http.client
        end = format_end_date(end)
        period_type = cls._period_type or (
            "days" if "daily" in cls._path else "weeks"
        )

        if period > cls._page_size:
            page = cls.list(end, cls._page_size, client=client)
            if not page:
                return []
            page = (
                cls.list(
                    end - timedelta(**{period_type: cls._page_size}),
                    period - cls._page_size,
                    client=client,
                )
                + page
            )
            return page

        start = end - timedelta(**{period_type: period - 1})
        path = cls._path.format(start=start, end=end, period=period)
        response = client.connectapi(path)

        # Allow subclasses to customize response parsing
        page_dirs = cls._parse_response(response)
        if not page_dirs:
            return []

        page_dirs = [camel_to_snake_dict(stat) for stat in page_dirs]
        return [cls(**stat) for stat in page_dirs]

    @classmethod
    def _parse_response(cls, response):
        """Parse API response into list of stat dictionaries.

        Override this method in subclasses for custom response parsing.
        Default implementation handles standard stats API format.
        """
        if not isinstance(response, list) or not response:
            return []
        page_dirs = [d for d in response if isinstance(d, dict)]
        if page_dirs and "values" in page_dirs[0]:
            page_dirs = [{**stat, **stat.pop("values")} for stat in page_dirs]
        return page_dirs
