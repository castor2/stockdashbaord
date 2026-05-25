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
  echo "[mode] 기존 InfluxDB/Grafana 사용 → collector만 실행"
  export COMPOSE_PROFILES=""
  docker compose up -d --build collector
else
  echo "[mode] 내장 InfluxDB/Grafana 사용 → 전체 스택 실행"
  export COMPOSE_PROFILES="${COMPOSE_PROFILES:-embedded}"
  docker compose up -d --build
fi

docker compose ps
