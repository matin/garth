from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import Optional, Union

from .. import http
from ..utils import date_range, format_end_date

MAX_WORKERS = 10


class Data:
    @classmethod
    def list(
        cls,
        end: Union[date, str, None] = None,
        days: int = 1,
        *,
        client: Optional[http.Client] = None,
        max_workers: int = MAX_WORKERS,
    ):
        client = client or http.client
        end = format_end_date(end)
        data = []

        def fetch_date(date_):
            if day := cls.get(date_, client=client):
                return day

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            dates = date_range(end, days)
            data = list(executor.map(fetch_date, dates))
            data = [day for day in data if day is not None]

        return data
