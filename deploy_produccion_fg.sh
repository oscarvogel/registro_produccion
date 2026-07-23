#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Deploy de registro_produccion en fasa_195
# ---------------------------------------------------------------------------
# Detecta automaticamente el modo de deploy:
#   - Si existe SOURCE_DIR/docker-compose.yml -> modo Docker (rebuild del
#     container y restart con --no-deps).
#   - Si no -> modo Host legacy (cp al APP_DIR + restart.sh).
#
# Variables de entorno (todas opcionales, tienen defaults razonables):
#   APP_DIR             Ruta del backend en host (default: /var/www/html/django/produccion_fg)
#   SOURCE_DIR          Ruta del codigo fuente (default: /srv/apps/registro_produccion)
#   PACKAGE             Path al tarball (default: el mas reciente en PACKAGE_DIR)
#   PACKAGE_DIR         Directorio donde se buscan los paquetes (default: /home/ferreteria)
#   BACKUP_DIR          Donde se guardan los backups (default: /var/backups/registro_produccion)
#   EXPECTED_COMMIT     Si esta definida, el tarball debe matchear este commit
#   HEALTH_URL_DOCKER   Health del container (default: http://127.0.0.1:18005/)
#   HEALTH_URL_HOST     Health del host legacy (default: http://127.0.0.1:8005/)
#   PUBLIC_URL          URL publica del sitio (default: https://produccion.servinlgsm.com.ar/)
#   INTERNAL_CHECK       1 = skip del curl externo (hairpin NAT workaround)
#   FORCE_HOST=1        Fuerza modo Host legacy aunque haya docker-compose
# ---------------------------------------------------------------------------

APP_DIR="${APP_DIR:-/var/www/html/django/produccion_fg}"
SOURCE_DIR="${SOURCE_DIR:-/srv/apps/registro_produccion}"
PACKAGE="${1:-}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/registro_produccion}"
HEALTH_URL_DOCKER="${HEALTH_URL_DOCKER:-http://127.0.0.1:18005/}"
HEALTH_URL_HOST="${HEALTH_URL_HOST:-http://127.0.0.1:8005/}"
PUBLIC_URL="${PUBLIC_URL:-https://produccion.servinlgsm.com.ar/}"
EXPECTED_COMMIT="${EXPECTED_COMMIT:-}"
PACKAGE_DIR="${PACKAGE_DIR:-/home/ferreteria}"

# Detectar modo
DOCKER_COMPOSE_FILE=""
if [[ -z "${FORCE_HOST:-}" && -f "${SOURCE_DIR}/docker-compose.yml" ]]; then
  DOCKER_COMPOSE_FILE="${SOURCE_DIR}/docker-compose.yml"
fi

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo \
    APP_DIR="$APP_DIR" \
    SOURCE_DIR="$SOURCE_DIR" \
    PACKAGE="$PACKAGE" \
    BACKUP_DIR="$BACKUP_DIR" \
    HEALTH_URL_DOCKER="$HEALTH_URL_DOCKER" \
    HEALTH_URL_HOST="$HEALTH_URL_HOST" \
    PUBLIC_URL="$PUBLIC_URL" \
    EXPECTED_COMMIT="$EXPECTED_COMMIT" \
    PACKAGE_DIR="$PACKAGE_DIR" \
    FORCE_HOST="${FORCE_HOST:-}" \
    bash "$0" "$PACKAGE"
fi

# Auto-pickear el paquete mas reciente si no se paso
if [[ -z "$PACKAGE" ]]; then
  PACKAGE="$(find "$PACKAGE_DIR" -maxdepth 1 -name 'registro_produccion_deploy_*.tar.gz' -printf '%T@ %p\n' | sort -nr | awk 'NR == 1 {print $2}')"
fi

if [[ -z "$PACKAGE" || ! -f "$PACKAGE" ]]; then
  echo "ERROR: no existe el paquete: $PACKAGE" >&2
  exit 1
fi

echo "==> Paquete: $PACKAGE"
if [[ -n "$DOCKER_COMPOSE_FILE" ]]; then
  echo "==> Modo: Docker (compose file: $DOCKER_COMPOSE_FILE)"
  HEALTH_URL="$HEALTH_URL_DOCKER"
