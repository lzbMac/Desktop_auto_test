from dataclasses import dataclass
from pathlib import Path
import shutil


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @property
    def outputs_dir(self) -> Path:
        return self.root / "outputs"

    @property
    def reports_dir(self) -> Path:
        return self.root / "reports"

    @property
    def screenshots_dir(self) -> Path:
        return self.root / "screenshots"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def test_data_dir(self) -> Path:
        return self.root / "test_data"

    def ensure_runtime_dirs(self) -> None:
        for directory in (
            self.outputs_dir,
            self.reports_dir,
            self.screenshots_dir,
            self.logs_dir,
            self.test_data_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def clean_outputs(self) -> None:
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        for path in self.outputs_dir.iterdir():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    def test_data(self, filename: str) -> Path:
        return self.test_data_dir / filename
