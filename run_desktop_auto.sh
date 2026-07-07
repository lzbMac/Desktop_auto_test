#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPIUM_HOME="${APPIUM_HOME:-${ROOT_DIR}/.appium-home}"
APPIUM_HOST="${APPIUM_HOST:-127.0.0.1}"
APPIUM_PORT="${APPIUM_PORT:-4723}"
APPIUM_URL="http://${APPIUM_HOST}:${APPIUM_PORT}/status"
APPIUM_PID=""
MODE="${1:-core}"
VENV_DIR="${VENV_DIR:-.venv}"
PYTHON_BIN="${PYTHON_BIN:-}"

export APPIUM_HOME

cd "$ROOT_DIR"
mkdir -p reports

usage() {
  cat <<'EOF'
Usage:
  ./run_desktop_auto.sh unit
  ./run_desktop_auto.sh smoke
  ./run_desktop_auto.sh core

Environment:
  APPIUM_HOME defaults to .appium-home under the project root
  APPIUM_HOST defaults to 127.0.0.1
  APPIUM_PORT defaults to 4723
  PYTHON_BIN overrides the Python executable
  VENV_DIR defaults to .venv
EOF
}

ensure_python() {
  if [[ -n "$PYTHON_BIN" ]]; then
    return
  fi

  if [[ -x "${VENV_DIR}/bin/python" ]]; then
    PYTHON_BIN="${VENV_DIR}/bin/python"
    return
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 command not found." >&2
    return 1
  fi

  echo "Creating Python virtual environment at ${VENV_DIR}"
  python3 -m venv "$VENV_DIR"
  PYTHON_BIN="${VENV_DIR}/bin/python"
}

ensure_python_deps() {
  ensure_python
  if "$PYTHON_BIN" -c "import pytest, pytest_html, appium" >/dev/null 2>&1; then
    return
  fi

  echo "Installing Python test dependencies into ${VENV_DIR}"
  "$PYTHON_BIN" -m pip install -r requirements.txt
}

appium_is_ready() {
  curl -fsS "$APPIUM_URL" >/dev/null 2>&1
}

console_is_locked() {
  local session_state
  session_state="$(ioreg -n Root -d1 2>/dev/null || true)"
  grep -Eq '"?(IOConsoleLocked|CGSessionScreenIsLocked)"?[[:space:]]*=[[:space:]]*Yes' <<<"$session_state"
}

wait_for_appium() {
  local deadline=$((SECONDS + 30))
  until appium_is_ready; do
    if (( SECONDS >= deadline )); then
      echo "Appium did not become ready at ${APPIUM_URL}" >&2
      echo "See reports/appium.log for details." >&2
      return 1
    fi
    sleep 1
  done
}

start_appium_if_needed() {
  if appium_is_ready; then
    echo "Using existing Appium server at ${APPIUM_URL}"
    return
  fi

  if ! command -v appium >/dev/null 2>&1; then
    echo "appium command not found. Install it with: npm install -g appium" >&2
    return 1
  fi

  echo "Starting Appium at ${APPIUM_HOST}:${APPIUM_PORT}"
  appium --address "$APPIUM_HOST" --port "$APPIUM_PORT" --base-path / >reports/appium.log 2>&1 &
  APPIUM_PID="$!"
  wait_for_appium
}

run_e2e_pytest() {
  local marker="$1"
  local report="$2"
  if console_is_locked; then
    echo "macOS desktop is locked; writing skipped ${report} without starting Appium."
    RUN_DESKTOP_E2E=1 "$PYTHON_BIN" -m pytest tests/e2e -m "$marker" --html="reports/${report}" -q
    return
  fi
  start_appium_if_needed
  RUN_DESKTOP_E2E=1 "$PYTHON_BIN" -m pytest tests/e2e -m "$marker" --html="reports/${report}" -q
}

cleanup() {
  if [[ -n "$APPIUM_PID" ]]; then
    echo "Stopping Appium pid ${APPIUM_PID}"
    kill "$APPIUM_PID" >/dev/null 2>&1 || true
    wait "$APPIUM_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT

case "$MODE" in
  unit)
    ensure_python_deps
    "$PYTHON_BIN" -m pytest tests/unit -q
    ;;
  smoke)
    ensure_python_deps
    run_e2e_pytest smoke smoke.html
    ;;
  core)
    ensure_python_deps
    run_e2e_pytest core core.html
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "Unknown mode: ${MODE}" >&2
    usage >&2
    exit 2
    ;;
esac
