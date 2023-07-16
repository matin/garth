from typing import Optional

from requests import Session


USER_AGENT = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    ),
}


class Client:
    def __init__(self, **kwargs):
        self.configure(**kwargs)

    def configure(
        self,
        domain: str = "garmin.com",
    ):
        self.domain = domain
        self.sess = Session()
        self.sess.headers.update(USER_AGENT)

    def request(
        self,
        method: str,
        subdomain: str,
        path: str,
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ):
        url = f"https://{subdomain}.{self.domain}{path}"
        resp = self.sess.request(
            method,
            url,
            params=params,
            data=data,
            **kwargs,
        )
        return resp

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)


client = Client()
