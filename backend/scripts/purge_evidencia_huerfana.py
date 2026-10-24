"""Barre los archivos de evidencia que ya no corresponden a ningun registro.

Las fotos de evidencia viven en disco (volumen Docker), no en la base. Si el
operador sube una foto y nunca completa el parte, o si el registro se borra,
el archivo queda huerfano y ocupa espacio para siempre.

Este script:

  1. consulta que filas de `produccion_evidencia` siguen VIVAS (vinculadas a
     un registro de produccion, o con un `form_uuid` que existe en
     `tablero_produccion`),
  2. recorre el directorio de evidencia y separa lo que no corresponde a
     ninguna fila viva,
  3. borra lo huerfano que sea mas viejo que `--dias`, para no tocar una foto
     que todavia esta encolada en un telefono sin conexion.

Por defecto SOLO INFORMA. Hay que pasar `--si` para borrar.

Uso:
    python scripts/purge_evidencia_huerfana.py            # informa
    python scripts/purge_evidencia_huerfana.py --si       # borra
    python scripts/purge_evidencia_huerfana.py --dias 30   # mas margen

Dentro del contenedor el script queda en /app/scripts/ y el volumen en
/app/media, asi que se corre igual:
    docker compose exec produccion_fg python scripts/purge_evidencia_huerfana.py --si
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Para que `python scripts/purge_evidencia_huerfana.py` funcione desde
# backend/ (y desde /app en el contenedor): al correr un script, sys.path[0]
# es la carpeta del script, no la raiz del backend.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, text  # noqa: E402

from app.core.config import settings  # noqa: E402

DEFAULT_MIN_DAYS = 7

# Una fila de evidencia es VIVA si esta vinculada a un registro que existe o si
# su form_uuid corresponde a un parte cargado. Lo que no cumple ninguna de las
# dos es huerfana.
CONDICION_VIVA = """
    (e.registro_id IS NOT NULL
     AND EXISTS (SELECT 1 FROM tablero_produccion t WHERE t.id = e.registro_id))
    OR (e.form_uuid IS NOT NULL AND e.form_uuid <> ''
        AND EXISTS (SELECT 1 FROM tablero_produccion t WHERE t.form_uuid = e.form_uuid))
"""


def filas_vivas(conn) -> list[dict]:
    result = conn.execute(text(f"SELECT e.archivo FROM produccion_evidencia e WHERE {CONDICION_VIVA}"))
    return [dict(row) for row in result.mappings().all()]


def filas_huerfanas(conn) -> list[dict]:
    result = conn.execute(
        text(
            f"""
            SELECT e.id, e.archivo, e.form_uuid, e.registro_id, e.created_at
            FROM produccion_evidencia e
            WHERE NOT ({CONDICION_VIVA})
            """
        )
    )
    return [dict(row) for row in result.mappings().all()]


def es_viejo(fecha, dias: int, ahora: float) -> bool:
    """True si el elemento es mas viejo que la ventana de dias."""
    if fecha is None:
        return False
    return fecha.timestamp() < ahora - dias * 86400


def archivos_en_disco(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return [p for p in root.rglob("*") if p.is_file()]


def relativa(root: Path, path: Path) -> str:
    """Ruta relativa con separadores '/' (como se guarda en la base)."""
    return path.relative_to(root).as_posix()


def plan_borrado(
    root: Path,
    huerfanas: list[dict],
    protegidos: set[str],
    dias: int,
    ahora: float,
) -> list[dict]:
    """Arma la lista de que hay que borrar.

    `huerfanas` son las filas de evidencia sin parte; `protegidos` son las
    rutas relativas de los archivos que corresponden a una fila viva.
    Devuelve una lista de {id, archivo, motivo}. Los archivos en disco que no
    tienen fila ninguna (escritura a medias, fila borrada antes) tambien
    entran, con id None.
    """
    plan: list[dict] = []

    for fila in huerfanas:
        if not es_viejo(fila.get("created_at"), dias, ahora):
            continue
        plan.append(
            {
                "id": fila.get("id"),
                "archivo": fila["archivo"],
                "motivo": "fila de evidencia sin parte",
            }
        )

    for path in archivos_en_disco(root):
        rel = relativa(root, path)
        if rel in protegidos:
            continue
        mtime = path.stat().st_mtime
        if ahora - mtime < dias * 86400:
            continue
        plan.append({"id": None, "archivo": rel, "motivo": "archivo sin fila de evidencia"})

    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Barre archivos de evidencia huerfanos")
    parser.add_argument(
        "--dias",
        type=int,
        default=DEFAULT_MIN_DAYS,
        help=f"Antiguedad minima para borrar (default {DEFAULT_MIN_DAYS} dias)",
    )
    parser.add_argument(
        "--si",
        action="store_true",
        help="Borra de verdad. Sin este flag solo informa.",
    )
    parser.add_argument(
        "--directorio",
        default=None,
        help="Directorio de evidencia (default: EVIDENCIA_STORAGE_DIR)",
    )
    args = parser.parse_args()

    root = Path(args.directorio or settings.EVIDENCIA_STORAGE_DIR).resolve()
    ahora = time.time()

    print("=== Purge de evidencia huerfana ===")
    print(f"directorio: {root}")
    print(f"antiguedad minima: {args.dias} dias")
    print(f"modo: {'BORRAR' if args.si else 'solo informar'}")
    print()

    if not root.is_dir():
        print(f"El directorio no existe todavia: {root}")
        print("No hay nada que purgear.")
        return 0

    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.connect() as conn:
            try:
                vivas = filas_vivas(conn)
                huerfanas = filas_huerfanas(conn)
            except Exception as exc:  # noqa: BLE001
                print(f"No se pudo leer la evidencia ({exc.__class__.__name__}: {exc}).")
                print(
                    "Revisar que la migracion 20261024_evidencia_produccion.sql este aplicada."
                )
                return 1

        protegidos = {fila["archivo"] for fila in vivas}
        plan = plan_borrado(root, huerfanas, protegidos, args.dias, ahora)

        print(f"archivos en disco: {len(archivos_en_disco(root))}")
        print(f"evidencias vivas: {len(vivas)}")
        print(f"evidencias huerfanas (sin parte): {len(huerfanas)}")
        print()

        for item in plan:
            print(f"  [{item['motivo']}] id={item['id']} archivo={item['archivo']}")

        print()
        if not plan:
            print("Nada que borrar.")
            return 0

        if not args.si:
            print(f"Se borrarian {len(plan)} elementos. Revisar y correr con --si.")
            return 0

        borrados = 0
        for item in plan:
            destino = (root / item["archivo"]).resolve()
            # Guarda de seguridad: nunca tocar algo fuera del directorio de evidencia.
            if not destino.is_relative_to(root):
                print(f"  [omitido] ruta fuera del directorio de evidencia: {item['archivo']}")
                continue
            if destino.is_file():
                destino.unlink()
                print(f"  [borrado] archivo {item['archivo']}")
                borrados += 1
            if item["id"] is not None:
                with engine.begin() as conn:
                    conn.execute(
                        text("DELETE FROM produccion_evidencia WHERE id = :id"),
                        {"id": item["id"]},
                    )
                print(f"  [borrado] fila de evidencia id={item['id']}")

        print()
        print(f"Listo: {borrados} archivo(s) borrado(s).")
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    sys.exit(main())
