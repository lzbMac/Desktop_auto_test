import pytest

from desktop_auto.config import AutomationConfig
from desktop_auto.pages.main_window import LoginRequiredError, MainWindow


class FakeElement:
    def __init__(self, driver):
        self.driver = driver

    def click(self):
        self.driver.page_source = "DesktopAccessDialog 请先在浏览器中完成登录后再继续"


class FakeDriver:
    page_source = ""

    def find_element(self, strategy, value):
        return FakeElement(self)


class MissingSelectorDriver:
    def __init__(self, page_source):
        self.page_source = page_source

    def find_element(self, strategy, value):
        raise RuntimeError(f"missing selector: {strategy}={value}")


class StaleFileListDriver:
    def __init__(self):
        self.page_source = 'value="文件列表（1）" value="audio_extract.mp4"'

    def find_element(self, strategy, value):
        if value == "fileList":
            return object()
        raise RuntimeError(f"missing selector: {strategy}={value}")


class ClearListElement:
    def __init__(self, driver):
        self.driver = driver
        self.clicked = False

    def click(self):
        self.clicked = True
        self.driver.page_source = "文件列表（1） Clear the file list? Clear List"


class ConfirmClearListElement(ClearListElement):
    def click(self):
        self.clicked = True
        self.driver.page_source = "添加视频"


class ClearListDriver:
    def __init__(self):
        self.page_source = "文件列表（1）"
        self.clear_button = ClearListElement(self)
        self.confirm_button = ConfirmClearListElement(self)
        self.calls = []

    def find_element(self, strategy, value):
        self.calls.append((strategy, value))
        if "btnConfirmHighRiskAction" in value:
            return self.confirm_button
        if value == "title == '清空列表' AND enabled == 1":
            return self.clear_button
        if "title == 'Clear List'" in value:
            return self.confirm_button
        raise RuntimeError(f"missing selector: {strategy}={value}")


class XPathClearListDriver(ClearListDriver):
    def find_element(self, strategy, value):
        self.calls.append((strategy, value))
        if "btnConfirmHighRiskAction" in value:
            return self.confirm_button
        if strategy == "xpath" and value == "//XCUIElementTypeButton[@title='清空列表' and @enabled='true']":
            return self.clear_button
        if "title == 'Clear List'" in value:
            return self.confirm_button
        raise RuntimeError(f"missing selector: {strategy}={value}")


def test_open_tool_tab_reports_login_required():
    page = MainWindow(
        FakeDriver(),
        AutomationConfig(bundle_id="", app_path="", selectors={"convert_tab": "tabConvert"}),
    )

    with pytest.raises(LoginRequiredError, match="browser login"):
        page.open_convert_tab()


def test_start_task_reports_login_required():
    page = MainWindow(
        FakeDriver(),
        AutomationConfig(bundle_id="", app_path="", selectors={"start_button": "btnStart"}),
    )

    with pytest.raises(LoginRequiredError, match="browser login"):
        page.start_task()


def test_wait_until_file_list_accepts_imported_filename_in_app_file_list():
    page = MainWindow(
        MissingSelectorDriver('value="文件列表（1）" value="import_mp4.mp4"'),
        AutomationConfig(bundle_id="", app_path="", selectors={"file_list": "fileList"}),
    )

    page.wait_until_file_list_has_content(0.01, filename="import_mp4.mp4")


def test_wait_until_file_list_accepts_non_empty_file_count_in_page_source():
    page = MainWindow(
        MissingSelectorDriver("文件列表（1）"),
        AutomationConfig(bundle_id="", app_path="", selectors={"file_list": "fileList"}),
    )

    page.wait_until_file_list_has_content(0.01)


def test_wait_until_file_list_rejects_filename_while_open_panel_is_visible():
    page = MainWindow(
        MissingSelectorDriver('identifier="open-panel" value="audio_extract.mp4"'),
        AutomationConfig(bundle_id="", app_path="", selectors={"file_list": "fileList"}),
    )

    with pytest.raises(TimeoutError, match="Imported file list did not appear"):
        page.wait_until_file_list_has_content(0.01, filename="audio_extract.mp4")


def test_wait_until_file_list_rejects_stale_file_list_when_requested_filename_is_missing():
    page = MainWindow(
        StaleFileListDriver(),
        AutomationConfig(bundle_id="", app_path="", selectors={"file_list": "fileList"}),
    )

    with pytest.raises(TimeoutError, match="Imported file list did not appear"):
        page.wait_until_file_list_has_content(0.01, filename="import_mp4.mp4")


def test_clear_file_list_if_present_clicks_enabled_clear_button():
    driver = ClearListDriver()
    page = MainWindow(driver, AutomationConfig(bundle_id="", app_path="", selectors={"file_list": "fileList"}))

    page.clear_file_list_if_present()

    assert driver.clear_button.clicked
    assert driver.confirm_button.clicked
    assert driver.page_source == "添加视频"
    assert any(value == "btnConfirmHighRiskAction" for _, value in driver.calls)


def test_clear_file_list_if_present_falls_back_to_xpath():
    driver = XPathClearListDriver()
    page = MainWindow(driver, AutomationConfig(bundle_id="", app_path="", selectors={"file_list": "fileList"}))

    page.clear_file_list_if_present()

    assert driver.clear_button.clicked


def test_clear_file_list_if_present_skips_when_clear_button_is_missing():
    page = MainWindow(
        MissingSelectorDriver("添加视频"),
        AutomationConfig(bundle_id="", app_path="", selectors={"file_list": "fileList"}),
    )

    page.clear_file_list_if_present()
