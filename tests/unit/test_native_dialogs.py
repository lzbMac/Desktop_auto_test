from unittest.mock import Mock
from pathlib import Path

from desktop_auto.utils.native_dialogs import choose_file_in_open_dialog, choose_folder_in_open_dialog


class FakeDriver:
    def __init__(self):
        self.scripts = []
        self.finds = []
        self.path_field = FakeElement()
        self.file_element = FakeElement()
        self.ok_button = FakeElement()

    def execute_script(self, script, payload):
        self.scripts.append((script, payload))

    def find_element(self, strategy, value):
        self.finds.append((strategy, value))
        if value == "PathTextField":
            return self.path_field
        if value == "OKButton":
            return self.ok_button
        return self.file_element


class FakeElement:
    def __init__(self):
        self.clicks = 0
        self.clear_calls = 0
        self.sent_keys = []

    def click(self):
        self.clicks += 1

    def clear(self):
        self.clear_calls += 1

    def send_keys(self, text):
        self.sent_keys.append(text)


def test_choose_file_in_open_dialog_uses_macos_keys_sequence():
    driver = FakeDriver()
    sleep = Mock()

    choose_file_in_open_dialog(driver, Path("/tmp/sample.mp4"), sleep=sleep)

    assert driver.scripts == [
        ("macos: keys", {"keys": [{"key": "g", "modifierFlags": 18}]}),
        ("macos: keys", {"keys": ["XCUIKeyboardKeyEnter"]}),
    ]
    assert driver.finds == [
        ("accessibility id", "PathTextField"),
        (
            "xpath",
            "//XCUIElementTypeCell[.//XCUIElementTypeTextField[@value=\"sample.mp4\"] or "
            ".//XCUIElementTypeStaticText[@value=\"sample.mp4\"]]",
        ),
        ("accessibility id", "OKButton"),
    ]
    assert driver.path_field.clicks == 1
    assert driver.path_field.clear_calls == 1
    assert driver.path_field.sent_keys == ["/tmp"]
    assert driver.file_element.clicks == 1
    assert driver.ok_button.clicks == 1
    assert sleep.call_args_list == [((0.5,),), ((0.5,),)]


def test_choose_file_in_open_dialog_waits_for_go_to_path_field_before_pasting():
    driver = FakeDriver()

    choose_file_in_open_dialog(driver, Path("/tmp/sample.mp4"), sleep=Mock())

    assert driver.finds[0] == ("accessibility id", "PathTextField")
    assert driver.scripts[0] == ("macos: keys", {"keys": [{"key": "g", "modifierFlags": 18}]})
    assert driver.path_field.sent_keys == ["/tmp"]


def test_choose_folder_in_open_dialog_uses_folder_path_directly():
    driver = FakeDriver()
    sleep = Mock()

    choose_folder_in_open_dialog(driver, Path("/tmp/output"), sleep=sleep)

    assert driver.scripts == [
        ("macos: keys", {"keys": [{"key": "g", "modifierFlags": 18}]}),
        ("macos: keys", {"keys": ["XCUIKeyboardKeyEnter"]}),
        ("macos: keys", {"keys": ["XCUIKeyboardKeyEnter"]}),
    ]
    assert driver.finds == [("accessibility id", "PathTextField")]
    assert driver.path_field.clear_calls == 1
    assert driver.path_field.sent_keys == ["/tmp/output"]
    assert sleep.call_args_list == [((0.5,),), ((0.5,),)]
