from pathlib import Path

from desktop_auto.pages.base_page import BasePage
from desktop_auto.utils.native_dialogs import choose_folder_in_open_dialog
from desktop_auto.utils.wait import wait_until


class MediaPanel(BasePage):
    def choose_output_format(self, format_name: str) -> None:
        try:
            self.find_by_accessibility_token(f"comboOutputFormat_{format_name.lower()}").click()
        except Exception:
            if "comboOutputFormat" not in self.driver.page_source:
                return
            raise

    def set_output_directory(self, output_dir: Path, timeout_seconds: int) -> None:
        output_control = self.find_by_accessibility_token("comboOutputLocation_control")
        output_control.click()
        self.find_by_accessibility_token("comboOutputLocation_choose_folder").click()
        choose_folder_in_open_dialog(self.driver, output_dir)
        wait_until(
            lambda: str(output_dir) in self._selected_output_directory(),
            timeout_seconds=timeout_seconds,
            message=f"Output directory was not selected: {output_dir}",
        )

    def _selected_output_directory(self) -> str:
        control = self.find_by_accessibility_token("comboOutputLocation_control")
        return control.get_attribute("title") or control.get_attribute("value") or ""

    def wait_for_output_file(self, output_path: Path, timeout_seconds: int) -> Path:
        return wait_until(
            lambda: output_path if output_path.exists() and output_path.stat().st_size > 0 else None,
            timeout_seconds=timeout_seconds,
            message=f"Output file was not created: {output_path}",
        )
