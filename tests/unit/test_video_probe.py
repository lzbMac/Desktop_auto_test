import pytest

from desktop_auto.utils.video_probe import (
    MediaInfo,
    StreamInfo,
    assert_duration_close,
    assert_has_no_audio_stream,
    assert_has_no_video_stream,
    assert_is_format,
)


def test_media_info_from_ffprobe_json_extracts_stream_counts():
    payload = {
        "format": {
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "duration": "5.120000",
            "size": "1024",
        },
        "streams": [
            {
                "codec_type": "video",
                "width": 1280,
                "height": 720,
                "avg_frame_rate": "30/1",
                "nb_frames": "154",
            },
            {"codec_type": "audio"},
        ],
    }

    info = MediaInfo.from_ffprobe_json(payload)

    assert info.format_name == "mov,mp4,m4a,3gp,3g2,mj2"
    assert info.duration == 5.12
    assert info.size == 1024
    assert info.video_stream_count == 1
    assert info.audio_stream_count == 1
    assert info.primary_video == StreamInfo(
        codec_type="video",
        width=1280,
        height=720,
        avg_frame_rate="30/1",
        nb_frames=154,
    )


def test_media_info_identifies_gif_format():
    info = MediaInfo(format_name="gif", duration=2.0, size=512, streams=[])

    assert info.is_format("gif")


def test_media_info_treats_asf_container_as_wmv_format():
    info = MediaInfo(format_name="asf", duration=2.0, size=512, streams=[])

    assert info.is_format("wmv")


def test_media_info_treats_matroska_container_as_mkv_format():
    info = MediaInfo(format_name="matroska,webm", duration=2.0, size=512, streams=[])

    assert info.is_format("mkv")


def test_assert_is_format_rejects_wrong_format():
    info = MediaInfo(format_name="mov,mp4,m4a,3gp,3g2,mj2", duration=2.0, size=512, streams=[])

    with pytest.raises(AssertionError, match="Expected media format"):
        assert_is_format(info, "gif")


def test_assert_has_no_audio_stream_rejects_audio_stream():
    info = MediaInfo(
        format_name="gif",
        duration=2.0,
        size=512,
        streams=[StreamInfo(codec_type="video"), StreamInfo(codec_type="audio")],
    )

    with pytest.raises(AssertionError, match="Expected no audio stream"):
        assert_has_no_audio_stream(info)


def test_assert_has_no_video_stream_rejects_video_stream():
    info = MediaInfo(
        format_name="mp3",
        duration=2.0,
        size=512,
        streams=[StreamInfo(codec_type="video"), StreamInfo(codec_type="audio")],
    )

    with pytest.raises(AssertionError, match="Expected no video stream"):
        assert_has_no_video_stream(info)


def test_assert_duration_close_accepts_small_difference():
    assert_duration_close(actual=5.8, expected=5.1, tolerance_seconds=1.0)


def test_assert_duration_close_rejects_large_difference():
    try:
        assert_duration_close(actual=8.5, expected=5.1, tolerance_seconds=1.0)
    except AssertionError as error:
        assert "duration differs" in str(error)
    else:
        raise AssertionError("Expected duration assertion to fail")
