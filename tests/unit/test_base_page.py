import pytest

from desktop_auto.config import AutomationConfig
from desktop_auto.pages.base_page import BasePage


class FakeDriver:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def find_element(self, strategy, value):
        self.calls.append((strategy, value))
        result = self.results.get((strategy, value))
        if result is None:
            raise RuntimeError("not found")
        return result


def test_find_by_selector_name_falls_back_to_identifier_suffix_predicate():
    element = object()
    driver = FakeDriver(
        {
            (
                "-ios predicate string",
                "identifier == 'tabConvert' OR identifier ENDSWITH '.tabConvert' OR identifier CONTAINS '.tabConvert.'",
            ): element
        }
    )
    page = BasePage(driver, AutomationConfig(bundle_id="", app_path="", selectors={"convert_tab": "tabConvert"}))

    assert page.find_by_selector_name("convert_tab") is element
    assert driver.calls == [
        ("accessibility id", "tabConvert"),
        ("name", "tabConvert"),
        (
            "-ios predicate string",
            "identifier == 'tabConvert' OR identifier ENDSWITH '.tabConvert' OR identifier CONTAINS '.tabConvert.'",
        ),
    ]


def test_find_by_selector_name_matches_qt_identifier_path_segment():
    element = object()
    driver = FakeDriver(
        {
            (
                "-ios predicate string",
                "identifier == 'mainWindow' OR identifier ENDSWITH '.mainWindow' OR identifier CONTAINS '.mainWindow.'",
            ): element
        }
    )
    page = BasePage(driver, AutomationConfig(bundle_id="", app_path="", selectors={"main": "mainWindow"}))

    assert page.find_by_selector_name("main") is element


def test_find_by_accessibility_token_uses_literal_token_without_config_lookup():
    element = object()
    driver = FakeDriver(
        {
            (
                "-ios predicate string",
                "identifier == 'comboOutputFormat_mov' OR identifier ENDSWITH '.comboOutputFormat_mov' OR identifier CONTAINS '.comboOutputFormat_mov.'",
            ): element
        }
    )
    page = BasePage(driver, AutomationConfig(bundle_id="", app_path="", selectors={}))

    assert page.find_by_accessibility_token("comboOutputFormat_mov") is element


def test_find_optional_by_selector_name_returns_none_when_all_strategies_fail():
    page = BasePage(FakeDriver({}), AutomationConfig(bundle_id="", app_path="", selectors={"main": "mainWindow"}))

    assert page.find_optional_by_selector_name("main") is None


def test_find_by_selector_name_raises_last_lookup_error_when_not_found():
    page = BasePage(FakeDriver({}), AutomationConfig(bundle_id="", app_path="", selectors={"main": "mainWindow"}))

    with pytest.raises(RuntimeError, match="not found"):
        page.find_by_selector_name("main")
