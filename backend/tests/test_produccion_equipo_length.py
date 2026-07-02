from pathlib import Path

from app.models.produccion import TableroProduccion


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_tablero_produccion_equipo_allows_long_machine_names():
    assert TableroProduccion.__table__.c.equipo.type.length == 100


def test_schema_documents_equipo_length_migration():
    migrations = (REPO_ROOT / "migrations.sql").read_text(encoding="utf-8")
    base_schema = (REPO_ROOT / "fg_structure.sql").read_text(encoding="utf-8")

    assert "MODIFY COLUMN equipo VARCHAR(100) NOT NULL DEFAULT ''" in migrations
    assert "`equipo` varchar(100) NOT NULL DEFAULT ''" in base_schema
