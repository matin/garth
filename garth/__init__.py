from .http import client

__version__ = "0.2.0"

configure = client.configure
login = client.login
connectapi = client.connectapi
save = client.save_session
resume = client.resume_session
