#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/html/django/produccion_fg}"
PACKAGE="${1:-}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/registro_produccion}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8005/}"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo bash "$0" "$PACKAGE"
fi

if [[ -z "$PACKAGE" ]]; then
  PACKAGE="$(find /home/ferreteria -maxdepth 1 -name 'registro_produccion_deploy_*.tar.gz' -printf '%T@ %p\n' | sort -nr | awk 'NR == 1 {print $2}')"
fi

if [[ -z "$PACKAGE" || ! -f "$PACKAGE" ]]; then
  echo "ERROR: no existe el paquete: $PACKAGE" >&2
  exit 1
fi

if [[ ! -d "$APP_DIR/backend/venv" ]]; then
  echo "ERROR: no existe el venv esperado: $APP_DIR/backend/venv" >&2
  exit 1
fi

if [[ ! -f "$APP_DIR/backend/.env" ]]; then
  echo "ERROR: no existe backend/.env; no despliego para no romper credenciales." >&2
  exit 1
fi

timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="$BACKUP_DIR/pre_deploy_$timestamp.tar.gz"
tmp_dir="$(mktemp -d)"

cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

echo "==> Validando paquete"
tar -tzf "$PACKAGE" >/dev/null

echo "==> Creando backup: $backup_file"
mkdir -p "$BACKUP_DIR"
tar -C "$APP_DIR" \
  --exclude='backend/venv' \
  --exclude='backend/.env' \
  --exclude='frontend/.env' \
  -czf "$backup_file" \
  backend/app backend/requirements.txt frontend restart.sh

echo "==> Extrayendo paquete"
tar -xzf "$PACKAGE" -C "$tmp_dir"

if [[ ! -d "$tmp_dir/backend/app" || ! -f "$tmp_dir/backend/requirements.txt" || ! -d "$tmp_dir/frontend/dist" ]]; then
  echo "ERROR: el paquete no tiene la estructura esperada." >&2
  exit 1
fi

echo "==> Actualizando backend"
rm -rf "$APP_DIR/backend/app"
cp -a "$tmp_dir/backend/app" "$APP_DIR/backend/"
cp "$tmp_dir/backend/requirements.txt" "$APP_DIR/backend/requirements.txt"

echo "==> Actualizando frontend"
find "$APP_DIR/frontend" -mindepth 1 ! -name '.env' -exec rm -rf {} +
cp -a "$tmp_dir/frontend/dist/." "$APP_DIR/frontend/"

echo "==> Instalando dependencias backend"
cd "$APP_DIR/backend"
"$APP_DIR/backend/venv/bin/pip" install -r requirements.txt

echo "==> Reiniciando backend"
bash "$APP_DIR/restart.sh"

echo "==> Verificando health: $HEALTH_URL"
sleep 2
curl -fsS "$HEALTH_URL"
echo

echo "==> Despliegue completado correctamente"
echo "Backup: $backup_file"
