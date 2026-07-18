#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_HOSTNAME="${EXPECTED_HOSTNAME:-fg-ubuntu}"
APP_DIR="${APP_DIR:-/srv/apps/registro_produccion}"
REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
ENV_DIR="${ENV_DIR:-/srv/env/registro_produccion}"
BACKUP_DIR="${BACKUP_DIR:-${HOME}/.deploy-backups/registro_produccion}"
LOCK_FILE="${LOCK_FILE:-${TMPDIR:-/tmp}/registro_produccion-deploy-main.lock}"
SERVICES=(indufor produccion_fg)
HEALTH_INDUFOR="${HEALTH_INDUFOR:-http://127.0.0.1:18004/health}"
HEALTH_PRODUCCION_FG="${HEALTH_PRODUCCION_FG:-http://127.0.0.1:18005/health}"

usage() {
  printf '%s\n' \
    "Usage: $0 --check" \
    "       $0 --deploy [--yes]"
}

mode=""
assume_yes=false
for argument in "$@"; do
  case "$argument" in
    --check|--deploy) mode="$argument" ;;
    --yes) assume_yes=true ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'ERROR: unknown argument: %s\n' "$argument" >&2; exit 2 ;;
  esac
done
[[ -n "$mode" ]] || { usage >&2; exit 2; }

log() {
  printf '==> %s\n' "$*"
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "missing command: $1"
}

rollback() {
  printf 'ERROR: rollback requested before implementation\n' >&2
  return 1
}

override_file=""

cleanup() {
  if [[ -n "$override_file" && -f "$override_file" ]]; then
    rm -f "$override_file"
  fi
}
trap cleanup EXIT

preflight() {
  [[ "$(hostname)" == "$EXPECTED_HOSTNAME" ]] ||
    fail "hostname must be $EXPECTED_HOSTNAME"

  for command_name in git docker curl flock; do
    require_command "$command_name"
  done

  [[ -d "$APP_DIR" ]] || fail "application checkout not found: $APP_DIR"
  cd "$APP_DIR"
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
    fail "application checkout not found: $APP_DIR"
  [[ -z "$(git status --porcelain)" ]] || fail "checkout is not clean"
  [[ -f "$ENV_DIR/indufor.env" ]] || fail "missing indufor env file"
  [[ -f "$ENV_DIR/produccion_fg.env" ]] || fail "missing produccion_fg env file"

  git fetch --prune "$REMOTE"
  target_commit="$(git rev-parse "$REMOTE/$BRANCH")"
  current_commit="$(git rev-parse HEAD)"
  git merge-base --is-ancestor "$current_commit" "$target_commit" ||
    fail "current commit is not a fast-forward of $REMOTE/$BRANCH"

  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    local_main="$(git rev-parse "$BRANCH")"
    git merge-base --is-ancestor "$local_main" "$target_commit" ||
      fail "local $BRANCH is not a fast-forward of $REMOTE/$BRANCH"
  fi

  docker compose config >/dev/null
  available_services="$(docker compose config --services)"
  for service in "${SERVICES[@]}"; do
    grep -Fxq "$service" <<<"$available_services" ||
      fail "missing compose service: $service"
  done
}

exec 9>"$LOCK_FILE"
flock -n 9 || fail "another deploy is running"
preflight

if [[ "$mode" == "--check" ]]; then
  log "Preflight successful"
  printf 'current_commit=%s\n' "$current_commit"
  printf 'target_commit=%s\n' "$target_commit"
  exit 0
fi

confirm_deploy() {
  if [[ "$assume_yes" == true ]]; then
    return
  fi
  [[ -t 0 ]] || fail "--deploy requires an interactive terminal or --yes"
  read -r -p "Type DEPLOY to continue: " answer
  [[ "$answer" == "DEPLOY" ]] || fail "deployment cancelled"
}

write_override() {
  override_file="$(mktemp)"
  cat >"$override_file" <<YAML
services:
  indufor:
    image: registro_produccion:${target_commit}
  produccion_fg:
    image: registro_produccion:${target_commit}
YAML
}

compose_target() {
  docker compose -f docker-compose.yml -f "$override_file" "$@"
}

wait_healthy() {
  local container="$1"
  local health_url="$2"
  local status

  for _ in {1..30}; do
    status="$(docker inspect -f '{{.State.Health.Status}}' "$container" 2>/dev/null || true)"
    if [[ "$status" == "healthy" ]]; then
      curl -fsS "$health_url" >/dev/null
      return
    fi
    sleep 2
  done
  fail "$container did not become healthy"
}

confirm_deploy

log "Updating local $BRANCH from $REMOTE/$BRANCH"
git switch "$BRANCH"
git merge --ff-only "$REMOTE/$BRANCH"
target_commit="$(git rev-parse HEAD)"
target_image="registro_produccion:${target_commit}"

log "Building immutable image $target_image"
docker build --tag "$target_image" .
docker run --rm "$target_image" python -m compileall -q /app
docker run --rm "$target_image" python -c "import app.main"

write_override

log "Updating indufor"
compose_target up -d --no-build --force-recreate indufor
wait_healthy registro_produccion_indufor "$HEALTH_INDUFOR"

log "Updating produccion_fg"
compose_target up -d --no-build --force-recreate produccion_fg
wait_healthy registro_produccion_produccion_fg "$HEALTH_PRODUCCION_FG"

docker tag "$target_image" registro_produccion:latest

log "Deploy successful"
printf 'target_commit=%s\n' "$target_commit"
printf 'target_image=%s\n' "$target_image"
