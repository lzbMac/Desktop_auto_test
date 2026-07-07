from dataclasses import dataclass
from pathlib import Path
import subprocess
from collections.abc import Callable


@dataclass(frozen=True)
class TestMedia:
    mp4: Path
    mov: Path
    mkv: Path


class MediaFactory:
    def __init__(
        self,
        media_dir: Path,
        duration_seconds: int = 3,
        runner: Callable[[list[str]], None] | None = None,
    ):
        self.media_dir = media_dir
        self.duration_seconds = duration_seconds
        self.runner = runner or self._run

    def ensure_default_media(self) -> TestMedia:
        self.media_dir.mkdir(parents=True, exist_ok=True)
        mp4 = self.media_dir / "sample.mp4"
        mov = self.media_dir / "sample.mov"
        mkv = self.media_dir / "sample.mkv"
        if not mp4.exists():
            self.runner(self._ffmpeg_command(mp4))
        if not mov.exists():
            self.runner(self._ffmpeg_command(mov))
        if not mkv.exists():
            self.runner(self._ffmpeg_command(mkv))
        return TestMedia(mp4=mp4, mov=mov, mkv=mkv)

    def _ffmpeg_command(self, output_path: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"testsrc=size=320x240:rate=24:duration={self.duration_seconds}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=1000:duration={self.duration_seconds}",
            "-shortest",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]

    @staticmethod
    def _run(command: list[str]) -> None:
        subprocess.run(command, check=True, capture_output=True, text=True)
