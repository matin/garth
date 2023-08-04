import json
import os

from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from . import sso
from .auth_tokens import OAuth1Token, OAuth2Token
from .utils import asdict

USER_AGENT = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    ),
}


class Client:
    sess: Session
    last_resp: Response
    domain: str = "garmin.com"
    oauth1_token: OAuth1Token | None = None
    oauth2_token: OAuth2Token | None = None
    timeout: int = 10
    retries: int = 3
    status_forcelist: tuple[int, ...] = (408, 429, 500, 502, 503, 504)
    backoff_factor: float = 0.5
    _username: str | None = None

    def __init__(self, session: Session | None = None, **kwargs):
        self.sess = session if session else Session()
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
        oauth1_token: OAuth1Token | None = None,
        oauth2_token: OAuth2Token | None = None,
        domain: str | None = None,
        proxies: dict | None = None,
        ssl_verify: bool | None = None,
        timeout: int | None = None,
        retries: int | None = None,
        status_forcelist: tuple[int, ...] | None = None,
        backoff_factor: float | None = None,
    ):
        if oauth1_token is not None:
            self.oauth1_token = oauth1_token
        if oauth2_token is not None:
            self.oauth2_token = oauth2_token
        if domain:
            self.domain = domain
        if proxies is not None:
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
    def username(self) -> str | None:
        if not self._username:
            self._username = self.connectapi(
                "/userprofile-service/socialProfile"
            )["userName"]
        return self._username

    def request(
        self,
        method: str,
        subdomain: str,
        path: str,
        /,
        api: bool = False,
        referrer: str | bool = False,
        headers: dict = {},
        **kwargs,
    ):
        url = f"https://{subdomain}.{self.domain}{path}"
        if referrer is True and self.last_resp:
            headers["referer"] = self.last_resp.url
        elif referrer:
            headers["referer"] = referrer
        if api:
            headers["Authorization"] = str(self.oauth2_token)
        self.last_resp = self.sess.request(
            method,
            url,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        self.last_resp.raise_for_status()
        return self.last_resp

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def login(self, *args):
        self.oauth1_token, self.oauth2_token = sso.login(*args, client=self)

    def connectapi(self, path: str, **kwargs):
        resp = self.get("connectapi", path, api=True, **kwargs)
        if resp.status_code == 204:
            rv = None
        else:
            rv = resp.json()
        return rv

    def dump(self, dir_path: str):
        dir_path = os.path.expanduser(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, "oauth1_token.json"), "w") as f:
            if self.oauth1_token:
                json.dump(asdict(self.oauth1_token), f, indent=4)
        with open(os.path.join(dir_path, "oauth2_token.json"), "w") as f:
            if self.oauth2_token:
                json.dump(asdict(self.oauth2_token), f, indent=4)

    def load(self, dir_path: str):
        dir_path = os.path.expanduser(dir_path)
        with open(os.path.join(dir_path, "oauth1_token.json")) as f:
            oauth1 = OAuth1Token(**json.load(f))
        with open(os.path.join(dir_path, "oauth2_token.json")) as f:
            oauth2 = OAuth2Token(**json.load(f))
        self.configure(oauth1_token=oauth1, oauth2_token=oauth2)


client = Client()
