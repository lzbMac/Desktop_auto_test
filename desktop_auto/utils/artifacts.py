from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from desktop_auto.utils.paths import ProjectPaths


@dataclass(frozen=True)
class FailureArtifacts:
    screenshot_path: Path
    page_source_path: Path


def capture_failure_artifacts(driver: Any, paths: ProjectPaths, test_id: str) -> FailureArtifacts:
    paths.ensure_runtime_dirs()
    safe_name = _safe_filename(test_id)
    screenshot_path = paths.screenshots_dir / f"{safe_name}.png"
    page_source_path = paths.logs_dir / f"{safe_name}.xml"

    driver.save_screenshot(str(screenshot_path))
    page_source_path.write_text(str(driver.page_source), encoding="utf-8")

    return FailureArtifacts(
        screenshot_path=screenshot_path,
        page_source_path=page_source_path,
    )


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")
