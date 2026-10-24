"""Esquema y flags de la evidencia fotografica (issue #194).

Cubre:
- los flags `requiere_foto_horometro` / `requiere_foto_procesador` en los dos
  schemas de tipo de proceso (admin y produccion),
- la coerccion de NULL ("sin configurar") a False en la API,
- la persistencia de los flags al crear y actualizar un tipo de proceso,
- el modelo de `produccion_evidencia`,
- el contrato de la migracion: tiene que ser idempotente y NO puede pisar la
  configuracion que el administrador cambie en Admin.
"""
import asyncio
from pathlib import Path

from app.api.routes import admin_legacy
from app.core.database import Base
from app.models.evidencia import ProduccionEvidencia
from app.models.tipo_proceso import TipoDeProceso
from app.schemas import admin as admin_schemas
from app.schemas import produccion as produccion_schemas
from app.schemas.admin import TipoProcesoCreate, TipoProcesoUpdate


MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "db_migrations"
    / "20261024_evidencia_produccion.sql"
)


class FakeQuery:
    def __init__(self, row):
        self.row = row

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.row


class FakeDb:
    def __init__(self, row=None):
        self.row = row
        self.commits = 0
        self.added = []
        self.refreshed = []

    def query(self, *_args, **_kwargs):
        return FakeQuery(self.row)

    def add(self, row):
        self.added.append(row)

    def commit(self):
        self.commits += 1

    def refresh(self, row):
        self.refreshed.append(row)
        # La DB real asigna el id; el fake lo imita para que el builder de la
        # respuesta pueda leerlo.
        if getattr(row, "id", None) is None:
            row.id = 1


class TipoProcesoRow:
    id = 7
    nombre = "Fresa"
    campos = "tn_despachadas"
    activo = 1
    requiere_acta = False
    requiere_predio = False
    requiere_rodal = False
    requiere_horometro = True
    requiere_foto_horometro = None
    requiere_foto_procesador = None


# ─── Defaults y exposicion de los flags ───────────────────────────

def test_tipo_proceso_create_defaults_evidence_flags_to_false():
    payload = TipoProcesoCreate(nombre="Fresa")

    assert payload.requiere_foto_horometro is False
    assert payload.requiere_foto_procesador is False


def test_tipo_proceso_update_accepts_evidence_flags():
    payload = TipoProcesoUpdate(requiere_foto_horometro=True, requiere_foto_procesador=True)

    assert payload.requiere_foto_horometro is True
    assert payload.requiere_foto_procesador is True


def test_both_tipo_proceso_responses_expose_evidence_flags():
    # Los dos endpoints usan schemas distintos: el de admin y el de produccion
    # (que alimenta el wizard). Los dos tienen que exponer los flags, igual que
    # paso con `requiere_horometro`.
    for schema in (admin_schemas.TipoProcesoResponse, produccion_schemas.TipoProcesoResponse):
        for flag in ("requiere_foto_horometro", "requiere_foto_procesador"):
            assert flag in schema.model_fields, (schema.__module__, flag)
            assert schema.model_fields[flag].default is False


# ─── NULL ("sin configurar") se expone como False ─────────────────

def test_produccion_response_coerces_unconfigured_flag_to_false():
    # En la base NULL significa "sin configurar". La API lo expone como False
    # para que el frontend siempre reciba un bool.
    class RowSinConfigurar:
        id = 3
        nombre = "PROCESO"
        campos = "m3,plantas"
        requiere_acta = False
        requiere_predio = False
        requiere_rodal = False
        requiere_horometro = True
        requiere_foto_horometro = None
        requiere_foto_procesador = None

    response = produccion_schemas.TipoProcesoResponse.model_validate(RowSinConfigurar())

    assert response.requiere_foto_horometro is False
    assert response.requiere_foto_procesador is False


def test_produccion_response_serializes_configured_flags():
    class RowConfigurado:
        id = 3
        nombre = "PROCESO"
        campos = "m3,plantas"
        requiere_acta = False
        requiere_predio = False
        requiere_rodal = False
        requiere_horometro = True
        requiere_foto_horometro = True
        requiere_foto_procesador = 1

    response = produccion_schemas.TipoProcesoResponse.model_validate(RowConfigurado())

    assert response.requiere_foto_horometro is True
    assert response.requiere_foto_procesador is True


