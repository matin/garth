from .http import client
from .version import __version__

__all__ = [
    "client",
    "configure",
    "login",
    "connectapi",
    "save",
    "resume",
    "__version__",
]

configure = client.configure
login = client.login
connectapi = client.connectapi
save = client.save_session
resume = client.resume_session
