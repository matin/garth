import builtins
import getpass
import sys

import pytest

from garth.cli import main


def test_help_flag(monkeypatch, capsys):
    # -h should print help and exit with code 0
    monkeypatch.setattr(sys, "argv", ["garth", "-h"])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0
    out, err = capsys.readouterr()
    assert "usage:" in out.lower()


def test_no_args_prints_help(monkeypatch, capsys):
    # No args should print help and not exit
    monkeypatch.setattr(sys, "argv", ["garth"])
    main()
    out, err = capsys.readouterr()
    assert "usage:" in out.lower()


@pytest.mark.vcr
def test_login_command(monkeypatch, capsys):
    def mock_input(prompt):
        match prompt:
            case "Email: ":
                return "user@example.com"
            case "MFA code: ":
                code = "023226"
                return code

    monkeypatch.setattr(sys, "argv", ["garth", "login"])
    monkeypatch.setattr(builtins, "input", mock_input)
    monkeypatch.setattr(getpass, "getpass", lambda _: "correct_password")
    main()
    out, err = capsys.readouterr()
    assert out
    assert not err
