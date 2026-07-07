import re
from pathlib import Path

from desktop_auto.pages.base_page import BasePage
from desktop_auto.utils.native_dialogs import choose_file_in_open_dialog
from desktop_auto.utils.wait import wait_until


class LoginRequiredError(RuntimeError):
    pass


class MainWindow(BasePage):
    def wait_until_ready(self, timeout_seconds: int = 30) -> None:
        wait_until(
            lambda: self.find_optional_by_selector_name("main_window"),
            timeout_seconds=timeout_seconds,
            message="Main window did not appear",
        )

    def open_import_dialog(self) -> None:
        self.click("import_button")

    def import_file(self, path: Path, timeout_seconds: int) -> None:
        self.clear_file_list_if_present(timeout_seconds)
        self.open_import_dialog()
        choose_file_in_open_dialog(self.driver, path)
        self.wait_until_file_list_has_content(timeout_seconds, filename=path.name)

    def clear_file_list_if_present(self, timeout_seconds: int = 5) -> None:
        clear_button = None
        for strategy, value in [
            ("-ios predicate string", "title == '清空列表' AND enabled == 1"),
            ("xpath", "//XCUIElementTypeButton[@title='清空列表' and @enabled='true']"),
        ]:
            try:
                clear_button = self.driver.find_element(strategy, value)
                break
            except Exception:
                continue
        if clear_button is None:
            return
        clear_button.click()
        self._confirm_clear_file_list_if_present()
        self._wait_until_file_list_is_empty(timeout_seconds)

    def wait_until_file_list_has_content(self, timeout_seconds: int, filename: str | None = None) -> None:
        wait_until(
            lambda: self._has_imported_file(filename),
            timeout_seconds=timeout_seconds,
            message="Imported file list did not appear",
        )

    def _has_imported_file(self, filename: str | None = None) -> bool:
        page_source = self.driver.page_source
        has_non_empty_file_list = bool(re.search(r"文件列表（[1-9]\d*）", page_source))
        if not filename:
            if self.find_optional_by_selector_name("file_list"):
                return True
            return has_non_empty_file_list
        return has_non_empty_file_list and filename in page_source

    def _confirm_clear_file_list_if_present(self) -> None:
        try:
            self.find_by_accessibility_token("btnConfirmHighRiskAction").click()
            return
        except Exception:
            pass
        for strategy, value in [
            ("-ios predicate string", "title == 'Clear List' AND enabled == 1"),
            ("-ios predicate string", "title == '清空列表' AND enabled == 1"),
            ("xpath", "//XCUIElementTypeButton[@title='Clear List' and @enabled='true']"),
            ("xpath", "//XCUIElementTypeButton[@title='清空列表' and @enabled='true']"),
        ]:
            try:
                self.driver.find_element(strategy, value).click()
                return
            except Exception:
                continue

    def _wait_until_file_list_is_empty(self, timeout_seconds: int) -> None:
        wait_until(
            lambda: not self._has_imported_file(),
            timeout_seconds=timeout_seconds,
            message="Imported file list was not cleared",
        )

    def open_convert_tab(self) -> None:
        self._open_tool_tab("convert_tab")

    def open_compress_tab(self) -> None:
        self._open_tool_tab("compress_tab")

    def open_audio_tab(self) -> None:
        self._open_tool_tab("audio_tab")

    def open_gif_tab(self) -> None:
        self._open_tool_tab("gif_tab")

    def start_task(self) -> None:
        self.click("start_button")
        self._raise_if_login_required()

    def current_task_status(self) -> str:
        return self.find_by_selector_name("task_status").text

    def _open_tool_tab(self, selector_name: str) -> None:
        self.click(selector_name)
        self._raise_if_login_required()

    def _raise_if_login_required(self) -> None:
        page_source = self.driver.page_source
        if "DesktopAccessDialog" in page_source or "请先在浏览器中完成登录" in page_source:
            raise LoginRequiredError(
                "VideoBee requires browser login before opening this workflow. "
                "Log in with the test account, then rerun the desktop E2E suite."
            )
