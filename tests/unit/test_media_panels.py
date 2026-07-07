from pathlib import Path

import pytest

from desktop_auto.config import AutomationConfig
from desktop_auto.pages.media_panels import MediaPanel


class FakeElement:
    def __init__(self, attributes=None):
        self.clicked = False
        self.attributes = attributes or {}

    def click(self):
        self.clicked = True

    def get_attribute(self, name):
        return self.attributes.get(name)


class FakeDriver:
    def __init__(self, results, page_source=""):
        self.results = results
        self.page_source = page_source
        self.calls = []

    def find_element(self, strategy, value):
        self.calls.append((strategy, value))
        result = self.results.get((strategy, value))
        if result is None:
            raise RuntimeError("not found")
        return result


def test_choose_output_format_clicks_target_format_option_directly():
    element = FakeElement()
    driver = FakeDriver(
        {
            (
                "-ios predicate string",
                "identifier == 'comboOutputFormat_mov' OR identifier ENDSWITH '.comboOutputFormat_mov' OR identifier CONTAINS '.comboOutputFormat_mov.'",
            ): element
        },
        page_source="comboOutputFormat",
    )
    panel = MediaPanel(driver, AutomationConfig(bundle_id="", app_path="", selectors={}))

    panel.choose_output_format("mov")

    assert element.clicked


def test_choose_output_format_skips_when_current_panel_has_no_format_controls():
    driver = FakeDriver({}, page_source="视频转 GIF 输出预览")
    panel = MediaPanel(driver, AutomationConfig(bundle_id="", app_path="", selectors={}))

    panel.choose_output_format("gif")


def test_set_output_directory_chooses_other_folder_and_selects_directory(monkeypatch):
    output_control = FakeElement({"title": "/tmp/case"})
    choose_folder = FakeElement()
    selected_paths = []
    driver = FakeDriver(
        {
            (
                "-ios predicate string",
                "identifier == 'comboOutputLocation_control' OR identifier ENDSWITH '.comboOutputLocation_control' OR identifier CONTAINS '.comboOutputLocation_control.'",
            ): output_control,
            (
                "-ios predicate string",
                "identifier == 'comboOutputLocation_choose_folder' OR identifier ENDSWITH '.comboOutputLocation_choose_folder' OR identifier CONTAINS '.comboOutputLocation_choose_folder.'",
            ): choose_folder,
        },
        page_source="/tmp/case",
    )
    panel = MediaPanel(driver, AutomationConfig(bundle_id="", app_path="", selectors={}))

    monkeypatch.setattr(
        "desktop_auto.pages.media_panels.choose_folder_in_open_dialog",
        lambda driver_arg, path: selected_paths.append((driver_arg, path)),
    )

    panel.set_output_directory(Path("/tmp/case"), 0.01)

    assert output_control.clicked
    assert choose_folder.clicked
    assert selected_paths == [(driver, Path("/tmp/case"))]


def test_set_output_directory_checks_selected_control_value_not_any_page_text(monkeypatch):
    output_control = FakeElement({"title": "/Users/lizhengbing/Movies/Audio Cut/Converted"})
    choose_folder = FakeElement()
    driver = FakeDriver(
        {
            (
                "-ios predicate string",
                "identifier == 'comboOutputLocation_control' OR identifier ENDSWITH '.comboOutputLocation_control' OR identifier CONTAINS '.comboOutputLocation_control.'",
            ): output_control,
            (
                "-ios predicate string",
                "identifier == 'comboOutputLocation_choose_folder' OR identifier ENDSWITH '.comboOutputLocation_choose_folder' OR identifier CONTAINS '.comboOutputLocation_choose_folder.'",
            ): choose_folder,
        },
        page_source="/tmp/case",
    )
    panel = MediaPanel(driver, AutomationConfig(bundle_id="", app_path="", selectors={}))

    monkeypatch.setattr(
        "desktop_auto.pages.media_panels.choose_folder_in_open_dialog",
        lambda driver_arg, path: None,
    )

    with pytest.raises(TimeoutError, match="Output directory was not selected"):
        panel.set_output_directory(Path("/tmp/case"), 0.01)
