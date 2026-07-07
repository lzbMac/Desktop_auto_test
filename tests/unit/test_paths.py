from pathlib import Path

from desktop_auto.utils.paths import ProjectPaths


def test_project_paths_create_runtime_directories(tmp_path):
    paths = ProjectPaths(root=tmp_path)

    paths.ensure_runtime_dirs()

    assert paths.outputs_dir.is_dir()
    assert paths.reports_dir.is_dir()
    assert paths.screenshots_dir.is_dir()
    assert paths.logs_dir.is_dir()


def test_project_paths_clean_outputs_removes_files_but_keeps_directory(tmp_path):
    paths = ProjectPaths(root=tmp_path)
    paths.ensure_runtime_dirs()
    output_file = paths.outputs_dir / "old-output.mov"
    output_file.write_text("stale", encoding="utf-8")

    paths.clean_outputs()

    assert paths.outputs_dir.is_dir()
    assert not output_file.exists()
    assert list(paths.outputs_dir.iterdir()) == []


def test_project_paths_resolve_test_data_uses_test_data_dir(tmp_path):
    paths = ProjectPaths(root=tmp_path)

    assert paths.test_data("sample.mp4") == Path(tmp_path) / "test_data" / "sample.mp4"
