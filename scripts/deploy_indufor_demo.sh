#!/usr/bin/env bash
set -euo pipefail

BRANCH="codex/docker-multi-instance-registro-produccion"
EXPECTED_HOSTNAME="fg-ubuntu"
APP_DIR="/srv/apps/registro_produccion"
ENV_FILE="/srv/env/registro_produccion/indufor_demo.env"
SERVICE="indufor_demo"
HEALTH_URL="http://127.0.0.1:18104/health"
OPENAPI_URL="http://127.0.0.1:18104/openapi.json"
COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.demo.yml)
RUN_SEED=false

usage() {
  cat <<'USAGE'
Usage: scripts/deploy_indufor_demo.sh [--seed]

Deploys only the indufor_demo staging container on fasa_195.

Options:
  --seed   Run python -m app.seed.demo_data after the container is healthy.
  -h, --help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --seed)
      RUN_SEED=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

log() {
  printf '==> %s\n' "$*"
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

require_env_value() {
  local key="$1"
  local expected="$2"
  if ! grep -Eq "^${key}=${expected}$" "$ENV_FILE"; then
    fail "$ENV_FILE must contain ${key}=${expected}"
  fi
}

require_env_key() {
  local key="$1"
  if ! grep -Eq "^${key}=" "$ENV_FILE"; then
    fail "$ENV_FILE must define ${key}"
  fi
}

validate_database_url() {
  python3 - "$ENV_FILE" <<'PY'
import sys
from pathlib import Path
from urllib.parse import urlparse

env_path = Path(sys.argv[1])
values = {}
for line in env_path.read_text(errors="replace").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    values[key.strip()] = value.strip().strip('"').strip("'")

raw_url = values.get("DATABASE_URL", "")
if not raw_url:
    raise SystemExit("DATABASE_URL is missing")

url = urlparse(raw_url)
if url.scheme not in {"mysql", "mysql+pymysql"}:
    raise SystemExit(f"DATABASE_URL must be mysql/mysql+pymysql, got {url.scheme!r}")
if url.path.lstrip("/") != "indufor_demo":
    raise SystemExit("DATABASE_URL must point to database indufor_demo")

print(f"database host: {url.hostname or 'unset'}")
print(f"database name: {url.path.lstrip('/')}")
print(f"database user: {url.username or 'unset'}")
PY
}

current_hostname="$(hostname)"
if [[ "$current_hostname" != "$EXPECTED_HOSTNAME" ]]; then
  log "WARNING: hostname is '$current_hostname', expected '$EXPECTED_HOSTNAME'. Continue only if this is fasa_195."
fi

require_command git
require_command docker
require_command curl
require_command python3

[[ -d "$APP_DIR" ]] || fail "Application directory not found: $APP_DIR"
cd "$APP_DIR"

[[ -f docker-compose.yml ]] || fail "Missing docker-compose.yml"
[[ -f docker-compose.demo.yml ]] || fail "Missing docker-compose.demo.yml"
[[ -f "$ENV_FILE" ]] || fail "Missing env file: $ENV_FILE"

log "Validating demo env file without printing secrets"
require_env_key "DATABASE_URL"
require_env_value "APP_ENV" "staging"
require_env_value "APP_INSTANCE" "indufor_demo"
require_env_value "EXPECTED_DB_NAME" "indufor_demo"
require_env_value "DEMO_SEED_RECORDS" "[0-9]+"

if [[ "$RUN_SEED" == "true" ]]; then
  require_env_value "ALLOW_DEMO_SEED" "true"
else
  require_env_value "ALLOW_DEMO_SEED" "false"
fi
validate_database_url

log "Updating repository branch $BRANCH"
git fetch origin --prune
git switch codex/docker-multi-instance-registro-produccion
git pull --ff-only origin codex/docker-multi-instance-registro-produccion

[[ -f docker-compose.yml ]] || fail "Missing docker-compose.yml after pull"
[[ -f docker-compose.demo.yml ]] || fail "Missing docker-compose.demo.yml after pull"

log "Validating Docker Compose configuration"
"${COMPOSE[@]}" config >/dev/null

log "Building and starting only $SERVICE"
"${COMPOSE[@]}" up -d --build "$SERVICE"

log "Validating health endpoint"
curl -fsS "$HEALTH_URL" >/dev/null

log "Validating OpenAPI endpoint"
curl -fsS "$OPENAPI_URL" >/dev/null

if [[ "$RUN_SEED" == "true" ]]; then
  log "Running demo seed for $SERVICE"
  "${COMPOSE[@]}" exec -T indufor_demo python -m app.seed.demo_data
  log "Re-validating health endpoint after seed"
  curl -fsS "$HEALTH_URL" >/dev/null
else
  log "Seed skipped. Pass --seed and set ALLOW_DEMO_SEED=true in $ENV_FILE to load fake data."
fi

log "Demo deploy summary"
printf 'service: %s\n' "$SERVICE"
printf 'container: registro_produccion_indufor_demo\n'
printf 'health: %s\n' "$HEALTH_URL"
printf 'openapi: %s\n' "$OPENAPI_URL"
printf 'seed_run: %s\n' "$RUN_SEED"
