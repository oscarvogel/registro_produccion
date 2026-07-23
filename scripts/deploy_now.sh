#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Deploy one-shot para fasa_195
# ---------------------------------------------------------------------------
# Mata el backend legacy del host, borra su venv/app, y re-deploya el
# container Docker con el paquete que este script conoce.
#
# Uso: bajar el script, revisar las variables de abajo, y correr.
#   bash deploy_now.sh
#
# Si queres deployar OTRO paquete, edita PACKAGE y EXPECTED_COMMIT antes.
# ---------------------------------------------------------------------------

set -euo pipefail

# ----- Configuracion (editable) -----
PACKAGE="/home/ferreteria/registro_produccion_deploy_23e4162.tar.gz"
EXPECTED_COMMIT="23e4162f9d770ba4a13a1e20922d492767424afe"
APP_DIR="/var/www/html/django/produccion_fg"
SOURCE_DIR="/srv/apps/registro_produccion"
INTERNAL_CHECK=1
# -------------------------------------

echo "=========================================="
echo "Deploy one-shot para fasa_195"
echo "=========================================="
echo "Paquete:        $PACKAGE"
echo "Commit:         $EXPECTED_COMMIT"
echo "APP_DIR:        $APP_DIR"
echo "SOURCE_DIR:     $SOURCE_DIR"
echo

if [[ ! -f "$PACKAGE" ]]; then
  echo "ERROR: no existe el paquete $PACKAGE" >&2
  echo "Subilo primero con scp o actualiza la variable PACKAGE." >&2
  exit 1
fi

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "ERROR: no existe $SOURCE_DIR (no hay repo git del container)" >&2
  exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
  echo "ERROR: sudo no esta instalado." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker no esta instalado." >&2
  exit 1
fi

# ----- 1) Matar el backend legacy del host (puerto 8005) -----
echo "==> Matando backend legacy del host (puerto 8005)"
LEGACY_PIDS="$(sudo lsof -t -i:8005 2>/dev/null || true)"
if [[ -n "$LEGACY_PIDS" ]]; then
  echo "    PIDs del proceso legacy en :8005: $LEGACY_PIDS"
  sudo kill -9 $LEGACY_PIDS 2>/dev/null || true
  sleep 1
  echo "    Muerto."
else
  echo "    No hay proceso legacy en :8005 (OK)."
fi

# ----- 2) Borrar venv/app legacy del APP_DIR -----
echo "==> Limpiando venv y app legacy del host"
if [[ -d "$APP_DIR/backend/venv" ]]; then
  sudo rm -rf "$APP_DIR/backend/venv"
  echo "    venv borrado."
else
  echo "    No habia venv."
fi
if [[ -d "$APP_DIR/backend/app" ]]; then
  sudo rm -rf "$APP_DIR/backend/app"
  echo "    backend/app borrado."
else
  echo "    No habia backend/app."
fi
echo "    (backend/.env queda intacto: lo usa el script de deploy para las migraciones)"
echo "    (frontend/ queda intacto: nginx lo sirve)"

# ----- 3) Extraer el paquete nuevo -----
echo "==> Extrayendo paquete en /tmp/deploy_staging"
rm -rf /tmp/deploy_staging
mkdir -p /tmp/deploy_staging
tar -xzf "$PACKAGE" -C /tmp/deploy_staging
ls /tmp/deploy_staging/

# ----- 4) Correr el deploy (modo Docker, auto-detectado por el script) -----
echo
echo "==> Corriendo deploy_produccion_fg.sh (modo Docker)"
echo
sudo \
  PACKAGE="$PACKAGE" \
  EXPECTED_COMMIT="$EXPECTED_COMMIT" \
  INTERNAL_CHECK="$INTERNAL_CHECK" \
  bash /tmp/deploy_staging/deploy_produccion_fg.sh

# ----- 5) Validacion final -----
echo
echo "=========================================="
echo "Validacion final"
echo "=========================================="
echo "Health del container:"
curl -fsS http://127.0.0.1:18005/health
echo
echo "Imagen del container (deberia incluir 23e4162):"
docker inspect registro_produccion_produccion_fg --format '{{.Config.Image}}'
echo
echo "Puerto 8005 (legacy) deberia estar libre:"
ss -tlnp 2>/dev/null | grep ':8005' || echo "OK: puerto 8005 libre."
echo
echo "Puerto 18005 (container) deberia estar respondiendo:"
ss -tlnp 2>/dev/null | grep ':18005' || echo "ERROR: puerto 18005 no escucha."

echo
echo "=========================================="
echo "Listo. Hard refresh en el browser:"
echo "  https://produccion.servinlgsm.com.ar/"
echo "=========================================="
