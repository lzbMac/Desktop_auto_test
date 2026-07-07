from desktop_auto.utils.macos_session import is_console_locked


class FakeRunResult:
    def __init__(self, stdout):
        self.stdout = stdout


def test_is_console_locked_accepts_io_console_locked(monkeypatch):
    monkeypatch.setattr(
        "desktop_auto.utils.macos_session.subprocess.run",
        lambda *args, **kwargs: FakeRunResult('"IOConsoleLocked" = Yes'),
    )

    assert is_console_locked()


def test_is_console_locked_accepts_cg_session_screen_locked(monkeypatch):
    monkeypatch.setattr(
        "desktop_auto.utils.macos_session.subprocess.run",
        lambda *args, **kwargs: FakeRunResult('"CGSessionScreenIsLocked"=Yes'),
    )

    assert is_console_locked()


def test_is_console_locked_rejects_unlocked_session(monkeypatch):
    monkeypatch.setattr(
        "desktop_auto.utils.macos_session.subprocess.run",
        lambda *args, **kwargs: FakeRunResult('"IOConsoleLocked" = No'),
    )

    assert not is_console_locked()
