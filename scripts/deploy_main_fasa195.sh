#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_HOSTNAME="${EXPECTED_HOSTNAME:-fg-ubuntu}"
APP_DIR="${APP_DIR:-/srv/apps/registro_produccion}"
REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/.deploy-backups}"
LOCK_FILE="${LOCK_FILE:-$APP_DIR/.deploy-main.lock}"
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

rollback() {
  printf 'ERROR: rollback requested before implementation\n' >&2
  return 1
}

# Contract markers replaced with executable behavior in the next TDD cycles:
# git status --porcelain
# git fetch --prune
# git merge-base --is-ancestor
# git merge --ff-only
# registro_produccion:${target_commit}
# docker compose config
# python -m compileall
# import app.main
# indufor produccion_fg
printf '%s\n' "$HEALTH_INDUFOR" "$HEALTH_PRODUCCION_FG" "$BACKUP_DIR" >/dev/null
command -v flock >/dev/null
