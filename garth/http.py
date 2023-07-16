from requests import Session

from .auth_token import AuthToken


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
    username: str | None = None

    def __init__(self, **kwargs):
        self.auth_token = None
        self.sess = Session()
        self.sess.headers.update(USER_AGENT)
        self.configure(**kwargs)

    def configure(
        self,
        /,
        auth_token: AuthToken | None = None,
        username: str | None = None,
        cookies: dict | None = None,
        domain: str | None = None,  # Set to "garmin.cn" for China
    ):
        if auth_token:
            self.auth_token = auth_token
        if username:
            self.username = username
        if cookies:
            self.sess.cookies.update(cookies)
        if domain:
            self.domain = domain

    def request(
        self,
        method: str,
        subdomain: str,
        path: str,
        **kwargs,
    ):
        if self.auth_token and self.auth_token.expired:
            self.auth_token.refresh(client=self)
        url = f"https://{subdomain}.{self.domain}{path}"
        resp = self.sess.request(
            method,
            url,
            **kwargs,
        )
        return resp

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def login(self, *args):
        if not self.auth_token:
            token, username = AuthToken.login(*args, client=self)
            self.auth_token = token
            self.username = username
        else:
            self.auth_token.refresh(client=self)


client = Client()
