from .http import client
from .resources import (
    DailySleep,
    DailySteps,
    DailyStress,
    SleepData,
    WeeklySteps,
    WeeklyStress,
)
from .version import __version__

__all__ = [
    "DailySleep",
    "DailySteps",
    "DailyStress",
    "SleepData",
    "WeeklySteps",
    "WeeklyStress",
    "__version__",
    "client",
    "configure",
    "connectapi",
    "login",
    "resume",
    "save",
]

configure = client.configure
login = client.login
connectapi = client.connectapi
save = client.dump
resume = client.load
