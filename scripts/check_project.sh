#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python_bin() {
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    printf '%s\n' "$PYTHON_BIN"
  elif [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    printf '%s\n' "$ROOT_DIR/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  elif command -v python >/dev/null 2>&1; then
    command -v python
  else
    echo "Python is required. Set PYTHON_BIN or install python3." >&2
    exit 127
  fi
}

WITH_DOCKER=0
if [[ "${1:-}" == "--with-docker" ]]; then
  WITH_DOCKER=1
elif [[ $# -gt 0 ]]; then
  echo "Usage: scripts/check_project.sh [--with-docker]" >&2
  exit 2
fi

PYTHON="$(python_bin)"

echo "== Backend tests =="
(cd backend && "$PYTHON" -m pytest tests/ -v)

echo "== Frontend tests =="
(cd frontend && npm test -- --runInBand)

echo "== Frontend build =="
(cd frontend && npm run build)

if [[ "$WITH_DOCKER" == "1" ]]; then
  echo "== Docker smoke test =="
  bash scripts/docker_smoke_test.sh
fi

echo "All requested checks passed"
