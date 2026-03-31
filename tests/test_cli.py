import builtins
import getpass
import sys
import time

import pytest

from garth.auth_tokens import OAuth1Token, OAuth2Token
from garth.cli import main


def test_help_flag(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["garth", "-h"])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert "usage:" in out.lower()


def test_no_args_prints_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["garth"])
    main()
    out, err = capsys.readouterr()
    assert "usage:" in out.lower()


def test_login_command(monkeypatch, capsys):
    mock_oauth1 = OAuth1Token(
        oauth_token="test_token",
        oauth_token_secret="test_secret",
        domain="garmin.com",
    )
    mock_oauth2 = OAuth2Token(
        scope="CONNECT_READ",
        jti="test_jti",
        token_type="Bearer",
        access_token="test_access",
        refresh_token="test_refresh",
        expires_in=3600,
        refresh_token_expires_in=7200,
        expires_at=int(time.time() + 3600),
        refresh_token_expires_at=int(time.time() + 7200),
    )

    import garth.sso
    monkeypatch.setattr(
        garth.sso, "login", lambda *a, **kw: (mock_oauth1, mock_oauth2)
    )

    def mock_input(prompt):
        if "Email" in prompt:
            return "user@example.com"
        return ""

    monkeypatch.setattr(sys, "argv", ["garth", "login"])
    monkeypatch.setattr(builtins, "input", mock_input)
    monkeypatch.setattr(getpass, "getpass", lambda _: "correct_password")
    main()
    out, err = capsys.readouterr()
    assert out  # Should print base64 token
    assert not err
