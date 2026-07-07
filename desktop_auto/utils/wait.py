from time import monotonic, sleep
from typing import Callable, TypeVar


T = TypeVar("T")


def wait_until(
    condition: Callable[[], T | None | bool],
    timeout_seconds: float,
    interval_seconds: float = 0.5,
    message: str = "condition was not met",
) -> T:
    deadline = monotonic() + timeout_seconds
    last_value = None
    while monotonic() < deadline:
        last_value = condition()
        if last_value:
            return last_value
        sleep(interval_seconds)
    raise TimeoutError(message)
