from desktop_auto.utils.artifacts import capture_failure_artifacts
from desktop_auto.utils.paths import ProjectPaths


class FakeDriver:
    page_source = "<App><Button identifier='btnImport' /></App>"

    def save_screenshot(self, path):
        with open(path, "wb") as screenshot:
            screenshot.write(b"png")
        self.screenshot_path = path
        return True


def test_capture_failure_artifacts_saves_screenshot_and_page_source(tmp_path):
    paths = ProjectPaths(tmp_path)
    paths.ensure_runtime_dirs()
    driver = FakeDriver()

    artifacts = capture_failure_artifacts(driver, paths, "tests/e2e/test_import.py::test_import_mp4_video")

    assert artifacts.screenshot_path.is_file()
    assert artifacts.page_source_path.is_file()
    assert artifacts.page_source_path.read_text(encoding="utf-8") == driver.page_source
    assert "test_import_mp4_video" in artifacts.screenshot_path.name
    assert driver.screenshot_path == str(artifacts.screenshot_path)
