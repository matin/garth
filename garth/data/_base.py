from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from .. import http
from ..utils import date_range, format_end_date


MAX_WORKERS = 10


class Data(ABC):
    @classmethod
    @abstractmethod
    def get(
        cls, day: date | str, *, client: http.Client | None = None
    ) -> "Data | None": ...  # pragma: no cover

    @classmethod
    def list(
        cls,
        end: date | str | None = None,
        days: int = 1,
        *,
        client: http.Client | None = None,
        max_workers: int = MAX_WORKERS,
    ):
        client = client or http.client
        end = format_end_date(end)

        def fetch_date(date_):
            if day := cls.get(date_, client=client):
                return day

        dates = date_range(end, days)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            data = list(executor.map(fetch_date, dates))
            data = [day for day in data if day is not None]

        return data
