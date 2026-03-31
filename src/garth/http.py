import base64
import json
import logging
import os
from collections.abc import Callable
from typing import IO, Any, Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from . import sso
from .auth_tokens import OAuth1Token, OAuth2Token
from .exc import GarthException, GarthHTTPError
from .utils import asdict

log = logging.getLogger(__name__)

OAUTH1_TOKEN_FILE = "oauth1_token.json"
OAUTH2_TOKEN_FILE = "oauth2_token.json"


class GarthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GARTH_")

    home: str | None = None
    token: str | None = None

    @model_validator(mode="after")
    def check_mutual_exclusivity(self):
        if self.home and self.token:
            raise GarthException(
                msg="GARTH_HOME and GARTH_TOKEN cannot both be set"
            )
        return self


class _Response:
    """Response wrapper compatible with garth's existing API.

    Note:
        This is not thread-safe. Playwright browser pages cannot be
        shared across threads.
    """

    def __init__(
        self, status_code: int, text: str, url: str
    ) -> None:
        self.status_code = status_code
        self.text = text
        self.url = url
        self.ok = 200 <= status_code < 300
        self.content = (
            text.encode() if isinstance(text, str) else b""
        )

    def json(self) -> Any:
        return json.loads(self.text)

    def raise_for_status(self) -> None:
        if not self.ok:
            raise GarthHTTPError(
                msg="Error in request",
                error=Exception(
                    f"{self.status_code} for url: {self.url}"
                ),
            )


