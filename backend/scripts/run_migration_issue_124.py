"""Ejecuta la migracion del issue #124 (LPAD + hifenados).

Aplica los UPDATEs de:
  * db_migrations/20260805_normalize_remito_lpad.sql
  * db_migrations/20260805_normalize_remito_hyphen.sql

y luego corre la consulta de verificacion al final de cada uno.
"""
from app.core.config import settings
from sqlalchemy import create_engine, text


def main():
    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as conn:
        # sql_mode vacio para no romper con '0000-00-00' en caso de
        # futuras validaciones, no deberia afectar este script.
        conn.execute(text("SET SESSION sql_mode = ''"))

        print("=== Parte 1: LPAD de remitos numericos cortos ===")
        updates = [
            (
                "cargacomb.remito",
                """
                UPDATE cargacomb
                SET remito = LPAD(remito, 12, '0')
                WHERE remito REGEXP '^[0-9]+$'
                  AND CHAR_LENGTH(remito) < 12
                """,
            ),
            (
                "cargacomb.remito2",
                """
                UPDATE cargacomb
                SET remito2 = LPAD(remito2, 12, '0')
                WHERE remito2 IS NOT NULL
                  AND remito2 REGEXP '^[0-9]+$'
                  AND CHAR_LENGTH(remito2) < 12
                """,
            ),
            (
                "cargacomb.remito3",
                """
                UPDATE cargacomb
                SET remito3 = LPAD(remito3, 12, '0')
                WHERE remito3 IS NOT NULL
                  AND remito3 REGEXP '^[0-9]+$'
                  AND CHAR_LENGTH(remito3) < 12
                """,
            ),
            (
                "tablero_produccion.remito",
                """
                UPDATE tablero_produccion
                SET remito = LPAD(remito, 12, '0')
                WHERE remito REGEXP '^[0-9]+$'
                  AND CHAR_LENGTH(remito) < 12
                """,
            ),
            (
                "tablero_produccion.remito2",
                """
                UPDATE tablero_produccion
                SET remito2 = LPAD(remito2, 12, '0')
                WHERE remito2 IS NOT NULL
                  AND remito2 REGEXP '^[0-9]+$'
                  AND CHAR_LENGTH(remito2) < 12
                """,
            ),
            (
                "tablero_produccion.remito3",
                """
                UPDATE tablero_produccion
                SET remito3 = LPAD(remito3, 12, '0')
                WHERE remito3 IS NOT NULL
                  AND remito3 REGEXP '^[0-9]+$'
                  AND CHAR_LENGTH(remito3) < 12
                """,
            ),
        ]

        for label, sql in updates:
            result = conn.execute(text(sql))
            print(f"  {label}: {result.rowcount} filas actualizadas")

        print()
        print("=== Parte 2: eliminar guion en remitos hifenados (PPPP-DDDDDDDD) ===")
        # MySQL LTRIM solo acepta 1 argumento; usamos TRIM(LEADING '0' FROM ...).
        hyphen_updates = [
            (
                "cargacomb.remito",
                """
                UPDATE cargacomb
                SET remito = CONCAT(
                        LPAD(
                          CASE WHEN TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', 1)) = ''
                               THEN '0'
                               ELSE TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', 1))
                          END,
                          4, '0'
                        ),
                        LPAD(
                          CASE WHEN TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', -1)) = ''
                               THEN '0'
                               ELSE TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', -1))
                          END,
                          8, '0'
                        )
                      )
                WHERE remito LIKE '%-%'
                  AND remito NOT LIKE '%-%-%'
                  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
                  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$'
                """,
            ),
            (
                "tablero_produccion.remito",
                """
                UPDATE tablero_produccion
                SET remito = CONCAT(
                        LPAD(
                          CASE WHEN TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', 1)) = ''
                               THEN '0'
                               ELSE TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', 1))
                          END,
                          4, '0'
                        ),
                        LPAD(
                          CASE WHEN TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', -1)) = ''
                               THEN '0'
                               ELSE TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', -1))
                          END,
                          8, '0'
                        )
                      )
                WHERE remito LIKE '%-%'
                  AND remito NOT LIKE '%-%-%'
                  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
                  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$'
                """,
            ),
        ]
        for label, sql in hyphen_updates:
            result = conn.execute(text(sql))
            print(f"  {label}: {result.rowcount} filas actualizadas")

        print()
        print("=== Verificacion post-migracion ===")
        rows = conn.execute(
            text(
                """
                SELECT 'cargacomb.remito cortos restantes' AS chequeo,
                       COUNT(*) AS total
                FROM cargacomb
                WHERE remito REGEXP '^[0-9]+$'
                  AND CHAR_LENGTH(remito) < 12
                UNION ALL
                SELECT 'tablero_produccion.remito cortos restantes',
                       COUNT(*)
                FROM tablero_produccion
                WHERE remito REGEXP '^[0-9]+$'
                  AND CHAR_LENGTH(remito) < 12
                UNION ALL
                SELECT 'cargacomb.remito hifenados restantes',
                       COUNT(*)
                FROM cargacomb
                WHERE remito LIKE '%-%'
                  AND remito NOT LIKE '%-%-%'
                  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
                  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$'
                UNION ALL
                SELECT 'tablero_produccion.remito hifenados restantes',
                       COUNT(*)
                FROM tablero_produccion
                WHERE remito LIKE '%-%'
                  AND remito NOT LIKE '%-%-%'
                  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
                  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$'
                """
            )
        ).all()
        for row in rows:
            print(f"  {row.chequeo}: {row.total}")


if __name__ == "__main__":
    main()
