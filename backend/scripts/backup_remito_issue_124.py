"""Backup de las columnas remito antes de correr la migracion del issue #124."""
from app.core.config import settings
from sqlalchemy import create_engine, text


def main():
    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as conn:
        # MySQL strict mode rechaza '0000-00-00' en tablero_produccion.fecha.
        # Lo deshabilitamos solo para esta sesion.
        conn.execute(text("SET SESSION sql_mode = ''"))

        conn.execute(text("DROP TABLE IF EXISTS backup_remito_pre_issue_124"))
        conn.execute(
            text(
                """
                CREATE TABLE backup_remito_pre_issue_124 AS
                SELECT idCargaComb AS id, Fecha, idMovil,
                       remito, remito2, remito3, NOW() AS backup_ts
                FROM cargacomb
                """
            )
        )
        n1 = conn.execute(
            text("SELECT COUNT(*) FROM backup_remito_pre_issue_124")
        ).scalar()

        conn.execute(text("DROP TABLE IF EXISTS backup_remito_tablero_pre_issue_124"))
        conn.execute(
            text(
                """
                CREATE TABLE backup_remito_tablero_pre_issue_124 AS
                SELECT id, fecha AS Fecha, cod_equipo AS idMovil,
                       remito, remito2, remito3, NOW() AS backup_ts
                FROM tablero_produccion
                """
            )
        )
        n2 = conn.execute(
            text(
                "SELECT COUNT(*) FROM backup_remito_tablero_pre_issue_124"
            )
        ).scalar()

        print(f"Backup cargacomb: {n1} filas -> backup_remito_pre_issue_124")
        print(f"Backup tablero:   {n2} filas -> backup_remito_tablero_pre_issue_124")


if __name__ == "__main__":
    main()
