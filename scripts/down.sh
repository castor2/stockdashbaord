#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

USE_EXISTING="${USE_EXISTING_SERVICES:-false}"

if [[ "$USE_EXISTING" == "true" ]]; then
  echo "[mode] collector만 중지"
  docker compose stop collector
else
  echo "[mode] 전체 스택 중지"
  export COMPOSE_PROFILES="${COMPOSE_PROFILES:-embedded}"
  docker compose --profile embedded down
fi
