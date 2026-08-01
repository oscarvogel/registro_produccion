#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_HOSTNAME="fg-ubuntu"
REMOTE="origin"
BRANCH="main"
SERVICE="produccion_fg"
CONTAINER="registro_produccion_produccion_fg"
HEALTH_URL="http://127.0.0.1:18005/health"
SOURCE_DIR="${SOURCE_DIR:-/srv/apps/registro_produccion}"
APP_PARENT="${APP_PARENT:-/var/www/html/django/produccion_fg}"
BACKUP_DIR="${BACKUP_DIR:-${HOME}/deploy-backups/registro_produccion}"
LOCK_FILE="${LOCK_FILE:-${TMPDIR:-/tmp}/registro_produccion-produccion-fg.lock}"

usage() {
  printf '%s\n' \
    "Usage: $0 --check PACKAGE" \
    "       $0 --deploy PACKAGE" \
    "       $0 --deploy --yes PACKAGE"
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  return 1
}

log() {
  printf '==> %s\n' "$*"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "missing command: $1"
}

mode=""
assume_yes=false
package=""

for argument in "$@"; do
  case "$argument" in
    --check|--deploy)
      [[ -z "$mode" ]] || { usage >&2; exit 2; }
      mode="$argument"
      ;;
    --yes)
      assume_yes=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      printf 'ERROR: unknown argument: %s\n' "$argument" >&2
      usage >&2
      exit 2
      ;;
    *)
      [[ -z "$package" ]] || { usage >&2; exit 2; }
      package="$argument"
      ;;
  esac
done

[[ -n "$mode" && -n "$package" ]] || { usage >&2; exit 2; }
if [[ "$mode" == "--check" && "$assume_yes" == true ]]; then
  fail "--yes is only valid with --deploy"
fi

tmp_dir=""
manifest=""
previous_image_id=""
rollback_tag=""
previous_frontend=""
failed_frontend=""
previous_manifest=""
failed_manifest=""
frontend_previous_created=false
manifest_previous_created=false
deploy_started=false
recovery_started=false

cleanup() {
  if [[ -n "$tmp_dir" && -d "$tmp_dir" ]]; then
    rm -rf "$tmp_dir"
  fi
}
trap cleanup EXIT

wait_healthy() {
  local status
  for _ in {1..30}; do
    status="$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null || true)"
    if [[ "$status" == "healthy" ]] && curl -fsS "$HEALTH_URL" >/dev/null; then
      return 0
    fi
    sleep 2
  done
  printf 'ERROR: %s did not become healthy\n' "$CONTAINER" >&2
  return 1
}

recover_and_exit() {
  local original_exit="$1"
  local recovery_failed=false

  if [[ "$recovery_started" == true ]]; then
    exit "$original_exit"
  fi
  recovery_started=true
  trap - ERR INT TERM
  set +e

  printf 'ERROR: deploy failed; starting rollback\n' >&2

  if [[ "$manifest_previous_created" == true ]]; then
    if [[ -f "$APP_PARENT/RELEASE_MANIFEST.txt" ]] &&
       ! mv "$APP_PARENT/RELEASE_MANIFEST.txt" "$failed_manifest"; then
      printf 'ERROR: failed to preserve failed release manifest\n' >&2
      recovery_failed=true
    fi
    if ! mv "$previous_manifest" "$APP_PARENT/RELEASE_MANIFEST.txt"; then
      printf 'ERROR: failed to restore release manifest\n' >&2
      recovery_failed=true
    fi
  fi

  if [[ "$frontend_previous_created" == true ]]; then
    if [[ -d "$APP_PARENT/frontend" ]] &&
       ! mv "$APP_PARENT/frontend" "$failed_frontend"; then
      printf 'ERROR: failed to preserve failed frontend\n' >&2
      recovery_failed=true
    fi
    if ! mv "$previous_frontend" "$APP_PARENT/frontend"; then
      printf 'ERROR: failed to restore frontend\n' >&2
      recovery_failed=true
    fi
  fi

  if [[ "$deploy_started" == true ]]; then
    if ! docker tag "$previous_image_id" registro_produccion:latest ||
       ! docker compose -f docker-compose.yml up -d --no-build --no-deps --force-recreate "$SERVICE" ||
       ! wait_healthy; then
      printf 'ERROR: failed to restore produccion_fg image or health\n' >&2
      recovery_failed=true
    fi
  fi

  if [[ -n "$manifest" && -f "$manifest" ]]; then
    if [[ "$recovery_failed" == true ]]; then
      printf 'status=rollback_failed\n' >>"$manifest"
    else
      printf 'status=rolled_back\n' >>"$manifest"
    fi
  fi

  if [[ "$recovery_failed" == true ]]; then
    printf 'ERROR: rollback failed; inspect backup: %s\n' "${manifest:-not-created}" >&2
  fi
  exit "$original_exit"
}

