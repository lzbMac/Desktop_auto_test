import pytest

from desktop_auto.pages.main_window import MainWindow


@pytest.mark.smoke
@pytest.mark.core
def test_app_launches(macos_driver, automation_config):
    main_window = MainWindow(macos_driver, automation_config)

    main_window.wait_until_ready(automation_config.launch_timeout_seconds)
