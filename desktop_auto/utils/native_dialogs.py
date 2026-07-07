from pathlib import Path
from time import monotonic
from time import sleep as default_sleep
from typing import Any

_COMMAND = 1 << 4
_SHIFT = 1 << 1


def choose_file_in_open_dialog(
    driver: Any,
    path: Path,
    sleep=default_sleep,
) -> None:
    _go_to_path_in_open_dialog(driver, path.parent, sleep=sleep)
    file_item = _wait_for_element(
        driver,
        "xpath",
        f'//XCUIElementTypeCell[.//XCUIElementTypeTextField[@value="{path.name}"] or '
        f'.//XCUIElementTypeStaticText[@value="{path.name}"]]',
        timeout_seconds=5,
        sleep=sleep,
        message=f"File did not appear in open dialog: {path}",
    )
    file_item.click()
    driver.find_element("accessibility id", "OKButton").click()


def choose_folder_in_open_dialog(
    driver: Any,
    path: Path,
    sleep=default_sleep,
) -> None:
    choose_path_in_open_dialog(driver, path, sleep=sleep)


def choose_path_in_open_dialog(
    driver: Any,
    path: Path,
    sleep=default_sleep,
) -> None:
    _go_to_path_in_open_dialog(driver, path, sleep=sleep)
    driver.execute_script("macos: keys", {"keys": ["XCUIKeyboardKeyEnter"]})


def _go_to_path_in_open_dialog(
    driver: Any,
    path: Path,
    sleep=default_sleep,
) -> None:
    driver.execute_script("macos: keys", {"keys": [{"key": "g", "modifierFlags": _SHIFT | _COMMAND}]})
    sleep(0.5)
    path_field = _wait_for_element(
        driver,
        "accessibility id",
        "PathTextField",
        timeout_seconds=3,
        sleep=sleep,
        message="Go to path field did not appear in open dialog",
    )
    path_field.click()
    path_field.clear()
    path_field.send_keys(str(path))
    driver.execute_script("macos: keys", {"keys": ["XCUIKeyboardKeyEnter"]})
    sleep(0.5)


def _wait_for_element(
    driver: Any,
    strategy: str,
    value: str,
    timeout_seconds: float,
    sleep=default_sleep,
    message: str | None = None,
) -> Any:
    deadline = monotonic() + timeout_seconds
    last_error = None
    while True:
        try:
            return driver.find_element(strategy, value)
        except Exception as error:
            last_error = error
        if monotonic() >= deadline:
            raise RuntimeError(message or f"Element not found: {strategy}={value}") from last_error
        sleep(0.2)
