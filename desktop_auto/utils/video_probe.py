from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
from typing import Any


FORMAT_ALIASES = {
    "mkv": {"matroska"},
    "wmv": {"asf"},
}


@dataclass(frozen=True)
class StreamInfo:
    codec_type: str
    width: int | None = None
    height: int | None = None
    avg_frame_rate: str | None = None
    nb_frames: int | None = None


@dataclass(frozen=True)
class MediaInfo:
    format_name: str
    duration: float
    size: int
    streams: list[StreamInfo]

    @classmethod
    def from_ffprobe_json(cls, payload: dict[str, Any]) -> "MediaInfo":
        raw_format = payload.get("format", {})
        streams = [
            StreamInfo(
                codec_type=str(stream.get("codec_type", "")),
                width=_optional_int(stream.get("width")),
                height=_optional_int(stream.get("height")),
                avg_frame_rate=stream.get("avg_frame_rate"),
                nb_frames=_optional_int(stream.get("nb_frames")),
            )
            for stream in payload.get("streams", [])
        ]
        return cls(
            format_name=str(raw_format.get("format_name", "")),
            duration=float(raw_format.get("duration", 0) or 0),
            size=int(raw_format.get("size", 0) or 0),
            streams=streams,
        )

    @property
    def video_stream_count(self) -> int:
        return sum(1 for stream in self.streams if stream.codec_type == "video")

    @property
    def audio_stream_count(self) -> int:
        return sum(1 for stream in self.streams if stream.codec_type == "audio")

    @property
    def primary_video(self) -> StreamInfo | None:
        return next((stream for stream in self.streams if stream.codec_type == "video"), None)

    def is_format(self, expected: str) -> bool:
        expected_name = expected.lower()
        accepted_names = {expected_name, *FORMAT_ALIASES.get(expected_name, set())}
        return bool(accepted_names.intersection(self.format_name.lower().split(",")))


def probe_media(path: Path) -> MediaInfo:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return MediaInfo.from_ffprobe_json(json.loads(result.stdout))


def assert_duration_close(actual: float, expected: float, tolerance_seconds: float = 1.0) -> None:
    diff = abs(actual - expected)
    if diff > tolerance_seconds:
        raise AssertionError(
            f"Media duration differs by {diff:.3f}s, expected <= {tolerance_seconds:.3f}s"
        )


def assert_has_video_stream(info: MediaInfo) -> None:
    if info.video_stream_count < 1:
        raise AssertionError("Expected at least one video stream")


def assert_has_audio_stream(info: MediaInfo) -> None:
    if info.audio_stream_count < 1:
        raise AssertionError("Expected at least one audio stream")


def assert_has_no_audio_stream(info: MediaInfo) -> None:
    if info.audio_stream_count > 0:
        raise AssertionError("Expected no audio stream")


def assert_has_no_video_stream(info: MediaInfo) -> None:
    if info.video_stream_count > 0:
        raise AssertionError("Expected no video stream")


def assert_is_format(info: MediaInfo, expected: str) -> None:
    if not info.is_format(expected):
        raise AssertionError(f"Expected media format {expected}, got {info.format_name}")


def assert_is_animated_gif(info: MediaInfo) -> None:
    assert_is_format(info, "gif")
    assert_has_video_stream(info)
    video = info.primary_video
    if video is None or video.nb_frames is None or video.nb_frames <= 1:
        raise AssertionError("Expected animated GIF with more than one frame")


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)
