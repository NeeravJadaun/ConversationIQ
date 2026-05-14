#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose "$@"
  else
    echo "Docker Compose is required. Install Docker Compose v2 or docker-compose." >&2
    exit 127
  fi
}

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
    echo "Python is required to run scripts/e2e_test.py. Set PYTHON_BIN or install python3." >&2
    exit 127
  fi
}

cleanup() {
  compose down -v --remove-orphans
}
trap cleanup EXIT

compose up --build -d

API_URL="${API_URL:-http://localhost:8000}" "$(python_bin)" scripts/e2e_test.py

echo "Docker smoke test passed"
