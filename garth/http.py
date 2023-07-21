import json
import pickle
import re
import os
from dataclasses import asdict

from requests.adapters import HTTPAdapter, Retry
from requests.cookies import RequestsCookieJar
from requests import Session

from .auth_token import AuthToken
from .exc import GarthException


USER_AGENT = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    ),
}


class Client:
    sess: Session
    domain: str = "garmin.com"
    auth_token: AuthToken | None = None
    timeout: int = 15
    retries: int = 3
    status_forcelist: tuple[int, ...] = (429, 500, 502, 503, 504)
    backoff_factor: float = 0.5
    _username: str | None = None

    def __init__(self, **kwargs):
        self.sess = Session()
        self.sess.headers.update(USER_AGENT)
        self.configure(
            timeout=self.timeout,
            retries=self.retries,
            status_forcelist=self.status_forcelist,
            backoff_factor=self.backoff_factor,
            **kwargs,
        )

    def configure(
        self,
        /,
        auth_token: AuthToken | None = None,
        cookies: RequestsCookieJar | None = None,
        domain: str | None = None,  # Set to "garmin.cn" for China
        proxies: dict | None = None,
        ssl_verify: bool | None = None,
        timeout: int | None = None,
        retries: int | None = None,
        status_forcelist: tuple[int, ...] | None = None,
        backoff_factor: float | None = None,
    ):
        if auth_token:
            self.auth_token = auth_token
        if cookies:
            self.sess.cookies = cookies
        if domain:
            self.domain = domain
        if proxies:
            self.sess.proxies.update(proxies)
        if ssl_verify is not None:
            self.sess.verify = ssl_verify
        if timeout is not None:
            self.timeout = timeout
        if retries is not None:
            self.retries = retries
        if status_forcelist is not None:
            self.status_forcelist = status_forcelist
        if backoff_factor is not None:
            self.backoff_factor = backoff_factor

        retry = Retry(
            total=self.retries,
            status_forcelist=self.status_forcelist,
            backoff_factor=self.backoff_factor,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.sess.mount("https://", adapter)

    @property
    def username(self) -> str:
        if self._username:
            return self._username
        resp = self.get("connect", "/modern")
        m = re.search(r'userName":"(.+?)"', resp.text)
        if not m:
            raise GarthException("Could not find username")
        self._username = m.group(1)
        return self._username

    def request(
        self,
        method: str,
        subdomain: str,
        path: str,
        /,
        api: bool = False,
        headers: dict = {},
        **kwargs,
    ):
        url = f"https://{subdomain}.{self.domain}{path}"
        if api:
            if self.auth_token and self.auth_token.expired:
                self.auth_token.refresh(client=self)
            headers["Authorization"] = str(self.auth_token)
            headers["di-backend"] = f"connectapi.{self.domain}"
        resp = self.sess.request(
            method,
            url,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        resp.raise_for_status()
        return resp

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def login(self, *args, clear_cookies: bool = False):
        if clear_cookies:
            self.cookies = RequestsCookieJar()
        token = AuthToken.login(*args, client=self)
        self.auth_token = token

    def connectapi(self, path: str, **kwargs):
        return self.get("connect", path, api=True, **kwargs).json()

    def save_session(self, dir_path: str):
        dir_path = os.path.expanduser(dir_path)
        with open(os.path.join(dir_path, "cookies.pickle"), "wb") as f:
            pickle.dump(self.sess.cookies, f)
        with open(os.path.join(dir_path, "auth_token.json"), "w") as f:
            json.dump(asdict(self.auth_token) if self.auth_token else {}, f)

    def resume_session(self, dir_path: str):
        dir_path = os.path.expanduser(dir_path)
        with open(os.path.join(dir_path, "cookies.pickle"), "rb") as f:
            cookies = pickle.load(f)
        with open(os.path.join(dir_path, "auth_token.json")) as f:
            auth_token = AuthToken(**json.load(f))
        self.configure(auth_token=auth_token, cookies=cookies)


client = Client()
