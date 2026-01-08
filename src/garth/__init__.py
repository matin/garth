from .data import (
    Activity,
    BodyBatteryData,
    DailyBodyBatteryStress,
    DailySummary,
    GarminScoresData,
    HRVData,
    MorningTrainingReadinessData,
    SleepData,
    WeightData,
)
from .http import Client, client
from .stats import (
    DailyHRV,
    DailyHydration,
    DailyIntensityMinutes,
    DailySleep,
    DailySteps,
    DailyStress,
    DailyTrainingStatus,
    MonthlyTrainingStatus,
    WeeklyIntensityMinutes,
    WeeklySteps,
    WeeklyStress,
    WeeklyTrainingStatus,
)
from .users import UserProfile, UserSettings
from .version import __version__


__all__ = [
    "Activity",
    "BodyBatteryData",
    "Client",
    "DailyBodyBatteryStress",
    "DailyHRV",
    "DailyHydration",
    "DailyIntensityMinutes",
    "DailySleep",
    "DailySteps",
    "DailyStress",
    "DailySummary",
    "DailyTrainingStatus",
    "GarminScoresData",
    "HRVData",
    "MorningTrainingReadinessData",
    "MonthlyTrainingStatus",
    "SleepData",
    "UserProfile",
    "UserSettings",
    "WeeklyIntensityMinutes",
    "WeeklySteps",
    "WeeklyStress",
    "WeeklyTrainingStatus",
    "WeightData",
    "__version__",
    "client",
    "configure",
    "connectapi",
    "download",
    "login",
    "resume",
    "save",
    "upload",
]

configure = client.configure
connectapi = client.connectapi
download = client.download
login = client.login
resume = client.load
save = client.dump
upload = client.upload
