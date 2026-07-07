import subprocess
import re


def is_console_locked() -> bool:
    result = subprocess.run(
        ["ioreg", "-n", "Root", "-d1"],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(
        re.search(r"IOConsoleLocked\"?\s*=\s*Yes", result.stdout)
        or re.search(r"CGSessionScreenIsLocked\"?\s*=\s*Yes", result.stdout)
    )
