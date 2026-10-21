#!/usr/local/bin/python
"""Load a protected runtime env file before starting the application."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path


def load_env_file(path: Path) -> None:
    if not path:
        return
    if not path.is_file():
        raise SystemExit(f"Required environment file not found: {path}")

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise SystemExit(f"Invalid environment line {line_number} in {path}")

        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not key.replace("_", "").isalnum() or key[0].isdigit():
            raise SystemExit(f"Invalid environment key on line {line_number} in {path}")

        value = value.strip()
        comment_index = value.find(" #")
        if comment_index >= 0:
            value = value[:comment_index].rstrip()
        if value[:1] in {"'", '"'}:
            try:
                value = ast.literal_eval(value)
            except (SyntaxError, ValueError) as exc:
                raise SystemExit(f"Invalid quoted value on line {line_number} in {path}") from exc
        os.environ[key] = value


env_file = os.environ.get("REGISTRO_ENV_FILE")
if env_file:
    load_env_file(Path(env_file))


def _app_root() -> Path:
    """Directorio donde vive el paquete `app` (raiz de la imagen: /app)."""
    for candidate in (Path("/app"), Path.cwd()):
        if (candidate / "app" / "migrate.py").is_file():
            return candidate
    return Path.cwd()


def _is_enabled(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def run_migrations() -> None:
    """Aplica `db_migrations/*.sql` antes de levantar la app.

    El deploy de Coolify recrea los containers, asi que este es el punto donde
    las migraciones se aplican solas. El **Pre-deployment Command** de Coolify
    no sirve para apps con build pack `dockercompose`: se ejecuta en un
    contenedor con nombre = uuid del deploy, que para compose nunca se crea
    (falla con "Could not find a valid container").

    - `RUN_MIGRATIONS=1` habilita el paso (esta apagado por default).
    - Si una migracion falla se loguea el error y la app sigue levantando: con
      compose el container anterior ya fue reemplazado, asi que abortar dejaria
      el servicio caido. Con `MIGRATIONS_STRICT=1` se aborta igual.
    """
    if not _is_enabled("RUN_MIGRATIONS"):
        return

    strict = _is_enabled("MIGRATIONS_STRICT")
    root = _app_root()
    print("[entrypoint] aplicando migraciones (python -m app.migrate)...", flush=True)
    result = subprocess.run([sys.executable, "-m", "app.migrate"], cwd=str(root))

    if result.returncode == 0:
        print("[entrypoint] migraciones aplicadas OK", flush=True)
        return

    print(
        f"[entrypoint] ERROR: las migraciones fallaron (exit {result.returncode})",
        file=sys.stderr,
        flush=True,
    )
    if strict:
        raise SystemExit(result.returncode)
    print(
        "[entrypoint] se sigue levantando la app sin las migraciones aplicadas "
        "(MIGRATIONS_STRICT no esta activo)",
        file=sys.stderr,
        flush=True,
    )


if len(sys.argv) < 2:
    raise SystemExit("No application command was provided")

run_migrations()

os.execvp(sys.argv[1], sys.argv[1:])
