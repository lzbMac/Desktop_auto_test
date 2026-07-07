import pytest

from desktop_auto.utils.video_probe import (
    assert_duration_close,
    assert_has_audio_stream,
    assert_has_video_stream,
    assert_is_format,
    probe_media,
)
from tests.e2e.workflow_helpers import output_path, prepare_input, run_workflow


@pytest.mark.core
@pytest.mark.convert
def test_mkv_to_mp4_end_to_end(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mkv, "mkv_to_mp4", "mkv_to_mp4.mkv")
    output = output_path(project_paths, "mkv_to_mp4", "mkv_to_mp4.mp4")

    run_workflow(macos_driver, automation_config, source, lambda page: page.open_convert_tab(), "mp4", output)

    source_info = probe_media(source)
    output_info = probe_media(output)
    assert_is_format(output_info, "mp4")
    assert_has_video_stream(output_info)
    assert_has_audio_stream(output_info)
    assert_duration_close(output_info.duration, source_info.duration)


@pytest.mark.core
@pytest.mark.convert
def test_mp4_to_mov_end_to_end(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mp4, "mp4_to_mov", "mp4_to_mov.mp4")
    output = output_path(project_paths, "mp4_to_mov", "mp4_to_mov.mov")

    run_workflow(macos_driver, automation_config, source, lambda page: page.open_convert_tab(), "mov", output)

    source_info = probe_media(source)
    output_info = probe_media(output)
    assert_is_format(output_info, "mov")
    assert_has_video_stream(output_info)
    assert_has_audio_stream(output_info)
    assert_duration_close(output_info.duration, source_info.duration)


@pytest.mark.core
@pytest.mark.convert
def test_mp4_to_mkv_end_to_end(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mp4, "mp4_to_mkv", "mp4_to_mkv.mp4")
    output = output_path(project_paths, "mp4_to_mkv", "mp4_to_mkv.mkv")

    run_workflow(macos_driver, automation_config, source, lambda page: page.open_convert_tab(), "mkv", output)

    source_info = probe_media(source)
    output_info = probe_media(output)
    assert_is_format(output_info, "mkv")
    assert_has_video_stream(output_info)
    assert_has_audio_stream(output_info)
    assert_duration_close(output_info.duration, source_info.duration)


@pytest.mark.core
@pytest.mark.convert
def test_mp4_to_wmv_end_to_end(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mp4, "mp4_to_wmv", "mp4_to_wmv.mp4")
    output = output_path(project_paths, "mp4_to_wmv", "mp4_to_wmv.wmv")

    run_workflow(macos_driver, automation_config, source, lambda page: page.open_convert_tab(), "wmv", output)

    source_info = probe_media(source)
    output_info = probe_media(output)
    assert_is_format(output_info, "wmv")
    assert_has_video_stream(output_info)
    assert_has_audio_stream(output_info)
    assert_duration_close(output_info.duration, source_info.duration)


@pytest.mark.core
@pytest.mark.convert
def test_mov_to_mp4_end_to_end(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mov, "mov_to_mp4", "mov_to_mp4.mov")
    output = output_path(project_paths, "mov_to_mp4", "mov_to_mp4.mp4")

    run_workflow(macos_driver, automation_config, source, lambda page: page.open_convert_tab(), "mp4", output)

    source_info = probe_media(source)
    output_info = probe_media(output)
    assert_is_format(output_info, "mp4")
    assert_has_video_stream(output_info)
    assert_has_audio_stream(output_info)
    assert_duration_close(output_info.duration, source_info.duration)
