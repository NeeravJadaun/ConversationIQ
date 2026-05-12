#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

cleanup() {
  docker compose down -v
}
trap cleanup EXIT

docker compose up --build -d

API_URL="${API_URL:-http://localhost:8000}" python scripts/e2e_test.py

echo "Docker smoke test passed"
