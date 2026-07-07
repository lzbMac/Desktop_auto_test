import pytest

from desktop_auto.pages.main_window import MainWindow
from tests.e2e.workflow_helpers import prepare_input, skip_if_login_required


@pytest.mark.core
def test_import_mp4_video(macos_driver, automation_config, project_paths, default_test_media):
    source = prepare_input(project_paths, default_test_media.mp4, "import_mp4", "import_mp4.mp4")
    main_window = MainWindow(macos_driver, automation_config)

    def import_video() -> None:
        main_window.wait_until_ready(automation_config.launch_timeout_seconds)
        main_window.open_convert_tab()
        main_window.import_file(source, automation_config.default_timeout_seconds)

    skip_if_login_required(import_video)