class Client:
    """Garmin Connect API client using browser-based transport.

    All HTTP requests are routed through a Camoufox headless browser
    via ``page.evaluate(fetch(...))``, bypassing Cloudflare bot
    detection.

    Note:
        This client is **not thread-safe**. Playwright browser pages
        cannot be shared across threads. If you need concurrent
        access, use separate Client instances in separate processes.
    """

    last_resp: _Response | None = None
    domain: str = "garmin.com"
    oauth1_token: OAuth1Token | Literal["needs_mfa"] | None = None
    oauth2_token: OAuth2Token | dict[str, Any] | None = None
    timeout: int = 10
    retries: int = 3
    status_forcelist: tuple[int, ...] = (408, 500, 502, 503, 504)
    backoff_factor: float = 0.5
    pool_connections: int = 10
    pool_maxsize: int = 10
    _user_profile: dict[str, Any] | None = None
    _garth_home: str | None = None

    def __init__(self, **kwargs):
        self.configure(**kwargs)
        self._auto_resume()

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
        **kwargs,
    ):
        if oauth1_token is not None:
            self.oauth1_token = oauth1_token
        if oauth2_token is not None:
            self.oauth2_token = oauth2_token
        if domain:
            self.domain = domain
        if proxies is not None:
            log.warning(
                "proxies not supported with browser transport"
            )
        if ssl_verify is not None:
            log.warning(
                "ssl_verify not supported with browser transport"
            )
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

    def _auto_resume(self):
        """Auto-resume session from GARTH_HOME or GARTH_TOKEN."""
        settings = GarthSettings()
        if settings.home:
            self._garth_home = settings.home
            token_path = os.path.join(
                os.path.expanduser(settings.home),
                OAUTH1_TOKEN_FILE,
            )
            if os.path.exists(token_path):
                self.load(settings.home)
        elif settings.token:
            self.loads(settings.token)

    @property
    def user_profile(self):
        if not self._user_profile:
            result = self.connectapi(
                "/userprofile-service/socialProfile"
            )
            assert isinstance(result, dict), (
                "No profile from connectapi"
            )
            self._user_profile = result
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
    ) -> _Response:
        """Make an API request through the browser.

        All requests are routed through ``page.evaluate(fetch(...))``
        in the Camoufox browser, bypassing Cloudflare.
        """
        page = sso.get_page()
        csrf = sso.get_csrf()

        if not page:
            raise GarthException(
                msg="Not logged in — call login() first"
            )

        url = f"/gc-api/{path.lstrip('/')}"

        params = kwargs.get("params")
        if params:
            from urllib.parse import urlencode
            url += "?" + urlencode(params)

        json_body = kwargs.get("json")
        data = kwargs.get("data")

        # Handle file uploads
        files = kwargs.get("files")
        if files:
            if len(files) > 1:
                raise GarthException(
                    msg="Only single file upload is supported"
                )
            return self._upload_via_browser(
                page, csrf, url, files
            )

        result = page.evaluate("""
            async ([url, method, jsonBody, formData, csrf,
                    extraHeaders]) => {
                const h = {
                    'connect-csrf-token': csrf || '',
                    'Accept': 'application/json'
                };
                if (extraHeaders) {
                    Object.assign(h, extraHeaders);
                }
                let body = undefined;
                if (jsonBody) {
                    h['Content-Type'] = 'application/json';
                    body = JSON.stringify(jsonBody);
                } else if (formData) {
                    h['Content-Type'] =
                        'application/x-www-form-urlencoded';
                    body = formData;
                }
                try {
                    const resp = await fetch(url, {
                        method: method || 'GET',
                        credentials: 'include',
                        headers: h,
                        body: body
                    });
                    const text = await resp.text();
                    return {
                        status: resp.status,
                        text: text,
                        url: resp.url
                    };
                } catch(e) {
                    return {status: 0, error: e.message};
                }
            }
        """, [
            url,
            method.upper(),
            json_body,
            data if isinstance(data, str) else None,
            csrf,
            headers if headers else None,
        ])

        if result.get("error"):
            raise GarthHTTPError(
                msg=f"Browser fetch error: {result['error']}",
                error=Exception(result["error"]),
            )

        status = result.get("status", 0)
        text = result.get("text", "")
        resp_url = result.get("url", "")

        resp = _Response(status, text, resp_url)
        self.last_resp = resp

        if not resp.ok:
            resp.raise_for_status()

        return resp

    def _upload_via_browser(
        self, page, csrf: str, url: str, files: dict
    ) -> _Response:
        """Upload a single file via browser FormData."""
        field_name, (filename, fp) = next(iter(files.items()))
        file_bytes = fp.read()
        b64_data = base64.b64encode(file_bytes).decode()

        result = page.evaluate("""
            async ([url, b64Data, fileName, csrf]) => {
                const resp = await fetch(
                    'data:application/octet-stream;base64,'
                    + b64Data
                );
                const blob = await resp.blob();
                const formData = new FormData();
                formData.append('file', blob, fileName);
                try {
                    const resp = await fetch(url, {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'connect-csrf-token': csrf || ''
                        },
                        body: formData
                    });
                    const text = await resp.text();
                    return {
                        status: resp.status,
                        text: text,
                        url: resp.url
                    };
                } catch(e) {
                    return {status: 0, error: e.message};
                }
            }
        """, [url, b64_data, filename, csrf])

        if result.get("error"):
            raise GarthHTTPError(
                msg=f"Upload error: {result['error']}",
                error=Exception(result["error"]),
            )

        resp = _Response(
            result.get("status", 0),
            result.get("text", ""),
            result.get("url", ""),
        )
        self.last_resp = resp

        if not resp.ok:
            resp.raise_for_status()

        return resp

    def get(self, *args, **kwargs) -> _Response:
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs) -> _Response:
        return self.request("POST", *args, **kwargs)

    def delete(self, *args, **kwargs) -> _Response:
        return self.request("DELETE", *args, **kwargs)

    def put(self, *args, **kwargs) -> _Response:
        return self.request("PUT", *args, **kwargs)

    def login(self, *args, **kwargs):
        self.oauth1_token, self.oauth2_token = sso.login(
            *args, **kwargs, client=self
        )
        if self._garth_home:
            self.dump(self._garth_home)
        return self.oauth1_token, self.oauth2_token

    def resume_login(self, *args, **kwargs):
        self.oauth1_token, self.oauth2_token = sso.resume_login(
            *args, **kwargs
        )
        if self._garth_home:
            self.dump(self._garth_home)
        return self.oauth1_token, self.oauth2_token

    def refresh_oauth2(self):
        assert self.oauth1_token and isinstance(
            self.oauth1_token, OAuth1Token
        ), "OAuth1 token is required for OAuth2 refresh"
        self.oauth2_token = sso.exchange(self.oauth1_token, self)
        if self._garth_home:
            self.dump(self._garth_home, oauth2_only=True)

    def connectapi(
        self, path: str, method="GET", **kwargs
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        resp = self.request(
            method, "connectapi", path, api=True, **kwargs
        )
        if resp.status_code == 204:
            return None
        return resp.json()

    def download(self, path: str, **kwargs) -> bytes:
        """Download binary data (FIT files, etc.)."""
        page = sso.get_page()
        csrf = sso.get_csrf()

        if not page:
            raise GarthException(
                msg="Not logged in — call login() first"
            )

        url = f"/gc-api/{path.lstrip('/')}"

        result = page.evaluate("""
            async ([url, csrf]) => {
                try {
                    const resp = await fetch(url, {
                        credentials: 'include',
                        headers: {
                            'connect-csrf-token': csrf || ''
                        }
                    });
                    if (resp.status !== 200) {
                        return {
                            status: resp.status, data: null
                        };
                    }
                    const blob = await resp.blob();
                    return await new Promise((resolve) => {
                        const reader = new FileReader();
                        reader.onloadend = () => {
                            const b64 = reader.result
                                .split(',')[1];
                            resolve({status: 200, data: b64});
                        };
                        reader.readAsDataURL(blob);
                    });
                } catch(e) {
                    return {status: 0, error: e.message};
                }
            }
        """, [url, csrf])

        if result.get("error") or result.get("status") != 200:
            raise GarthHTTPError(
                msg=(
                    "Download failed: "
                    f"HTTP {result.get('status')}"
                ),
                error=Exception(
                    result.get(
                        "error",
                        f"HTTP {result.get('status')}",
                    )
                ),
            )

        return base64.b64decode(result["data"])

    def upload(
        self,
        fp: IO[bytes],
        /,
        path: str = "/upload-service/upload",
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

    def dump(
        self, dir_path: str, /, oauth2_only: bool = False
    ) -> None:
        dir_path = os.path.expanduser(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        if not oauth2_only:
            with open(
                os.path.join(dir_path, OAUTH1_TOKEN_FILE), "w"
            ) as f:
                if self.oauth1_token:
                    json.dump(
                        asdict(self.oauth1_token), f, indent=4
                    )
        with open(
            os.path.join(dir_path, OAUTH2_TOKEN_FILE), "w"
        ) as f:
            if self.oauth2_token:
                json.dump(
                    asdict(self.oauth2_token), f, indent=4
                )

    def dumps(self) -> str:
        r = []
        r.append(asdict(self.oauth1_token))
        r.append(asdict(self.oauth2_token))
        s = json.dumps(r)
        return base64.b64encode(s.encode()).decode()

    def load(self, dir_path: str) -> None:
        dir_path = os.path.expanduser(dir_path)
        with open(
            os.path.join(dir_path, OAUTH1_TOKEN_FILE)
        ) as f:
            oauth1 = OAuth1Token(**json.load(f))
        with open(
            os.path.join(dir_path, OAUTH2_TOKEN_FILE)
        ) as f:
            oauth2 = OAuth2Token(**json.load(f))

        # Detect browser-backed placeholder tokens
        if sso.is_browser_token(oauth1):
            log.warning(
                "Loaded browser-session tokens from %s. "
                "These require an active browser — call login() "
                "to start a new session.",
                dir_path,
            )

        self.configure(
            oauth1_token=oauth1,
            oauth2_token=oauth2,
            domain=oauth1.domain,
        )

    def loads(self, s: str) -> None:
        oauth1, oauth2 = json.loads(base64.b64decode(s))
        oauth1_obj = OAuth1Token(**oauth1)

        if sso.is_browser_token(oauth1_obj):
            log.warning(
                "Loaded browser-session tokens from string. "
                "These require an active browser — call login() "
                "to start a new session."
            )

        self.configure(
            oauth1_token=oauth1_obj,
            oauth2_token=OAuth2Token(**oauth2),
            domain=oauth1.get("domain"),
        )


client = Client()
