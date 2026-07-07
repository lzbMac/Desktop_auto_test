from pathlib import Path

import pytest

from desktop_auto.utils.file_assert import assert_file_exists, assert_file_size_at_most_ratio


def test_assert_file_exists_accepts_non_empty_file(tmp_path):
    output_file = tmp_path / "output.mp4"
    output_file.write_bytes(b"video")

    assert_file_exists(output_file)


def test_assert_file_exists_rejects_missing_file(tmp_path):
    with pytest.raises(AssertionError, match="does not exist"):
        assert_file_exists(tmp_path / "missing.mp4")


def test_assert_file_exists_rejects_empty_file(tmp_path):
    output_file = tmp_path / "empty.mp4"
    output_file.touch()

    with pytest.raises(AssertionError, match="is empty"):
        assert_file_exists(output_file)


def test_assert_file_size_at_most_ratio_accepts_small_growth(tmp_path):
    source = tmp_path / "source.mp4"
    output = tmp_path / "compressed.mp4"
    source.write_bytes(b"123")
    output.write_bytes(b"12345")

    assert_file_size_at_most_ratio(output, source, max_ratio=2.0)


def test_assert_file_size_at_most_ratio_rejects_excessive_growth(tmp_path):
    source = tmp_path / "source.mp4"
    output = tmp_path / "compressed.mp4"
    source.write_bytes(b"123")
    output.write_bytes(b"1234567")

    with pytest.raises(AssertionError, match="too large"):
        assert_file_size_at_most_ratio(output, source, max_ratio=2.0)
