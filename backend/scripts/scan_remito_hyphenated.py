"""Escanea remitos con formato XX-YYYYYY (solo la parte que quedaba
pendiente despues de la migracion del issue #124)."""
from app.core.config import settings
from sqlalchemy import create_engine, text


def main():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("=== cargacomb.remito con guion y partes numericas ===")
        rows = conn.execute(
            text(
                """
                SELECT remito, COUNT(*) AS total
                FROM cargacomb
                WHERE remito LIKE '%-%'
                  AND remito NOT REGEXP '[A-Z]'
                  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
                  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$'
                GROUP BY remito
                ORDER BY total DESC
                LIMIT 30
                """
            )
        ).all()
        total_general = 0
        for row in rows:
            print(f"  remito={row.remito!r:>14}  total={row.total}")
            total_general += row.total
        print(f"  -> {len(rows)} valores distintos, {total_general} filas en total")

        print()
        print("=== tablero_produccion.remito con guion y partes numericas ===")
        rows = conn.execute(
            text(
                """
                SELECT remito, COUNT(*) AS total
                FROM tablero_produccion
                WHERE remito LIKE '%-%'
                  AND remito NOT REGEXP '[A-Z]'
                  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
                  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$'
                GROUP BY remito
                ORDER BY total DESC
                LIMIT 30
                """
            )
        ).all()
        total_general = 0
        for row in rows:
            print(f"  remito={row.remito!r:>14}  total={row.total}")
            total_general += row.total
        print(f"  -> {len(rows)} valores distintos, {total_general} filas en total")


if __name__ == "__main__":
    main()
