"""Infra de la evidencia fotografica (issue #196).

Cubre el contrato de la infraestructura que necesita la evidencia:

- el compose monta UN volumen nombrado, compartido por los dos backends
  (produccion_fg e indufor comparten la base `fg`),
- nginx acepta cuerpos mas grandes que 1 MB en /api/ (si no, las fotos dan 413),
- los settings por defecto apuntan al volumen y el tope del backend es menor
  que el de nginx,
- el barrido de huerfanos solo borra lo que corresponde.
"""
import importlib.util
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"


def _envejecer(path: Path, dias: int) -> None:
    """Deja el archivo con una antiguedad deterministica."""
    marca = time.time() - dias * 86400
    os.utime(path, (marca, marca))


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


# ─── Compose ─────────────────────────────────────────────────────

def test_compose_declares_one_named_evidence_volume():
    compose = read("docker-compose.yml")

    assert "volumes:" in compose
    assert "registro_produccion_evidencia" in compose


def test_compose_mounts_the_evidence_volume_in_both_backends():
    """produccion_fg e indufor comparten la base: si el volumen fuera dos, una
    foto subida por una instancia daria 404 en la otra."""
    compose = read("docker-compose.yml")

    assert compose.count("- evidencia:/app/media") == 2


def test_compose_does_not_use_a_separate_volume_per_instance():
    compose = read("docker-compose.yml")

    assert "evidencia_indufor" not in compose
    assert "evidencia_produccion" not in compose


def test_compose_keeps_the_secret_mounts_read_only():
    compose = read("docker-compose.yml")

    assert compose.count("/run/secrets/registro.env:ro") == 2
    assert compose.count("/run/secrets/mysql-central-ca.pem:ro") == 2


# ─── nginx ──────────────────────────────────────────────────────

def test_nginx_raises_the_body_limit_on_the_api_location():
    nginx = read("frontend/nginx.conf.template")

    match = re.search(r"location /api/ \{(.*?)\}", nginx, re.DOTALL)
    assert match, "no se encontro el location /api/"

    limit = re.search(r"client_max_body_size\s+(\d+)([mk]?);", match.group(1))
    assert limit, "el location /api/ no define client_max_body_size"

    valor = int(limit.group(1))
    unidad = limit.group(2)
    megabytes = valor if unidad in ("", "m") else valor / 1024
    # El default de nginx es 1 MB y las fotos reales lo superan.
    assert megabytes >= 12


def test_nginx_does_not_raise_the_limit_on_the_health_check():
    nginx = read("frontend/nginx.conf.template")

    health = re.search(r"location = /health \{(.*?)\}", nginx, re.DOTALL)
    assert health
    assert "client_max_body_size" not in health.group(1)


def test_nginx_template_has_balanced_blocks():
    """El template se renderiza dentro del contenedor de nginx. Sin binario de
    nginx disponible en el entorno de test, al menos se comprueba que los
    bloques cierran: una llave desbalanceada rompe el arranque del frontend."""
    nginx = read("frontend/nginx.conf.template")

    # Las variables de entorno del template ($host, ${BACKEND_HOST}) no afectan
    # al conteo de llaves.
    assert nginx.count("{") == nginx.count("}"), "llaves desbalanceadas en el template"

    # Todo location debe cerrar su bloque.
    locations = re.findall(r"location [^{]*\{", nginx)
    assert locations, "no se encontro ningun location"
    for location in locations:
        inicio = nginx.index(location) + len(location)
        # El bloque termina en la primera llave de cierre.
        assert "}" in nginx[inicio:], location


# ─── Migracion de la evidencia: la exigencia NO se enciende sola ───

MIGRACION_EVIDENCIA = "db_migrations/20261024_evidencia_produccion.sql"


def test_the_migration_never_turns_the_evidence_requirement_on():
    """La evidencia no se exige por defecto: la activa el administrador.

    La migracion corria con los flags en 1 para HORAS MAQUINAS, PROCESO y
    VOLTEO. Con eso, el deploy encendia la exigencia para todos los
    operadores de una, sin que nadie lo hubiera decidido proceso por
    proceso (issue #212).
    """
    sql = read(MIGRACION_EVIDENCIA)

    assert not re.search(r"SET\s+requiere_foto_\w+\s*=\s*1", sql, re.IGNORECASE)


def test_the_migration_leaves_the_flags_explicitly_off():
    """Los flags quedan en 0 (configurado: no exige evidencia), no en NULL."""
    sql = read(MIGRACION_EVIDENCIA)

    for flag in ("requiere_foto_horometro", "requiere_foto_procesador"):
        assert re.search(
            rf"SET\s+{flag}\s*=\s*0\b", sql, re.IGNORECASE
        ), f"{flag} deberia quedar en 0"


def test_the_migration_only_touches_unconfigured_rows():
    """El UPDATE solo toca filas NULL: si el admin enciende o apaga un flag
    (queda en 1 o en 0), un deploy posterior no lo pisa."""
    sql = read(MIGRACION_EVIDENCIA)

    updates = re.findall(
        r"UPDATE\s+tipo_de_proceso\s+SET\s+requiere_foto_\w+\s*=\s*0(.*?);",
        sql,
        re.IGNORECASE | re.DOTALL,
    )

    assert len(updates) == 2, "se esperaba un UPDATE por flag"
    for bloque in updates:
        assert "IS NULL" in bloque.upper()


def test_the_migration_still_creates_the_evidence_table():
    """Cambiar el default no puede romper el resto de la migracion."""
    sql = read(MIGRACION_EVIDENCIA)

    assert "CREATE TABLE IF NOT EXISTS produccion_evidencia" in sql
    assert "ADD COLUMN requiere_foto_horometro" in sql
    assert "ADD COLUMN requiere_foto_procesador" in sql


