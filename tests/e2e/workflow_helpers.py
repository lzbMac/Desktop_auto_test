from pathlib import Path
import os
import shutil

import pytest

from desktop_auto.pages.main_window import LoginRequiredError, MainWindow
from desktop_auto.pages.media_panels import MediaPanel
from desktop_auto.utils.wait import wait_until


def prepare_input(project_paths, source: Path, case_name: str, filename: str) -> Path:
    output_dir = project_paths.outputs_dir / case_name
    input_root = Path(os.environ.get("DESKTOP_AUTO_INPUT_ROOT", "/tmp/desktop-ui-auto-inputs"))
    input_dir = input_root / case_name
    for path in (output_dir, input_dir):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
    target = input_dir / filename
    shutil.copy2(source, target)
    return target


def output_path(project_paths, case_name: str, filename: str) -> Path:
    return project_paths.outputs_dir / case_name / filename


def skip_if_login_required(action) -> None:
    try:
        action()
    except LoginRequiredError as error:
        pytest.skip(str(error))


def run_workflow(
    driver,
    config,
    source: Path,
    open_tab,
    output_format: str | None,
    expected_output: Path,
) -> Path:
    main_window = MainWindow(driver, config)
    panel = MediaPanel(driver, config)

    def submit_task() -> None:
        main_window.wait_until_ready(config.launch_timeout_seconds)
        open_tab(main_window)
        main_window.import_file(source, config.default_timeout_seconds)
        if output_format:
            panel.choose_output_format(output_format)
        panel.set_output_directory(expected_output.parent, config.default_timeout_seconds)
        main_window.start_task()

    skip_if_login_required(submit_task)
    return wait_until(
        lambda: expected_output if expected_output.exists() and expected_output.stat().st_size > 0 else None,
        timeout_seconds=config.task_timeout_seconds,
        message=f"Output file was not created: {expected_output}",
    )
