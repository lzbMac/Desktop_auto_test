import pytest

from desktop_auto.utils.video_probe import (
    assert_duration_close,
    assert_is_animated_gif,
    probe_media,
)
from tests.e2e.workflow_helpers import output_path, prepare_input, run_workflow


@pytest.mark.core
@pytest.mark.gif
def test_video_to_gif_end_to_end(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mp4, "video_to_gif", "video_to_gif.mp4")
    output = output_path(project_paths, "video_to_gif", "video_to_gif.gif")

    run_workflow(macos_driver, automation_config, source, lambda page: page.open_gif_tab(), "gif", output)

    source_info = probe_media(source)
    output_info = probe_media(output)
    assert_is_animated_gif(output_info)
    assert_duration_close(output_info.duration, source_info.duration)
