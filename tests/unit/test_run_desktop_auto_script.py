import os
import subprocess
import textwrap
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def write_executable(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    path.chmod(0o755)


def test_smoke_uses_project_appium_home_by_default(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    venv_dir = tmp_path / "venv"
    (venv_dir / "bin").mkdir(parents=True)

    write_executable(
        venv_dir / "bin" / "python",
        """\
        #!/usr/bin/env bash
        if [[ "$1" == "-c" ]]; then
          exit 0
        fi
        exit 0
        """,
    )
    write_executable(
        fake_bin / "ioreg",
        """\
        #!/usr/bin/env bash
        exit 0
        """,
    )
    write_executable(
        fake_bin / "curl",
        """\
        #!/usr/bin/env bash
        if [[ -f "${FAKE_READY_FILE}" ]]; then
          exit 0
        fi
        exit 1
        """,
    )
    write_executable(
        fake_bin / "appium",
        """\
        #!/usr/bin/env bash
        printf '%s' "${APPIUM_HOME:-}" > "${FAKE_APPIUM_HOME_CAPTURE}"
        touch "${FAKE_READY_FILE}"
        while true; do
          sleep 1
        done
        """,
    )

    env = {
        **os.environ,
        "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
        "VENV_DIR": str(venv_dir),
        "FAKE_READY_FILE": str(state_dir / "ready"),
        "FAKE_APPIUM_HOME_CAPTURE": str(state_dir / "appium_home"),
    }
    env.pop("APPIUM_HOME", None)

    result = subprocess.run(
        [str(ROOT_DIR / "run_desktop_auto.sh"), "smoke"],
        cwd=ROOT_DIR,
        env=env,
        text=True,
        capture_output=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (state_dir / "appium_home").read_text(encoding="utf-8") == str(
        ROOT_DIR / ".appium-home"
    )
