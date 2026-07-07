import pytest

from desktop_auto.utils.video_probe import (
    assert_duration_close,
    assert_has_audio_stream,
    assert_has_no_video_stream,
    assert_is_format,
    probe_media,
)
from tests.e2e.workflow_helpers import output_path, prepare_input, run_workflow


@pytest.mark.core
@pytest.mark.audio
def test_audio_extract_end_to_end(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mp4, "audio_extract", "audio_extract.mp4")
    output = output_path(project_paths, "audio_extract", "audio_extract.mp3")

    run_workflow(macos_driver, automation_config, source, lambda page: page.open_audio_tab(), "mp3", output)

    source_info = probe_media(source)
    output_info = probe_media(output)
    assert_is_format(output_info, "mp3")
    assert_has_audio_stream(output_info)
    assert_has_no_video_stream(output_info)
    assert_duration_close(output_info.duration, source_info.duration)
