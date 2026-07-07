from pathlib import Path


def assert_file_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"File does not exist: {path}")
    if not path.is_file():
        raise AssertionError(f"Path is not a file: {path}")
    if path.stat().st_size == 0:
        raise AssertionError(f"File is empty: {path}")


def assert_file_size_at_most_ratio(output: Path, source: Path, max_ratio: float) -> None:
    assert_file_exists(output)
    assert_file_exists(source)

    output_size = output.stat().st_size
    source_size = source.stat().st_size
    if output_size > source_size * max_ratio:
        raise AssertionError(
            f"Output file is too large relative to source: "
            f"output={output_size}, source={source_size}, max_ratio={max_ratio}"
        )
