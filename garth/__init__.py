from .http import client
from .resources import (
    DailyIntensityMinutes,
    DailySleep,
    DailySteps,
    DailyStress,
    SleepData,
    WeeklyIntensityMinutes,
    WeeklySteps,
    WeeklyStress,
)
from .version import __version__

__all__ = [
    "DailyIntensityMinutes",
    "DailySleep",
    "DailySteps",
    "DailyStress",
    "SleepData",
    "WeeklyIntensityMinutes",
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
