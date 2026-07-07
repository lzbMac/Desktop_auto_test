from types import ModuleType, SimpleNamespace
import sys

from desktop_auto.config import AutomationConfig
from desktop_auto.utils.app_runner import AppiumServer, create_macos_driver


class FakeAppiumOptions:
    def __init__(self):
        self.capabilities = {}

    def set_capability(self, name, value):
        self.capabilities[name] = value


class FakeDriver:
    def __init__(self):
        self.implicit_waits = []

    def implicitly_wait(self, seconds):
        self.implicit_waits.append(seconds)


def test_create_macos_driver_keeps_session_alive_longer_than_task_timeout(monkeypatch):
    fake_driver = FakeDriver()
    created = {}

    def remote(url, options):
        created["url"] = url
        created["options"] = options
        return fake_driver

    appium_module = ModuleType("appium")
    appium_module.webdriver = SimpleNamespace(Remote=remote)
    options_module = ModuleType("appium.options")
    common_module = ModuleType("appium.options.common")
    common_module.AppiumOptions = FakeAppiumOptions

    monkeypatch.setitem(sys.modules, "appium", appium_module)
    monkeypatch.setitem(sys.modules, "appium.options", options_module)
    monkeypatch.setitem(sys.modules, "appium.options.common", common_module)

    config = AutomationConfig(
        bundle_id="io.audiocut.app",
        app_path="",
        selectors={},
        task_timeout_seconds=60,
    )

    driver = create_macos_driver(config, AppiumServer("http://127.0.0.1:4723"))

    assert driver is fake_driver
    assert created["options"].capabilities["appium:newCommandTimeout"] == 90
