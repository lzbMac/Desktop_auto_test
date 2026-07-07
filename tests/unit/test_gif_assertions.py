import pytest

from desktop_auto.utils.video_probe import MediaInfo, StreamInfo, assert_is_animated_gif


def test_assert_is_animated_gif_accepts_multiple_frames():
    info = MediaInfo(
        format_name="gif",
        duration=2.0,
        size=512,
        streams=[StreamInfo(codec_type="video", width=320, height=180, nb_frames=12)],
    )

    assert_is_animated_gif(info)


def test_assert_is_animated_gif_rejects_single_frame():
    info = MediaInfo(
        format_name="gif",
        duration=2.0,
        size=512,
        streams=[StreamInfo(codec_type="video", width=320, height=180, nb_frames=1)],
    )

    with pytest.raises(AssertionError, match="Expected animated GIF"):
        assert_is_animated_gif(info)
