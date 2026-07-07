#!/usr/bin/env bash
set -euo pipefail

python3 -m pytest tests/unit -q
