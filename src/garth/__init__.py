import warnings


warnings.warn(
    "Garth is deprecated and no longer maintained. "
    "See https://github.com/matin/garth/discussions/222",
    DeprecationWarning,
    stacklevel=2,
)

from .data import (  # noqa: E402
    Activity,
    BodyBatteryData,
    DailyBodyBatteryStress,
    DailyHeartRate,
    DailySleepData,
    DailySummary,
    FitnessActivity,
    GarminScoresData,
    HRVData,
    MorningTrainingReadinessData,
    SleepData,
    TrainingReadinessData,
    WeightData,
)
from .http import Client, client  # noqa: E402
from .stats import (  # noqa: E402
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
from .users import UserProfile, UserSettings  # noqa: E402
from .version import __version__  # noqa: E402


__all__ = [
    "Activity",
    "BodyBatteryData",
    "Client",
    "DailyBodyBatteryStress",
    "DailyHeartRate",
    "DailyHRV",
    "DailyHydration",
    "DailyIntensityMinutes",
    "DailySleep",
    "DailySleepData",
    "DailySteps",
    "DailyStress",
    "DailySummary",
    "DailyTrainingStatus",
    "FitnessActivity",
    "GarminScoresData",
    "HRVData",
    "MorningTrainingReadinessData",
    "MonthlyTrainingStatus",
    "SleepData",
    "TrainingReadinessData",
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
