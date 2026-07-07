from pathlib import Path
from types import SimpleNamespace

import pytest

from desktop_auto.pages.main_window import LoginRequiredError
from tests.e2e import workflow_helpers


class FakeMainWindow:
    def __init__(self, driver, config):
        driver.events.append("main_window")
        self.driver = driver

    def wait_until_ready(self, timeout_seconds):
        self.driver.events.append(("ready", timeout_seconds))

    def import_file(self, source, timeout_seconds):
        self.driver.events.append(("import", source, timeout_seconds))

    def start_task(self):
        self.driver.events.append("start")


class FakeMediaPanel:
    def __init__(self, driver, config):
        driver.events.append("media_panel")
        self.driver = driver

    def choose_output_format(self, output_format):
        self.driver.events.append(("format", output_format))

    def set_output_directory(self, output_dir, timeout_seconds):
        self.driver.events.append(("output_dir", output_dir, timeout_seconds))


class FakeDriver:
    def __init__(self):
        self.events = []


class FakeConfig:
    launch_timeout_seconds = 3
    default_timeout_seconds = 5
    task_timeout_seconds = 7


class LoginRequiredMainWindow(FakeMainWindow):
    def start_task(self):
        raise LoginRequiredError("login required")


def test_run_workflow_sets_output_directory_before_starting_task(monkeypatch, tmp_path):
    driver = FakeDriver()
    source = tmp_path / "case" / "input.mp4"
    expected_output = tmp_path / "case" / "input.mov"
    expected_output.parent.mkdir()
    expected_output.write_bytes(b"media")

    monkeypatch.setattr(workflow_helpers, "MainWindow", FakeMainWindow)
    monkeypatch.setattr(workflow_helpers, "MediaPanel", FakeMediaPanel)
    wait_events = []

    def wait_until_spy(condition, timeout_seconds, message):
        wait_events.append(("wait_output", timeout_seconds, message))
        return condition()

    monkeypatch.setattr(workflow_helpers, "wait_until", wait_until_spy)

    workflow_helpers.run_workflow(
        driver,
        FakeConfig(),
        source,
        lambda page: driver.events.append("open_tab"),
        "mov",
        expected_output,
    )

    assert driver.events == [
        "main_window",
        "media_panel",
        ("ready", 3),
        "open_tab",
        ("import", source, 5),
        ("format", "mov"),
        ("output_dir", Path(expected_output.parent), 5),
        "start",
    ]
    assert wait_events == [
        ("wait_output", 7, f"Output file was not created: {expected_output}"),
    ]


def test_prepare_input_uses_short_runtime_input_directory(monkeypatch, tmp_path):
    project_paths = SimpleNamespace(outputs_dir=tmp_path / "outputs")
    input_root = tmp_path / "runtime_inputs"
    monkeypatch.setenv("DESKTOP_AUTO_INPUT_ROOT", str(input_root))
    sample = tmp_path / "sample.mp4"
    sample.write_bytes(b"media")

    source = workflow_helpers.prepare_input(project_paths, sample, "audio_extract", "audio_extract.mp4")

    output_dir = project_paths.outputs_dir / "audio_extract"
    assert source == input_root / "audio_extract" / "audio_extract.mp4"
    assert source.read_bytes() == b"media"
    assert output_dir.is_dir()
    assert list(output_dir.iterdir()) == []


def test_output_path_uses_case_output_directory(tmp_path):
    project_paths = SimpleNamespace(outputs_dir=tmp_path / "outputs")

    output = workflow_helpers.output_path(project_paths, "audio_extract", "audio_extract.mp3")

    assert output == project_paths.outputs_dir / "audio_extract" / "audio_extract.mp3"


def test_run_workflow_skips_when_login_is_required(monkeypatch, tmp_path):
    driver = FakeDriver()
    source = tmp_path / "case" / "input.mp4"
    expected_output = tmp_path / "case" / "input.mov"
    expected_output.parent.mkdir()

    monkeypatch.setattr(workflow_helpers, "MainWindow", LoginRequiredMainWindow)
    monkeypatch.setattr(workflow_helpers, "MediaPanel", FakeMediaPanel)

    with pytest.raises(pytest.skip.Exception, match="login required"):
        workflow_helpers.run_workflow(
            driver,
            FakeConfig(),
            source,
            lambda page: driver.events.append("open_tab"),
            "mov",
            expected_output,
        )


def test_skip_if_login_required_runs_action_when_login_is_available():
    events = []

    workflow_helpers.skip_if_login_required(lambda: events.append("ran"))

    assert events == ["ran"]


def test_skip_if_login_required_skips_when_login_is_required():
    with pytest.raises(pytest.skip.Exception, match="login required"):
        workflow_helpers.skip_if_login_required(lambda: (_ for _ in ()).throw(LoginRequiredError("login required")))
