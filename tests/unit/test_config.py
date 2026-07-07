import json

from desktop_auto.config import AutomationConfig, load_config


def test_load_config_reads_app_and_selector_settings(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps(
            {
                "app": {
                    "bundle_id": "com.example.VideoApp",
                    "app_path": "/Applications/VideoApp.app",
                    "launch_timeout_seconds": 20,
                },
                "test_media": {
                    "mp4": "test_data/sample.mp4",
                    "mov": "test_data/sample.mov",
                    "duration_seconds": 3,
                },
                "selectors": {
                    "main_window": "mainWindow",
                    "import_button": "btnImport",
                },
                "task_timeout_seconds": 45,
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config == AutomationConfig(
        bundle_id="com.example.VideoApp",
        app_path="/Applications/VideoApp.app",
        launch_timeout_seconds=20,
        task_timeout_seconds=45,
        test_media={
            "mp4": "test_data/sample.mp4",
            "mov": "test_data/sample.mov",
            "duration_seconds": "3",
        },
        selectors={
            "main_window": "mainWindow",
            "import_button": "btnImport",
        },
    )


def test_config_requires_bundle_id_or_app_path():
    config = AutomationConfig(bundle_id="", app_path="", selectors={})

    assert not config.can_launch_app


def test_config_can_launch_when_app_path_is_present():
    config = AutomationConfig(bundle_id="", app_path="/Applications/VideoApp.app", selectors={})

    assert config.can_launch_app
