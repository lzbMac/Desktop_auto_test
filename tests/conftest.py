from pathlib import Path
import os

import pytest

from desktop_auto.config import load_config
from desktop_auto.utils.artifacts import capture_failure_artifacts
from desktop_auto.utils.app_runner import create_macos_driver
from desktop_auto.utils.macos_session import is_console_locked
from desktop_auto.utils.media_factory import MediaFactory
from desktop_auto.utils.paths import ProjectPaths


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project_paths():
    paths = ProjectPaths(PROJECT_ROOT)
    paths.ensure_runtime_dirs()
    return paths


@pytest.fixture(scope="session")
def default_test_media():
    paths = ProjectPaths(PROJECT_ROOT)
    paths.ensure_runtime_dirs()
    return MediaFactory(paths.test_data_dir).ensure_default_media()


@pytest.fixture(scope="session")
def automation_config():
    config_path = Path(os.environ.get("AUTOMATION_CONFIG", PROJECT_ROOT / "config" / "test_config.json"))
    if not config_path.exists():
        pytest.skip(f"Missing automation config: {config_path}")
    return load_config(config_path)


@pytest.fixture
def macos_driver(automation_config):
    if os.environ.get("RUN_DESKTOP_E2E") != "1":
        pytest.skip("Set RUN_DESKTOP_E2E=1 to run desktop UI tests")
    if is_console_locked():
        pytest.skip("macOS desktop is locked; unlock the test machine before running desktop UI automation")
    driver = create_macos_driver(automation_config)
    yield driver
    try:
        driver.quit()
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    driver = item.funcargs.get("macos_driver")
    paths = item.funcargs.get("project_paths")
    if driver is None or paths is None:
        return
    try:
        capture_failure_artifacts(driver, paths, item.nodeid)
    except Exception as error:
        report.sections.append(("artifact capture failed", str(error)))
