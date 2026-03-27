# Garth

> **Garth is deprecated and no longer maintained.** Garmin changed their auth
> flow, breaking the mobile auth approach that Garth depends on. I'm not in a
> position to dedicate the time to adapt to these changes. See the
> [announcement](https://github.com/matin/garth/discussions/222) for details.
> Anyone is welcome to fork Garth as a starting point for a new library.

[![PyPI version](https://img.shields.io/pypi/v/garth.svg?logo=python&logoColor=brightgreen&color=brightgreen)](https://pypi.org/project/garth/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/garth)](https://pypistats.org/packages/garth)

Garmin SSO auth + Connect Python client

## About

Garth was a Python library for Garmin Connect API access with OAuth
authentication. It reached 350k+ downloads per month and was translated into
multiple programming languages.

Garmin recently changed their auth flow, breaking the mobile auth approach
that Garth and other libraries depend on
([#217](https://github.com/matin/garth/issues/217)). This is the final
release.

## For existing users

If you already have a saved session with a valid OAuth1 token, Garth may
continue to work until that token expires (~1 year from when it was issued).
New logins will not work.

## Documentation

Documentation is still available at
**[garth.readthedocs.io](https://garth.readthedocs.io)** for reference.
