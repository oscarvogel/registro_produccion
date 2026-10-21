"""Runner de migraciones SQL para el deploy.

Aplica todos los archivos de `db_migrations/*.sql` en orden alfabetico. Las
migraciones del proyecto son idempotentes (usan `information_schema` /
`IF NOT EXISTS`), asi que se pueden correr en cada deploy; es la misma
convencion que usa `deploy_produccion_fg.sh`.

Pensado para ejecutarse como Pre-deployment Command de Coolify:

    python -m app.migrate

Cada archivo se ejecuta como una unidad con soporte multi-statement (los .sql
usan `SET @...; PREPARE ...; EXECUTE ...;`). Si una migracion falla, el comando
sale con codigo distinto de cero para que el deploy aborte.
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

import pymysql
from pymysql.constants import CLIENT
from sqlalchemy.engine import make_url

from app.core.config import settings


class MigrationError(RuntimeError):
    """Falla al aplicar una migracion puntual."""


def _load_secret_env() -> None:
    """Carga `REGISTRO_ENV_FILE` en os.environ.

    Coolify puede correr el Pre-deployment Command sin pasar por el entrypoint
    del container (que es quien normalmente carga el .env protegido). Repetimos
    esa carga aca para tener `DATABASE_URL` disponible.
    """
    env_file = os.environ.get("REGISTRO_ENV_FILE")
    if not env_file:
        return
    path = Path(env_file)
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        comment_index = value.find(" #")
        if comment_index >= 0:
            value = value[:comment_index].rstrip()
        if value[:1] in {"'", '"'}:
            try:
                value = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                pass
        if key:
            os.environ[key] = value


def _setting(name: str, fallback):
    return os.environ.get(name) or fallback


def migrations_dir() -> Path:
    """Ubica el directorio de migraciones.

    Prioriza `DB_MIGRATIONS_DIR`. Si no esta, busca `db_migrations` junto al
    paquete `app`: `/app/db_migrations` dentro del container o
    `<repo>/db_migrations` en desarrollo local.
    """
    _load_secret_env()
    override = _setting("DB_MIGRATIONS_DIR", getattr(settings, "DB_MIGRATIONS_DIR", ""))
    if override:
        return Path(override)

    here = Path(__file__).resolve()
    candidates = [
        here.parents[1] / "db_migrations",
        here.parents[2] / "db_migrations",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


def discover_migrations(directory: Path) -> list[Path]:
    """Devuelve los `.sql` del directorio ordenados por nombre."""
    if not directory.is_dir():
        return []
    return sorted((p for p in directory.glob("*.sql") if p.is_file()), key=lambda p: p.name)


def _connect() -> "pymysql.connections.Connection":
    _load_secret_env()
    database_url = _setting("DATABASE_URL", settings.DATABASE_URL)
    url = make_url(database_url)
    if url.get_backend_name() not in ("mysql", "mariadb", "pymysql"):
        raise MigrationError(
            f"DB_MIGRATIONS: DATABASE_URL no es MySQL/MariaDB (backend={url.get_backend_name()})."
        )

    connect_args: dict = {
        "host": url.host or "localhost",
        "port": int(url.port or 3306),
        "user": url.username or "",
        "password": url.password or "",
        "database": url.database or "",
        "charset": "utf8mb4",
        "autocommit": True,
        "client_flag": CLIENT.MULTI_STATEMENTS,
        "connect_timeout": 10,
        "read_timeout": 120,
        "write_timeout": 120,
    }
    ssl_ca = _setting("MYSQL_SSL_CA", settings.MYSQL_SSL_CA)
    if ssl_ca:
        verify_cert = str(_setting("MYSQL_SSL_VERIFY_CERT", settings.MYSQL_SSL_VERIFY_CERT)).lower() not in ("0", "false", "no")
        verify_identity = str(_setting("MYSQL_SSL_VERIFY_IDENTITY", settings.MYSQL_SSL_VERIFY_IDENTITY)).lower() in ("1", "true", "yes")
        connect_args["ssl"] = {
            "ca": ssl_ca,
            "check_hostname": verify_identity,
            "verify_mode": 1 if verify_cert else 0,
        }
    return pymysql.connect(**connect_args)


def apply_file(connection, path: Path) -> None:
    """Ejecuta un archivo `.sql` completo y consume todos los result sets."""
    sql = path.read_text(encoding="utf-8")
    if not sql.strip():
        return
    with connection.cursor() as cursor:
        cursor.execute(sql)
        # Multi-statement: drenar cada result set para no dejar la conexion
        # "out of sync".
        while cursor.nextset():
            pass


def run(directory: Path | None = None) -> int:
    """Aplica todas las migraciones. Devuelve cuantas aplico."""
    target = directory or migrations_dir()
    files = discover_migrations(target)
    if not files:
        print(f"DB_MIGRATIONS: sin archivos .sql en {target}; nada que aplicar.")
        return 0

    print(f"DB_MIGRATIONS: {len(files)} archivo(s) en {target}")
    connection = _connect()
    try:
        for path in files:
            print(f"DB_MIGRATIONS: aplicando {path.name}")
            try:
                apply_file(connection, path)
            except Exception as exc:  # noqa: BLE001 - se re-lanza con contexto
                raise MigrationError(f"Fallo la migracion {path.name}: {exc}") from exc
    finally:
        connection.close()
    print(f"DB_MIGRATIONS: {len(files)} migracion(es) aplicadas.")
    return len(files)


def main() -> int:
    try:
        run()
    except MigrationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
