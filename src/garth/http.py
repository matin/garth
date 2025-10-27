import base64
import json
import os
from typing import IO, Any, Literal
from urllib.parse import urljoin

from requests import HTTPError, Response, Session
from requests.adapters import HTTPAdapter, Retry

from . import sso
from .auth_tokens import OAuth1Token, OAuth2Token
from .exc import GarthHTTPError
from .utils import asdict


USER_AGENT = {"User-Agent": "GCM-iOS-5.7.2.1"}


class Client:
    sess: Session
    last_resp: Response
    domain: str = "garmin.com"
    oauth1_token: OAuth1Token | Literal["needs_mfa"] | None = None
    oauth2_token: OAuth2Token | dict[str, Any] | None = None
    timeout: int = 10
    retries: int = 3
    status_forcelist: tuple[int, ...] = (408, 429, 500, 502, 503, 504)
    backoff_factor: float = 0.5
    pool_connections: int = 10
    pool_maxsize: int = 10
    _user_profile: dict[str, Any] | None = None

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
        proxies: dict[str, str] | None = None,
        ssl_verify: bool | None = None,
        timeout: int | None = None,
        retries: int | None = None,
        status_forcelist: tuple[int, ...] | None = None,
        backoff_factor: float | None = None,
        pool_connections: int | None = None,
        pool_maxsize: int | None = None,
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
        if pool_connections is not None:
            self.pool_connections = pool_connections
        if pool_maxsize is not None:
            self.pool_maxsize = pool_maxsize

        retry = Retry(
            total=self.retries,
            status_forcelist=self.status_forcelist,
            backoff_factor=self.backoff_factor,
        )
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
        )
        self.sess.mount("https://", adapter)

    @property
    def user_profile(self):
        if not self._user_profile:
            self._user_profile = self.connectapi(
                "/userprofile-service/socialProfile"
            )
            assert isinstance(self._user_profile, dict), (
                "No profile from connectapi"
            )
        return self._user_profile

    @property
    def profile(self):
        return self.user_profile

    @property
    def username(self):
        return self.user_profile["userName"]

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
    ) -> Response:
        url = f"https://{subdomain}.{self.domain}"
        url = urljoin(url, path)
        if referrer is True and self.last_resp:
            headers["referer"] = self.last_resp.url
        if api:
            assert self.oauth1_token, (
                "OAuth1 token is required for API requests"
            )
            if (
                not isinstance(self.oauth2_token, OAuth2Token)
                or self.oauth2_token.expired
            ):
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

    def delete(self, *args, **kwargs) -> Response:
        return self.request("DELETE", *args, **kwargs)

    def put(self, *args, **kwargs) -> Response:
        return self.request("PUT", *args, **kwargs)

    def login(self, *args, **kwargs):
        self.oauth1_token, self.oauth2_token = sso.login(
            *args, **kwargs, client=self
        )
        return self.oauth1_token, self.oauth2_token

    def resume_login(self, *args, **kwargs):
        self.oauth1_token, self.oauth2_token = sso.resume_login(
            *args, **kwargs
        )
        return self.oauth1_token, self.oauth2_token

    def refresh_oauth2(self):
        assert self.oauth1_token and isinstance(
            self.oauth1_token, OAuth1Token
        ), "OAuth1 token is required for OAuth2 refresh"
        # There is a way to perform a refresh of an OAuth2 token, but it
        # appears even Garmin uses this approach when the OAuth2 is expired
        self.oauth2_token = sso.exchange(self.oauth1_token, self)

    def connectapi(
        self, path: str, method="GET", **kwargs
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        resp = self.request(method, "connectapi", path, api=True, **kwargs)
        if resp.status_code == 204:
            return None
        return resp.json()

    def download(self, path: str, **kwargs) -> bytes:
        resp = self.get("connectapi", path, api=True, **kwargs)
        return resp.content

    def upload(
        self, fp: IO[bytes], /, path: str = "/upload-service/upload"
    ) -> dict[str, Any]:
        fname = os.path.basename(fp.name)
        files = {"file": (fname, fp)}
        result = self.connectapi(
            path,
            method="POST",
            files=files,
        )
        assert result is not None, "No result from upload"
        assert isinstance(result, dict)
        return result

    def dump(self, dir_path: str):
        dir_path = os.path.expanduser(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, "oauth1_token.json"), "w") as f:
            if self.oauth1_token:
                json.dump(asdict(self.oauth1_token), f, indent=4)
        with open(os.path.join(dir_path, "oauth2_token.json"), "w") as f:
            if self.oauth2_token:
                json.dump(asdict(self.oauth2_token), f, indent=4)

    def dumps(self) -> str:
        r = []
        r.append(asdict(self.oauth1_token))
        r.append(asdict(self.oauth2_token))
        s = json.dumps(r)
        return base64.b64encode(s.encode()).decode()

    def load(self, dir_path: str):
        dir_path = os.path.expanduser(dir_path)
        with open(os.path.join(dir_path, "oauth1_token.json")) as f:
            oauth1 = OAuth1Token(**json.load(f))
        with open(os.path.join(dir_path, "oauth2_token.json")) as f:
            oauth2 = OAuth2Token(**json.load(f))
        self.configure(
            oauth1_token=oauth1, oauth2_token=oauth2, domain=oauth1.domain
        )

    def loads(self, s: str):
        oauth1, oauth2 = json.loads(base64.b64decode(s))
        self.configure(
            oauth1_token=OAuth1Token(**oauth1),
            oauth2_token=OAuth2Token(**oauth2),
            domain=oauth1.get("domain"),
        )


client = Client()
