#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_HOSTNAME="${EXPECTED_HOSTNAME:-fg-ubuntu}"
APP_DIR="${APP_DIR:-/srv/apps/registro_produccion}"
REMOTE="origin"
BRANCH="main"
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
  local service="$1"
  local image="$2"
  local container="$3"
  local health_url="$4"

  log "rollback_service $service $image"
  write_service_override "$service" "$image"
  if ! compose_target up -d --no-build --force-recreate "$service"; then
    printf 'ERROR: rollback compose failed for %s\n' "$service" >&2
    return 1
  fi
  if ! wait_healthy "$container" "$health_url"; then
    printf 'ERROR: rollback healthcheck failed for %s\n' "$service" >&2
    return 1
  fi
  return 0
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

write_service_override() {
  local service="$1"
  local image="$2"

  if [[ -z "$override_file" ]]; then
    override_file="$(mktemp)"
  fi
  cat >"$override_file" <<YAML
services:
  ${service}:
    image: ${image}
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
      return 0
    fi
    sleep 2
  done
  printf 'ERROR: %s did not become healthy\n' "$container" >&2
  return 1
}

confirm_deploy

previous_branch="$(git branch --show-current)"
previous_commit="$(git rev-parse HEAD)"
previous_indufor_image="$(
  docker inspect -f '{{.Image}}' registro_produccion_indufor
)"
previous_produccion_image="$(
  docker inspect -f '{{.Image}}' registro_produccion_produccion_fg
)"
indufor_updated=false
produccion_updated=false
manifest=""
recovery_started=false

recover_and_exit() {
  local exit_code="$1"
  local reason="$2"
  local recovery_failed=false

  if [[ "$recovery_started" == true ]]; then
    exit "$exit_code"
  fi
  recovery_started=true
  trap - ERR INT TERM
  set +e

  printf 'ERROR: %s; starting rollback\n' "$reason" >&2
  if [[ "$produccion_updated" == true ]]; then
    if ! rollback \
      produccion_fg \
      "$previous_produccion_image" \
      registro_produccion_produccion_fg \
      "$HEALTH_PRODUCCION_FG"; then
      printf 'ERROR: failed to restore produccion_fg\n' >&2
      recovery_failed=true
    fi
  fi
  if [[ "$indufor_updated" == true ]]; then
    if ! rollback \
      indufor \
      "$previous_indufor_image" \
      registro_produccion_indufor \
      "$HEALTH_INDUFOR"; then
      printf 'ERROR: failed to restore indufor\n' >&2
      recovery_failed=true
    fi
  fi

  if ! git switch "$previous_branch"; then
    printf 'ERROR: failed to restore Git branch %s\n' "$previous_branch" >&2
    recovery_failed=true
  fi
  if ! git reset --keep "$previous_commit"; then
    printf 'ERROR: failed to restore Git commit %s\n' "$previous_commit" >&2
    recovery_failed=true
  fi
  if [[ -n "$manifest" && -f "$manifest" ]]; then
    if [[ "$recovery_failed" == true ]]; then
      printf 'status=rollback_failed\n' >>"$manifest"
    else
      printf 'status=rolled_back\n' >>"$manifest"
    fi
  fi
  if [[ "$recovery_failed" == true ]]; then
    printf 'ERROR: rollback failed; inspect containers and manifest: %s\n' \
      "$manifest" >&2
  fi
  exit "$exit_code"
}

handle_error() {
  local exit_code=$?
  recover_and_exit "$exit_code" "deploy failed"
}

handle_signal() {
  recover_and_exit 130 "deployment interrupted"
}

trap handle_error ERR
trap handle_signal INT TERM

log "Updating local $BRANCH from $REMOTE/$BRANCH"
git switch "$BRANCH"
git merge --ff-only "$REMOTE/$BRANCH"
target_commit="$(git rev-parse HEAD)"
target_image="registro_produccion:${target_commit}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"
manifest="$BACKUP_DIR/deploy_${timestamp}_${target_commit}.env"
printf '%s\n' \
  "previous_branch=$previous_branch" \
  "previous_commit=$previous_commit" \
  "previous_indufor_image=$previous_indufor_image" \
  "previous_produccion_fg_image=$previous_produccion_image" \
  "target_commit=$target_commit" \
  "target_image=$target_image" >"$manifest"
chmod 600 "$manifest"

log "Building immutable image $target_image"
docker build --tag "$target_image" .
docker run --rm "$target_image" python -m compileall -q /app
docker run --rm "$target_image" python -c "import app.main"

write_override
resolved_target_count="$(
  compose_target config --images |
    grep -Fxc "$target_image"
)"
[[ "$resolved_target_count" -eq 2 ]] ||
  fail "compose override did not resolve both services to $target_image"

log "Updating indufor"
indufor_updated=true
compose_target up -d --no-build --force-recreate indufor
wait_healthy registro_produccion_indufor "$HEALTH_INDUFOR"

log "Updating produccion_fg"
produccion_updated=true
compose_target up -d --no-build --force-recreate produccion_fg
wait_healthy registro_produccion_produccion_fg "$HEALTH_PRODUCCION_FG"

docker tag "$target_image" registro_produccion:latest
printf 'status=success\n' >>"$manifest"
trap - ERR INT TERM

indufor_image="$(
  docker inspect -f '{{.Image}}' registro_produccion_indufor
)"
produccion_fg_image="$(
  docker inspect -f '{{.Image}}' registro_produccion_produccion_fg
)"
indufor_health="$(
  docker inspect -f '{{.State.Health.Status}}' registro_produccion_indufor
)"
produccion_fg_health="$(
  docker inspect -f '{{.State.Health.Status}}' registro_produccion_produccion_fg
)"

log "Deploy successful"
printf 'target_commit=%s\n' "$target_commit"
printf 'target_image=%s\n' "$target_image"
printf 'indufor_image=%s\n' "$indufor_image"
printf 'indufor_health=%s\n' "$indufor_health"
printf 'indufor_health_url=%s\n' "$HEALTH_INDUFOR"
printf 'produccion_fg_image=%s\n' "$produccion_fg_image"
printf 'produccion_fg_health=%s\n' "$produccion_fg_health"
printf 'produccion_fg_health_url=%s\n' "$HEALTH_PRODUCCION_FG"
