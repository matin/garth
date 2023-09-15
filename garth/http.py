import json
import os
from typing import Dict, Optional, Tuple, Union

from requests import HTTPError, Response, Session
from requests.adapters import HTTPAdapter, Retry

from . import sso
from .auth_tokens import OAuth1Token, OAuth2Token
from .exc import GarthHTTPError
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
    oauth1_token: Optional[OAuth1Token] = None
    oauth2_token: Optional[OAuth2Token] = None
    timeout: int = 10
    retries: int = 3
    status_forcelist: Tuple[int, ...] = (408, 429, 500, 502, 503, 504)
    backoff_factor: float = 0.5
    _profile: Optional[Dict] = None

    def __init__(self, session: Optional[Session] = None, **kwargs):
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
        oauth1_token: Optional[OAuth1Token] = None,
        oauth2_token: Optional[OAuth2Token] = None,
        domain: Optional[str] = None,
        proxies: Optional[Dict] = None,
        ssl_verify: Optional[bool] = None,
        timeout: Optional[int] = None,
        retries: Optional[int] = None,
        status_forcelist: Optional[Tuple[int, ...]] = None,
        backoff_factor: Optional[float] = None,
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
    def profile(self):
        if not self._profile:
            self._profile = self.connectapi(
                "/userprofile-service/socialProfile"
            )
            assert isinstance(self._profile, dict)
        return self._profile

    @property
    def username(self):
        return self.profile["userName"]

    def request(
        self,
        method: str,
        subdomain: str,
        path: str,
        /,
        api: bool = False,
        referrer: Union[str, bool] = False,
        headers: dict = {},
        **kwargs,
    ) -> Response:
        url = f"https://{subdomain}.{self.domain}{path}"
        if referrer is True and self.last_resp:
            headers["referer"] = self.last_resp.url
        if api:
            assert self.oauth1_token and self.oauth2_token
            if self.oauth2_token.expired:
                self.refresh_oauth2()
            headers["Authorization"] = str(self.oauth2_token)
        self.last_resp = self.sess.request(
            method,
            url,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        try:
            self.last_resp.raise_for_status()
        except HTTPError as e:
            raise GarthHTTPError(
                msg="Error in request",
                error=e,
            )
        return self.last_resp

    def get(self, *args, **kwargs) -> Response:
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs) -> Response:
        return self.request("POST", *args, **kwargs)

    def login(self, *args):
        self.oauth1_token, self.oauth2_token = sso.login(*args, client=self)

    def refresh_oauth2(self):
        assert self.oauth1_token
        # There is a way to perform a refresh of an OAuth2 token, but it
        # appears even Garmin uses this approach when the OAuth2 is expired
        self.oauth2_token = sso.exchange(self.oauth1_token, self)

    def connectapi(self, path: str, **kwargs):
        resp = self.get("connectapi", path, api=True, **kwargs)
        if resp.status_code == 204:
            rv = None
        else:
            rv = resp.json()
        return rv

    def download(self, path: str, **kwargs) -> bytes:
        resp = self.get("connectapi", path, api=True, **kwargs)
        return resp.content

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
