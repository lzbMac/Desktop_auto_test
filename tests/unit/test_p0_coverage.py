import ast
from pathlib import Path


def test_e2e_suite_defines_ten_core_p0_cases():
    core_tests = []
    for test_file in Path("tests/e2e").glob("test_*.py"):
        tree = ast.parse(test_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                if _has_pytest_mark(node, "core"):
                    core_tests.append(f"{test_file}::{node.name}")

    assert sorted(core_tests) == [
        "tests/e2e/test_audio_extract.py::test_audio_extract_end_to_end",
        "tests/e2e/test_import.py::test_import_mp4_video",
        "tests/e2e/test_smoke.py::test_app_launches",
        "tests/e2e/test_video_compress.py::test_video_compress_end_to_end",
        "tests/e2e/test_video_convert.py::test_mkv_to_mp4_end_to_end",
        "tests/e2e/test_video_convert.py::test_mov_to_mp4_end_to_end",
        "tests/e2e/test_video_convert.py::test_mp4_to_mkv_end_to_end",
        "tests/e2e/test_video_convert.py::test_mp4_to_mov_end_to_end",
        "tests/e2e/test_video_convert.py::test_mp4_to_wmv_end_to_end",
        "tests/e2e/test_video_to_gif.py::test_video_to_gif_end_to_end",
    ]


def _has_pytest_mark(node: ast.FunctionDef, mark_name: str) -> bool:
    for decorator in node.decorator_list:
        if (
            isinstance(decorator, ast.Attribute)
            and decorator.attr == mark_name
            and isinstance(decorator.value, ast.Attribute)
            and decorator.value.attr == "mark"
        ):
            return True
    return False