# ─── Settings ───────────────────────────────────────────────────

def test_evidence_settings_have_working_defaults():
    sys.path.insert(0, str(BACKEND_ROOT))
    from app.core.config import settings

    # El default tiene que caer dentro del volumen que monta el compose.
    assert settings.EVIDENCIA_STORAGE_DIR.startswith("/app/media")
    assert settings.EVIDENCIA_MAX_UPLOAD_MB == 10


def test_nginx_limit_is_above_the_backend_limit():
    """El backend acepta hasta X MB; nginx tiene que dejar pasar un poco mas
    para que el multipart con sus campos quepa entero."""
    sys.path.insert(0, str(BACKEND_ROOT))
    from app.core.config import settings

    nginx = read("frontend/nginx.conf.template")
    match = re.search(r"location /api/ \{(.*?)\}", nginx, re.DOTALL)
    limit = re.search(r"client_max_body_size\s+(\d+)([mk]?);", match.group(1))
    megabytes = (
        int(limit.group(1)) if limit.group(2) in ("", "m") else int(limit.group(1)) / 1024
    )

    assert megabytes > settings.EVIDENCIA_MAX_UPLOAD_MB


# ─── Script de barrido ───────────────────────────────────────────

def _cargar_script():
    ruta = BACKEND_ROOT / "scripts" / "purge_evidencia_huerfana.py"
    spec = importlib.util.spec_from_file_location("purge_evidencia_huerfana", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_purge_script_only_plans_files_older_than_the_window(tmp_path):
    modulo = _cargar_script()
    ahora = time.time()
    viejo = datetime.now() - timedelta(days=30)
    nuevo = datetime.now() - timedelta(days=1)

    (tmp_path / "2026" / "10").mkdir(parents=True)
    viejo_path = tmp_path / "2026" / "10" / "viejo.jpg"
    viejo_path.write_bytes(b"x")
    nuevo_path = tmp_path / "2026" / "10" / "nuevo.jpg"
    nuevo_path.write_bytes(b"x")

    plan = modulo.plan_borrado(
        tmp_path,
        huerfanas=[{"id": 1, "archivo": "2026/10/viejo.jpg", "created_at": viejo},
                   {"id": 2, "archivo": "2026/10/nuevo.jpg", "created_at": nuevo}],
        protegidos=set(),
        dias=7,
        ahora=ahora,
    )

    archivos = {item["archivo"] for item in plan}
    # La fila vieja entra; la reciente no (puede estar encolada sin conexion).
    assert "2026/10/viejo.jpg" in archivos
    assert "2026/10/nuevo.jpg" not in archivos


def test_purge_script_never_plans_a_live_file(tmp_path):
    modulo = _cargar_script()
    ahora = time.time()
    (tmp_path / "vivo.jpg").write_bytes(b"x")

    plan = modulo.plan_borrado(
        tmp_path,
        huerfanas=[],
        protegidos={"vivo.jpg"},
        dias=0,
        ahora=ahora,
    )

    assert plan == []


def test_purge_script_plans_files_without_a_row(tmp_path):
    modulo = _cargar_script()
    (tmp_path / "sin_fila.jpg").write_bytes(b"x")
    _envejecer(tmp_path / "sin_fila.jpg", 30)

    plan = modulo.plan_borrado(
        tmp_path, huerfanas=[], protegidos=set(), dias=0, ahora=time.time()
    )

    assert [item["archivo"] for item in plan] == ["sin_fila.jpg"]
    assert plan[0]["id"] is None


def test_purge_script_keeps_recent_files_without_a_row(tmp_path):
    """Un archivo reciente sin fila puede ser una foto recien subida que todavia
    no se vinculo: la ventana de dias lo protege."""
    modulo = _cargar_script()
    (tmp_path / "reciente.jpg").write_bytes(b"x")
    _envejecer(tmp_path / "reciente.jpg", 1)

    plan = modulo.plan_borrado(
        tmp_path, huerfanas=[], protegidos=set(), dias=7, ahora=time.time()
    )

    assert plan == []


def test_purge_script_requires_the_confirmation_flag_to_delete(tmp_path):
    """Sin --si el script solo informa: el default nunca borra."""
    modulo = _cargar_script()
    origen = Path(modulo.__file__).read_text(encoding="utf-8")

    assert '"--si"' in origen
    assert "if not args.si:" in origen


@pytest.mark.parametrize("servicio", ["produccion_fg", "indufor"])
def test_purge_script_runs_from_the_backend_folder(servicio):
    """El script tiene que poder correr dentro del contenedor (/app), que es
    donde el compose monta el volumen."""
    ruta = BACKEND_ROOT / "scripts" / "purge_evidencia_huerfana.py"

    assert ruta.is_file()
    assert "from app.core.config import settings" in ruta.read_text(encoding="utf-8")


def test_purge_script_can_be_invoked_as_a_file():
    """`python scripts/purge_evidencia_huerfana.py` deja el backend fuera del
    path (sys.path[0] es la carpeta del script), y entonces `import app` falla.
    Se comprueba con --help, que no llega a tocar la base."""
    import subprocess

    proc = subprocess.run(
        [
            sys.executable,
            str(BACKEND_ROOT / "scripts" / "purge_evidencia_huerfana.py"),
            "--help",
        ],
        capture_output=True,
        text=True,
        cwd=str(BACKEND_ROOT),
    )

    assert proc.returncode == 0, proc.stderr
    assert "ModuleNotFoundError" not in proc.stderr
    assert "--si" in proc.stdout
