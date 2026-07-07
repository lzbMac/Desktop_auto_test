from pathlib import Path

from desktop_auto.utils.media_factory import MediaFactory


class FakeRunner:
    def __init__(self):
        self.commands = []

    def __call__(self, command):
        self.commands.append(command)
        output = Path(command[-1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"media")


def test_media_factory_generates_missing_mp4_mov_and_mkv(tmp_path):
    runner = FakeRunner()
    factory = MediaFactory(tmp_path, runner=runner)

    media = factory.ensure_default_media()

    assert media.mp4 == tmp_path / "sample.mp4"
    assert media.mov == tmp_path / "sample.mov"
    assert media.mkv == tmp_path / "sample.mkv"
    assert media.mp4.read_bytes() == b"media"
    assert media.mov.read_bytes() == b"media"
    assert media.mkv.read_bytes() == b"media"
    assert len(runner.commands) == 3


def test_media_factory_does_not_regenerate_existing_files(tmp_path):
    (tmp_path / "sample.mp4").write_bytes(b"mp4")
    (tmp_path / "sample.mov").write_bytes(b"mov")
    (tmp_path / "sample.mkv").write_bytes(b"mkv")
    runner = FakeRunner()
    factory = MediaFactory(tmp_path, runner=runner)

    media = factory.ensure_default_media()

    assert media.mp4.read_bytes() == b"mp4"
    assert media.mov.read_bytes() == b"mov"
    assert media.mkv.read_bytes() == b"mkv"
    assert runner.commands == []
