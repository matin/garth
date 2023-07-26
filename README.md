# Garth

[![CI](https://github.com/matin/garth/workflows/CI/badge.svg?event=push)](https://github.com/matin/garth/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![codecov](https://codecov.io/gh/matin/garth/branch/main/graph/badge.svg?token=0EFFYJNFIL)](https://codecov.io/gh/matin/garth)

Garmin SSO auth + Connect client

## Google Colabs

[Graph 28-day rolling average of daily stress](https://colab.research.google.com/github/matin/garth/blob/main/colabs/stress.ipynb)


## Background

Garth is meant for personal use and follows the philosiphy that your data is
your data. You should be able to download it and analyze it in the way that
you'd like. In my case, that means processing with Google Colab, Pandas,
Matplotlib, etc.

There are already a few Garmin Connect libraries. Why write another?

### Authentication

The most important reasoning is to build a library with authentication that
works on [Google Colab](https://colab.research.google.com/) and doesn't require
tools like Cloudscraper. Garth, in comparison:

1. Uses the same embedded SSO as the mobile app
1. Only requires `requests` and `pydantic` as dependencies
1. Supports MFA
1. Supports saving and resuming sessions to avoid the need to log in each time
you run a script, which is particularly useful if you have MFA enabled
1. Works on Google Colab

### Python 3.10+

Google Colab, currently, uses 3.10. We should take advantage of all the goodies
that come along with it. If you need to use an earlier version of Python, there
are other libraries that will meet your needs. There's no intetion to backport.

### JSON vs HTML

Using `garth.connectapi()` allows you to make requests routed to the Connect API
and receive JSON vs needing to parse HTML. You can use the same endpoints the
mobile app uses.

This also goes back to authentication. Garth manages the necessary Bearer
Authentication (along with auto-refresh) necessary to make requests routed to
the Connect API.

## Instructions

### Install

```bash
python -m pip install garth
```

### Authenticate and save session

```python
import garth
from getpass import getpass

email = input("Enter email address: ")
password = getpass("Enter password: ")
# If there's MFA, you'll be prompted during the login
garth.login(email, password)

garth.save("~/.garth")
```

### Configure

#### Set domain for China

```python
garth.configure(domain="garmin.cn")
```

#### Proxy through Charles

```python
garth.configure(proxies={"https": "http://localhost:8888"}, ssl_verify=False)
```

### Attempt to resume session

```python
import garth
from garth import GarthException
from requests import HTTPError

garth.resume("~/.garth")
try:
    garth.client.auth_token.refresh()
except (GarthException, HTTPError):
    # Session is expired. You'll need to log in again
```

## Connect API

### Wellness

```python
sleep = garth.connectapi(
    f"/wellness-service/wellness/dailySleepData/{garth.client.username}",
    params={"date": "2023-07-05", "nonSleepBufferMinutes": 60),
)
list(sleep.keys())
```

```json
[
    "dailySleepDTO",
    "sleepMovement",
    "remSleepData",
    "sleepLevels",
    "sleepRestlessMoments",
    "restlessMomentsCount",
    "wellnessSpO2SleepSummaryDTO",
    "wellnessEpochSPO2DataDTOList",
    "wellnessEpochRespirationDataDTOList",
    "sleepStress"
]
```

### Usersummary

```python
stress =  garth.connectapi(f"/usersummary-service/stats/stress/weekly/2023-07-05/52")
```

```json
{
    "calendarDate": "2023-07-13",
    "values": {
        "highStressDuration": 2880,
        "lowStressDuration": 10140,
        "overallStressLevel": 33,
        "restStressDuration": 30960,
        "mediumStressDuration": 8760
    }
}
```

## Resources

### Stress

Daily stress levels

```python
DailyStress.get("2023-07-23", 2)
```

```python
[
    DailyStress(
        calendar_date=datetime.date(2023, 7, 22),
        overall_stress_level=31,
        rest_stress_duration=31980,
        low_stress_duration=23820,
        medium_stress_duration=7440,
        high_stress_duration=1500
    ),
    DailyStress(
        calendar_date=datetime.date(2023, 7, 23),
        overall_stress_level=26,
        rest_stress_duration=38220,
        low_stress_duration=22500,
        medium_stress_duration=2520,
        high_stress_duration=300
    )
]
```

Weekly stress levels

```python
WeeklyStress.get("2023-07-23", 2)
```

```python
[
    WeeklyStress(calendar_date=datetime.date(2023, 7, 10), value=33),
    WeeklyStress(calendar_date=datetime.date(2023, 7, 17), value=32)
]
```
