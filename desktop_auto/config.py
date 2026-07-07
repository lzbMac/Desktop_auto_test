from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class AutomationConfig:
    bundle_id: str
    app_path: str
    selectors: dict[str, str]
    launch_timeout_seconds: int = 30
    default_timeout_seconds: int = 60
    task_timeout_seconds: int = 60
    test_media: dict[str, str] | None = None

    @property
    def can_launch_app(self) -> bool:
        return bool(self.bundle_id or self.app_path)

    def selector(self, name: str) -> str:
        try:
            return self.selectors[name]
        except KeyError as error:
            raise KeyError(f"Missing selector in config: {name}") from error


def load_config(path: Path) -> AutomationConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    app = payload.get("app", {})
    return AutomationConfig(
        bundle_id=str(app.get("bundle_id", "")),
        app_path=str(app.get("app_path", "")),
        launch_timeout_seconds=int(app.get("launch_timeout_seconds", 30)),
        default_timeout_seconds=int(payload.get("default_timeout_seconds", 60)),
        task_timeout_seconds=int(payload.get("task_timeout_seconds", 60)),
        test_media={str(key): str(value) for key, value in payload.get("test_media", {}).items()},
        selectors={str(key): str(value) for key, value in payload.get("selectors", {}).items()},
    )