def test_admin_response_coerces_unconfigured_flag_to_false(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_tipo_proceso_unidad_ids", lambda _db, _row: [])

    response = admin_legacy._to_tipo_proceso_response(object(), TipoProcesoRow())

    assert response.requiere_foto_horometro is False
    assert response.requiere_foto_procesador is False


# ─── Persistencia ─────────────────────────────────────────────────

def test_update_tipo_proceso_persists_evidence_flags(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_sync_tipo_proceso_unidades", lambda *_args: None)
    monkeypatch.setattr(admin_legacy, "_tipo_proceso_unidad_ids", lambda _db, _row: [])
    row = TipoProcesoRow()
    db = FakeDb(row)
    payload = TipoProcesoUpdate(requiere_foto_horometro=True, requiere_foto_procesador=False)

    response = asyncio.run(admin_legacy.update_tipo_proceso(7, payload, db=db, _=object()))

    assert row.requiere_foto_horometro is True
    assert row.requiere_foto_procesador is False
    assert response.requiere_foto_horometro is True
    assert response.requiere_foto_procesador is False
    assert db.commits == 1


def test_update_tipo_proceso_keeps_flags_when_not_sent(monkeypatch):
    # `exclude_unset` hace que un PUT sin los flags no los toque: un cliente
    # viejo no puede borrar la configuracion de evidencia por accidente.
    monkeypatch.setattr(admin_legacy, "_sync_tipo_proceso_unidades", lambda *_args: None)
    monkeypatch.setattr(admin_legacy, "_tipo_proceso_unidad_ids", lambda _db, _row: [])
    row = TipoProcesoRow()
    row.requiere_foto_horometro = True
    row.requiere_foto_procesador = True
    db = FakeDb(row)

    asyncio.run(admin_legacy.update_tipo_proceso(7, TipoProcesoUpdate(nombre="Fresa"), db=db, _=object()))

    assert row.requiere_foto_horometro is True
    assert row.requiere_foto_procesador is True


def test_create_tipo_proceso_persists_evidence_flags(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_sync_tipo_proceso_unidades", lambda *_args: None)
    monkeypatch.setattr(admin_legacy, "_tipo_proceso_unidad_ids", lambda _db, _row: [])
    db = FakeDb(TipoProcesoRow())
    payload = TipoProcesoCreate(
        nombre="Fresa",
        requiere_foto_horometro=True,
        requiere_foto_procesador=True,
    )

    asyncio.run(admin_legacy.create_tipo_proceso(payload, db=db, _=object()))

    assert len(db.added) == 1
    created = db.added[0]
    assert created.requiere_foto_horometro is True
    assert created.requiere_foto_procesador is True


# ─── Modelo ───────────────────────────────────────────────────────

def test_tipo_proceso_model_has_evidence_flag_columns():
    columns = TipoDeProceso.__table__.columns

    assert "requiere_foto_horometro" in columns
    assert "requiere_foto_procesador" in columns
    # NULL = "sin configurar": la columna tiene que admitir null.
    assert columns["requiere_foto_horometro"].nullable is True
    assert columns["requiere_foto_procesador"].nullable is True


def test_produccion_evidencia_model_is_registered():
    assert "produccion_evidencia" in Base.metadata.tables

    columns = ProduccionEvidencia.__table__.columns
    for expected in (
        "id",
        "registro_id",
        "form_uuid",
        "tipo",
        "incluye_horometro",
        "archivo",
        "mime",
        "tamano",
        "hash_sha256",
        "estado",
        "cargado_por",
        "cargado_por_id",
        "verificado_por",
        "verificado_at",
        "comentario",
        "created_at",
    ):
        assert expected in columns, expected


def test_produccion_evidencia_indexes_form_uuid_and_tipo():
    # Issue #198 (D-F): el indice UNIQUE (form_uuid, tipo) paso a ser un
    # indice NORMAL. Con D-F puede haber mas de una fila por tipo: la foto
    # rechazada queda como historial y la nueva la reemplaza. La unicidad
    # "una sola evidencia viva por tipo" la garantiza la aplicacion.
    indices = {
        tuple(sorted(column.name for column in index.columns)): index.name
        for index in ProduccionEvidencia.__table__.indexes
    }

    assert indices.get(("form_uuid", "tipo")) == "idx_evidencia_form_tipo"


def test_produccion_evidencia_has_no_unique_constraint_on_form_uuid_and_tipo():
    constraints = {
        tuple(sorted(col.name for col in constraint.columns))
        for constraint in ProduccionEvidencia.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert ("form_uuid", "tipo") not in constraints


# ─── Contrato de la migracion ─────────────────────────────────────

def _migration_sql() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


def test_migration_file_exists():
    assert MIGRATION_PATH.is_file()


def test_migration_creates_the_evidence_table_idempotently():
    sql = _migration_sql()

    assert "CREATE TABLE IF NOT EXISTS produccion_evidencia" in sql


def test_migration_adds_columns_with_information_schema_guard():
    # El runner aplica TODOS los .sql en cada deploy: el ALTER tiene que
    # comprobar information_schema antes de agregarla.
    sql = _migration_sql()

    assert "information_schema.COLUMNS" in sql
    assert "ADD COLUMN requiere_foto_horometro" in sql
    assert "ADD COLUMN requiere_foto_procesador" in sql


def test_migration_seed_never_overwrites_admin_configuration():
    # La configuracion inicial solo puede tocar filas con el flag en NULL.
    # Un UPDATE sin ese filtro volveria a pisar, en cada deploy, lo que el
    # administrador ajusto en Admin.
    sql = _migration_sql()

    assert "requiere_foto_horometro IS NULL" in sql
    assert "requiere_foto_procesador IS NULL" in sql


def test_migration_seeds_the_agreed_initial_configuration():
    sql = _migration_sql()

    assert "'HORAS MAQUINAS', 'PROCESO'" in sql
    assert "'PROCESO', 'VOLTEO'" in sql
