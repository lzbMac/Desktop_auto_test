from __future__ import annotations

from dataclasses import dataclass

from desktop_auto.config import AutomationConfig


@dataclass(frozen=True)
class AppiumServer:
    url: str = "http://127.0.0.1:4723"


def create_macos_driver(config: AutomationConfig, server: AppiumServer | None = None):
    if not config.can_launch_app:
        raise ValueError("Set app.bundle_id or app.app_path in config/test_config.json")

    try:
        from appium import webdriver
        from appium.options.common import AppiumOptions
    except ImportError as error:
        raise RuntimeError("Install Appium Python client with: pip install Appium-Python-Client") from error

    options = AppiumOptions()
    options.set_capability("platformName", "Mac")
    options.set_capability("appium:automationName", "Mac2")
    options.set_capability("appium:showServerLogs", True)
    options.set_capability("appium:newCommandTimeout", max(config.task_timeout_seconds + 30, 90))
    if config.bundle_id:
        options.set_capability("appium:bundleId", config.bundle_id)
    if config.app_path:
        options.set_capability("appium:appPath", config.app_path)

    appium_server = server or AppiumServer()
    driver = webdriver.Remote(appium_server.url, options=options)
    driver.implicitly_wait(1)
    return driver