else
  echo "==> Modo: Host legacy"
  HEALTH_URL="$HEALTH_URL_HOST"
  if [[ ! -d "$APP_DIR/backend/venv" ]]; then
    echo "ERROR: no existe el venv esperado: $APP_DIR/backend/venv" >&2
    exit 1
  fi
  if [[ ! -f "$APP_DIR/backend/.env" ]]; then
    echo "ERROR: no existe backend/.env; no despliego para no romper credenciales." >&2
    exit 1
  fi
fi

timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="$BACKUP_DIR/pre_deploy_$timestamp.tar.gz"
tmp_dir="$(mktemp -d)"
rollback_needed=0

cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

apply_db_migrations() {
  # Las migraciones se aplican con el .env del APP_DIR (host) porque apunta
  # a la misma DB que el container. Asi no necesitamos entrar al container.
  local migrations_dir="$tmp_dir/db_migrations"
  if [[ ! -d "$migrations_dir" ]] || ! compgen -G "$migrations_dir/*.sql" >/dev/null; then
    return
  fi

  if ! command -v mysql >/dev/null 2>&1; then
    echo "ERROR: mysql CLI no disponible; no puedo aplicar migraciones DB." >&2
    exit 1
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 no disponible; no puedo leer DATABASE_URL para migraciones DB." >&2
    exit 1
  fi

  echo "==> Aplicando migraciones DB"
  local mysql_defaults
  mysql_defaults="$(mktemp)"
  if ! python3 - "$APP_DIR/backend/.env" >"$mysql_defaults" <<'PY'
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

values = {}
for raw in Path(sys.argv[1]).read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    values[key.strip()] = value.strip().strip("\"'")

url = urlparse(values["DATABASE_URL"])
print("[client]")
print(f"host={url.hostname}")
if url.port:
    print(f"port={url.port}")
print(f"user={unquote(url.username or '')}")
print(f"password={unquote(url.password or '')}")
print(f"database={url.path.lstrip('/')}")
PY
  then
    rm -f "$mysql_defaults"
    echo "ERROR: no pude preparar credenciales mysql desde DATABASE_URL." >&2
    exit 1
  fi
  chmod 600 "$mysql_defaults"
  for migration in "$migrations_dir"/*.sql; do
    echo "==> DB migration: $(basename "$migration")"
    if ! mysql --defaults-extra-file="$mysql_defaults" < "$migration"; then
      rm -f "$mysql_defaults"
      echo "ERROR: fallo migracion DB: $(basename "$migration")" >&2
      exit 1
    fi
  done
  rm -f "$mysql_defaults"
}

restore_backup() {
  if [[ "$rollback_needed" -ne 1 || ! -f "$backup_file" ]]; then
    return
  fi

  echo "==> Fallo detectado; restaurando backup: $backup_file" >&2
  if [[ -n "$DOCKER_COMPOSE_FILE" ]]; then
    # En modo Docker el rollback es: rebuild + up del commit previo
    local previous_commit
    previous_commit="$(awk -F= '$1 == "commit" {print $2}' "$backup_file" | tr -d '\r')"
    if [[ -n "$previous_commit" ]]; then
      echo "==> Rollback Docker: rebuild del commit previo $previous_commit"
      cd "$SOURCE_DIR"
      git reset --hard "$previous_commit"
      docker compose -f "$DOCKER_COMPOSE_FILE" build produccion_fg
      docker compose -f "$DOCKER_COMPOSE_FILE" up -d --no-deps produccion_fg
    fi
  else
    rm -rf "$APP_DIR/backend/app" "$APP_DIR/frontend"
    mkdir -p "$APP_DIR"
    tar -xzf "$backup_file" -C "$APP_DIR"
    if [[ -f "$APP_DIR/restart.sh" ]]; then
      bash "$APP_DIR/restart.sh" || true
    fi
  fi
}
trap restore_backup ERR

echo "==> Validando paquete: $PACKAGE"
tar -tzf "$PACKAGE" >/dev/null
package_sha="$(sha256sum "$PACKAGE" | awk '{print $1}')"
tar -xzf "$PACKAGE" -C "$tmp_dir"

manifest="$tmp_dir/RELEASE_MANIFEST.txt"
if [[ ! -f "$manifest" ]]; then
  echo "ERROR: el paquete no incluye RELEASE_MANIFEST.txt." >&2
  exit 1
fi

release_commit="$(awk -F= '$1 == "commit" {print $2}' "$manifest" | tr -d '\r')"
if [[ -z "$release_commit" ]]; then
  echo "ERROR: RELEASE_MANIFEST.txt no declara commit=." >&2
  exit 1
fi

if [[ -n "$EXPECTED_COMMIT" && "$release_commit" != "$EXPECTED_COMMIT" ]]; then
  echo "ERROR: commit del paquete ($release_commit) no coincide con EXPECTED_COMMIT ($EXPECTED_COMMIT)." >&2
  exit 1
fi

if [[ ! -d "$tmp_dir/backend/app" || ! -f "$tmp_dir/backend/requirements.txt" || ! -d "$tmp_dir/frontend/dist" ]]; then
  echo "ERROR: el paquete no tiene la estructura esperada." >&2
  exit 1
fi

if find "$tmp_dir" -path '*/.env' -o -name '.env.*' | grep -q .; then
  echo "ERROR: el paquete contiene archivos .env; no despliego secretos." >&2
  exit 1
fi

echo "==> Paquete OK"
echo "Commit: $release_commit"
echo "SHA256: $package_sha"

# ---------------------------------------------------------------------------
# MODO DOCKER
# ---------------------------------------------------------------------------
if [[ -n "$DOCKER_COMPOSE_FILE" ]]; then
  echo "==> Creando backup del estado actual de SOURCE_DIR"
  mkdir -p "$BACKUP_DIR"
  cp "$manifest" "$BACKUP_DIR/RELEASE_MANIFEST.txt.previous"
  (
    cd "$SOURCE_DIR"
    {
      echo "commit=$(git rev-parse HEAD)"
      echo "short_commit=$(git rev-parse --short HEAD)"
      echo "branch=$(git rev-parse --abbrev-ref HEAD)"
    } > "$backup_file"
  )

  echo "==> Sincronizando SOURCE_DIR al commit $release_commit"
  cd "$SOURCE_DIR"
  git fetch origin
  if ! git reset --hard "$release_commit" 2>&1; then
    echo "ERROR: git reset --hard $release_commit fallo. Abortando." >&2
    exit 1
  fi

  rollback_needed=1

  apply_db_migrations

  echo "==> Rebuild del container produccion_fg"
  docker compose -f "$DOCKER_COMPOSE_FILE" build produccion_fg

  echo "==> Re-deploy del container (--no-deps para no tocar indufor)"
  docker compose -f "$DOCKER_COMPOSE_FILE" up -d --no-deps produccion_fg

  # Publicar el frontend que viene en el tarball (nginx lo sirve desde APP_DIR)
  echo "==> Publicando frontend en $APP_DIR/frontend"
  rm -rf "$APP_DIR/frontend.next"
  mkdir -p "$APP_DIR/frontend.next"
  cp -a "$tmp_dir/frontend/dist/." "$APP_DIR/frontend.next/"
  rm -rf "$APP_DIR/frontend.previous"
  if [[ -d "$APP_DIR/frontend" ]]; then
    mv "$APP_DIR/frontend" "$APP_DIR/frontend.previous"
  fi
  mv "$APP_DIR/frontend.next" "$APP_DIR/frontend"

  echo "==> Verificando health interno: $HEALTH_URL"
  sleep 5
  curl -fsS "$HEALTH_URL"
  echo

  if [[ "${INTERNAL_CHECK:-0}" == "1" ]]; then
    echo "==> INTERNAL_CHECK=1: saltando curl externo (hairpin NAT)"
    frontend_index="$APP_DIR/frontend/index.html"
    if [[ ! -f "$frontend_index" ]]; then
      echo "ERROR: no existe $frontend_index; el deploy fallo al publicar el frontend." >&2
      exit 1
    fi
    if ! grep -qi '<div id="app"></div>' "$frontend_index"; then
      echo "ERROR: $frontend_index no contiene '#app' marker; el frontend no quedo bien." >&2
      exit 1
    fi
    echo "==> Frontend dist OK: $frontend_index"
  else
    echo "==> Verificando home publica: $PUBLIC_URL"
    curl -fsSI "$PUBLIC_URL" >/dev/null
    curl -fsS "$PUBLIC_URL" | grep -qi '<div id="app"></div>'
  fi

  echo "==> Imagen actual del container:"
  docker inspect registro_produccion_produccion_fg --format '{{.Config.Image}}'

  rollback_needed=0
  rm -rf "$APP_DIR/frontend.previous"

  echo
  echo "==> Despliegue Docker completado correctamente"
  echo "Commit: $release_commit"
  echo "Backup: $backup_file"
  echo "Package SHA256: $package_sha"
  exit 0
fi

# ---------------------------------------------------------------------------
# MODO HOST LEGACY (fallback)
# ---------------------------------------------------------------------------
echo "==> Creando backup: $backup_file"
mkdir -p "$BACKUP_DIR"
tar -C "$APP_DIR" \
  --exclude='backend/venv' \
  --exclude='backend/.env' \
  --exclude='frontend/.env' \
  -czf "$backup_file" \
  backend/app backend/requirements.txt frontend restart.sh RELEASE_MANIFEST.txt 2>/dev/null || \
tar -C "$APP_DIR" \
  --exclude='backend/venv' \
  --exclude='backend/.env' \
  --exclude='frontend/.env' \
  -czf "$backup_file" \
  backend/app backend/requirements.txt frontend restart.sh

rollback_needed=1

apply_db_migrations

echo "==> Actualizando backend"
rm -rf "$APP_DIR/backend/app"
cp -a "$tmp_dir/backend/app" "$APP_DIR/backend/"
cp "$tmp_dir/backend/requirements.txt" "$APP_DIR/backend/requirements.txt"

echo "==> Preparando frontend en staging"
rm -rf "$APP_DIR/frontend.next"
mkdir -p "$APP_DIR/frontend.next"
cp -a "$tmp_dir/frontend/dist/." "$APP_DIR/frontend.next/"

echo "==> Publicando frontend"
rm -rf "$APP_DIR/frontend.previous"
if [[ -d "$APP_DIR/frontend" ]]; then
  mv "$APP_DIR/frontend" "$APP_DIR/frontend.previous"
fi
mv "$APP_DIR/frontend.next" "$APP_DIR/frontend"

cp "$manifest" "$APP_DIR/RELEASE_MANIFEST.txt"

echo "==> Instalando dependencias backend"
cd "$APP_DIR/backend"
"$APP_DIR/backend/venv/bin/pip" install -r requirements.txt

echo "==> Reiniciando backend (host legacy)"
if [[ -f "$APP_DIR/restart.sh" ]]; then
  bash "$APP_DIR/restart.sh"
else
  echo "WARN: $APP_DIR/restart.sh no existe; el backend del host no se reinicio."
fi

echo "==> Verificando health interno: $HEALTH_URL"
sleep 2
curl -fsS "$HEALTH_URL"
echo

if [[ "${INTERNAL_CHECK:-0}" == "1" ]]; then
  echo "==> INTERNAL_CHECK=1: saltando curl externo (hairpin NAT)"
  frontend_index="$APP_DIR/frontend/index.html"
  if [[ ! -f "$frontend_index" ]]; then
    echo "ERROR: no existe $frontend_index; el deploy fallo al publicar el frontend." >&2
    exit 1
  fi
  if ! grep -qi '<div id="app"></div>' "$frontend_index"; then
    echo "ERROR: $frontend_index no contiene '#app' marker; el frontend no quedo bien." >&2
    exit 1
  fi
  echo "==> Frontend dist OK: $frontend_index"
else
  echo "==> Verificando home publica: $PUBLIC_URL"
  curl -fsSI "$PUBLIC_URL" >/dev/null
  curl -fsS "$PUBLIC_URL" | grep -qi '<div id="app"></div>'
fi

rollback_needed=0
rm -rf "$APP_DIR/frontend.previous"

echo "==> Despliegue Host legacy completado correctamente"
echo "Commit: $release_commit"
echo "Backup: $backup_file"
echo "Package SHA256: $package_sha"
