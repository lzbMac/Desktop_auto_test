import pytest

from desktop_auto.utils.file_assert import assert_file_size_at_most_ratio
from desktop_auto.utils.video_probe import (
    assert_duration_close,
    assert_has_audio_stream,
    assert_has_video_stream,
    assert_is_format,
    probe_media,
)
from tests.e2e.workflow_helpers import output_path, prepare_input, run_workflow


@pytest.mark.core
@pytest.mark.compress
def test_video_compress_end_to_end(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mov, "video_compress", "video_compress.mov")
    output = output_path(project_paths, "video_compress", "video_compress.mp4")

    run_workflow(macos_driver, automation_config, source, lambda page: page.open_compress_tab(), "mp4", output)

    source_info = probe_media(source)
    output_info = probe_media(output)
    assert_is_format(output_info, "mp4")
    assert_has_video_stream(output_info)
    assert_has_audio_stream(output_info)
    assert_duration_close(output_info.duration, source_info.duration)
    assert_file_size_at_most_ratio(output, source, max_ratio=2.0)
