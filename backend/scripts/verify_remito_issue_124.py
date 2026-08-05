"""Verificacion visual del resultado de la migracion del issue #124."""
from app.core.config import settings
from sqlalchemy import create_engine, text


def main():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("=== cargacomb: filas afectadas por la migracion hifenada ===")
        rows = conn.execute(
            text(
                """
                SELECT idCargaComb, Fecha, idMovil, remito
                FROM cargacomb
                WHERE remito IN ('000200001335', '000200001344')
                ORDER BY Fecha, idCargaComb
                """
            )
        ).all()
        for r in rows:
            print(f"  id={r.idCargaComb} fecha={r.Fecha} movil={r.idMovil} remito={r.remito!r}")

        print()
        print("=== tablero_produccion: filas afectadas por la migracion hifenada ===")
        rows = conn.execute(
            text(
                """
                SELECT id, fecha, cod_equipo, remito
                FROM tablero_produccion
                WHERE remito IN ('000200001335', '000200001344')
                ORDER BY fecha, id
                """
            )
        ).all()
        for r in rows:
            print(f"  id={r.id} fecha={r.fecha} equipo={r.cod_equipo} remito={r.remito!r}")


if __name__ == "__main__":
    main()