handle_error() {
  local exit_code=$?
  recover_and_exit "$exit_code"
}

handle_signal() {
  recover_and_exit 130
}

preflight() {
  [[ "$(hostname)" == "$EXPECTED_HOSTNAME" ]] ||
    fail "hostname must be $EXPECTED_HOSTNAME"

  for command_name in git docker curl flock tar sha256sum awk grep mktemp; do
    require_command "$command_name"
  done

  [[ -d "$SOURCE_DIR" ]] || fail "application checkout not found: $SOURCE_DIR"
  cd "$SOURCE_DIR"
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 ||
    fail "application checkout not found: $SOURCE_DIR"
  [[ -z "$(git status --porcelain)" ]] || fail "checkout is not clean"
  [[ -f docker-compose.yml ]] || fail "missing docker-compose.yml"
  [[ -f "$package" ]] || fail "package not found: $package"
  [[ -d "$APP_PARENT/frontend" ]] || fail "published frontend not found"
  [[ -f "$APP_PARENT/frontend/index.html" ]] || fail "published frontend index not found"
  [[ -f "$APP_PARENT/RELEASE_MANIFEST.txt" ]] || fail "release manifest not found"

  package="$(cd "$(dirname "$package")" && pwd)/$(basename "$package")"
  package_sha="$(sha256sum "$package" | awk '{print $1}')"
  package_listing="$(tar -tzf "$package")"
  [[ -n "$package_listing" ]] || fail "package is empty"
  if grep -Eq '(^/|(^|/)\.\.(/|$))' <<<"$package_listing"; then
    fail "package contains unsafe paths"
  fi
  if grep -Eq '(^|/)\.env($|\.)' <<<"$package_listing"; then
    fail "package contains forbidden env files"
  fi

  tmp_dir="$(mktemp -d)"
  tar -xzf "$package" -C "$tmp_dir"
  [[ -f "$tmp_dir/RELEASE_MANIFEST.txt" ]] || fail "package manifest missing"
  [[ -d "$tmp_dir/backend/app" ]] || fail "package backend missing"
  [[ -f "$tmp_dir/backend/requirements.txt" ]] || fail "package requirements missing"
  [[ -f "$tmp_dir/frontend/dist/index.html" ]] || fail "package frontend missing"

  release_commit="$(awk -F= '$1 == "commit" {print $2}' "$tmp_dir/RELEASE_MANIFEST.txt" | tr -d '\r')"
  release_branch="$(awk -F= '$1 == "branch" {print $2}' "$tmp_dir/RELEASE_MANIFEST.txt" | tr -d '\r')"
  [[ -n "$release_commit" ]] || fail "package manifest has no commit"
  [[ "$release_branch" == "$BRANCH" ]] || fail "package was not built from main"

  deployed_commit="$(awk -F= '$1 == "commit" {print $2}' "$APP_PARENT/RELEASE_MANIFEST.txt" | tr -d '\r')"
  [[ -n "$deployed_commit" ]] || fail "deployed release manifest has no commit"

  git fetch --prune "$REMOTE"
  target_commit="$(git rev-parse "$REMOTE/$BRANCH")"
  source_commit="$(git rev-parse HEAD)"
  [[ "$release_commit" == "$target_commit" ]] ||
    fail "package commit does not match origin/main"
  [[ "$source_commit" == "$target_commit" ]] ||
    fail "source checkout does not match origin/main"
  git merge-base --is-ancestor "$deployed_commit" "$target_commit" ||
    fail "deployed commit is not an ancestor of origin/main"
  changed_migrations="$(git diff --name-only "$deployed_commit" "$target_commit" -- db_migrations)"
  [[ -z "$changed_migrations" ]] ||
    fail "database migrations require a separate procedure"

  docker compose -f docker-compose.yml config --services | grep -Fxq "$SERVICE" ||
    fail "compose service missing: $SERVICE"
  previous_image_id="$(docker inspect -f '{{.Image}}' "$CONTAINER")"
  [[ -n "$previous_image_id" ]] || fail "current produccion_fg image is unknown"
  [[ "$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER")" == "healthy" ]] ||
    fail "current produccion_fg container is not healthy"
  curl -fsS "$HEALTH_URL" >/dev/null || fail "current produccion_fg health endpoint failed"

  indufor_before="$(docker inspect -f '{{.Id}}|{{.Image}}' registro_produccion_indufor)"
  demo_before="$(docker inspect -f '{{.Id}}|{{.Image}}' registro_produccion_indufor_demo)"

  log "Preflight successful"
  printf 'deployed_commit=%s\n' "$deployed_commit"
  printf 'target_commit=%s\n' "$target_commit"
  printf 'package_sha256=%s\n' "$package_sha"
}

exec 9>"$LOCK_FILE"
flock -n 9 || fail "another produccion_fg deploy is running"
preflight

if [[ "$mode" == "--check" ]]; then
  exit 0
fi

if [[ "$assume_yes" != true ]]; then
  [[ -t 0 ]] || fail "--deploy requires an interactive terminal or --yes"
  read -r -p "Type DEPLOY to continue: " answer
  [[ "$answer" == "DEPLOY" ]] || fail "deployment cancelled"
fi

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"
manifest="$BACKUP_DIR/deploy_${timestamp}_${target_commit}.env"
rollback_tag="registro_produccion:rollback-${timestamp}"
previous_frontend="$APP_PARENT/frontend.previous-${timestamp}"
failed_frontend="$APP_PARENT/frontend.failed-${timestamp}"
previous_manifest="$APP_PARENT/RELEASE_MANIFEST.previous-${timestamp}.txt"
failed_manifest="$APP_PARENT/RELEASE_MANIFEST.failed-${timestamp}.txt"
staging_frontend="$APP_PARENT/frontend.next-${timestamp}"

tar -czf "$BACKUP_DIR/frontend_${timestamp}_${deployed_commit}.tar.gz" -C "$APP_PARENT" frontend
cp "$APP_PARENT/RELEASE_MANIFEST.txt" "$BACKUP_DIR/RELEASE_MANIFEST_${timestamp}_${deployed_commit}.txt"
printf '%s\n' \
  "deployed_commit=$deployed_commit" \
  "previous_image_id=$previous_image_id" \
  "target_commit=$target_commit" \
  "package_sha256=$package_sha" \
  "started_at=$timestamp" >"$manifest"
chmod 600 "$manifest"
docker tag "$previous_image_id" "$rollback_tag"

mkdir "$staging_frontend"
cp -a "$tmp_dir/frontend/dist/." "$staging_frontend/"
grep -qi '<div id="app"></div>' "$staging_frontend/index.html" ||
  fail "staged frontend does not contain app marker"
frontend_asset="$(grep -oE 'assets/index-[A-Za-z0-9_-]+\.js' "$staging_frontend/index.html" | head -1)"
[[ -n "$frontend_asset" ]] || fail "staged frontend main asset not found"

trap handle_error ERR
trap handle_signal INT TERM

target_image="registro_produccion:${target_commit}"
log "Building immutable image $target_image"
docker build --tag "$target_image" .
docker run --rm "$target_image" python -m compileall -q /app
docker run --rm "$target_image" python -c "import app.main"
target_image_id="$(docker image inspect "$target_image" --format '{{.Id}}')"

docker tag "$target_image" registro_produccion:latest
deploy_started=true
docker compose -f docker-compose.yml up -d --no-build --no-deps --force-recreate "$SERVICE"
wait_healthy
[[ "$(docker inspect -f '{{.Image}}' "$CONTAINER")" == "$target_image_id" ]] ||
  fail "running image does not match target image"

mv "$APP_PARENT/frontend" "$previous_frontend"
frontend_previous_created=true
mv "$staging_frontend" "$APP_PARENT/frontend"

printf '%s\n' \
  "name=registro_produccion" \
  "commit=$target_commit" \
  "short_commit=${target_commit:0:7}" \
  "branch=$BRANCH" \
  "built_at=$timestamp" >"$APP_PARENT/RELEASE_MANIFEST.next-${timestamp}.txt"
mv "$APP_PARENT/RELEASE_MANIFEST.txt" "$previous_manifest"
manifest_previous_created=true
mv "$APP_PARENT/RELEASE_MANIFEST.next-${timestamp}.txt" "$APP_PARENT/RELEASE_MANIFEST.txt"

[[ "$(grep -oE 'assets/index-[A-Za-z0-9_-]+\.js' "$APP_PARENT/frontend/index.html" | head -1)" == "$frontend_asset" ]] ||
  fail "published frontend asset does not match package"
wait_healthy

indufor_after="$(docker inspect -f '{{.Id}}|{{.Image}}' registro_produccion_indufor)"
demo_after="$(docker inspect -f '{{.Id}}|{{.Image}}' registro_produccion_indufor_demo)"
[[ "$indufor_after" == "$indufor_before" ]] || fail "indufor changed during deploy"
[[ "$demo_after" == "$demo_before" ]] || fail "indufor_demo changed during deploy"

printf '%s\n' \
  "target_image=$target_image" \
  "target_image_id=$target_image_id" \
  "frontend_asset=$frontend_asset" \
  "status=success" \
  "completed_at=$(date -u +%Y%m%dT%H%M%SZ)" >>"$manifest"
trap - ERR INT TERM

printf '%s\n' \
  "deploy_status=success" \
  "target_commit=$target_commit" \
  "target_image=$target_image" \
  "target_image_id=$target_image_id" \
  "produccion_fg_health=healthy" \
  "produccion_fg_health_url=$HEALTH_URL" \
  "frontend_asset=$frontend_asset" \
  "indufor_unchanged=yes" \
  "indufor_demo_unchanged=yes" \
  "backup_dir=$BACKUP_DIR"
