import asyncio

from app.api.routes import admin_legacy
from app.schemas.admin import LugarCargaCreate, LugarCargaResponse, LugarCargaUpdate


class FakeQuery:
    def __init__(self, row):
        self.row = row

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.row


class FakeDb:
    def __init__(self, row):
        self.row = row
        self.commits = 0
        self.refreshed = []
        self.deleted = []
        self.added = []

    def query(self, *_args, **_kwargs):
        return FakeQuery(self.row)

    def commit(self):
        self.commits += 1

    def refresh(self, row):
        self.refreshed.append(row)


class LugarCargaRow:
    idLugarCarga = 42
    Detalle = "BASE FG - STOCK COMBUSTIBLE"
    activo = 1
    unidad_negocio = 1


def test_lugar_carga_create_defaults_unidad_ids_to_empty_list():
    payload = LugarCargaCreate(detalle="Patio Norte")

    assert payload.unidad_ids == []
    assert payload.unidad_negocio == 1


def test_lugar_carga_response_includes_unidad_ids(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_lugar_carga_unidad_ids", lambda _db, _row: [1, 2])
    row = LugarCargaRow()
    row.unidad_negocio = 1

    response = admin_legacy._to_lugar_carga_response(object(), row)

    assert response.idLugarCarga == 42
    assert response.unidad_negocio == 1
    assert response.unidad_ids == [1, 2]
    assert response.activo == 1


def test_lugar_carga_response_falls_back_to_principal_when_pivot_empty(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_lugar_carga_unidad_ids", lambda _db, _row: [])
    row = LugarCargaRow()
    row.unidad_negocio = 3

    response = admin_legacy._to_lugar_carga_response(object(), row)

    assert response.unidad_negocio == 3
    assert response.unidad_ids == [3]


def test_sync_lugar_carga_unidades_falls_back_when_pivot_table_missing(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_table_exists", lambda _db, table: False)
    row = LugarCargaRow()
    row.unidad_negocio = 1
    db = FakeDb(row)

    admin_legacy._sync_lugar_carga_unidades(db, row, [5, 7])

    assert row.unidad_negocio == 5
    assert db.added == []


def test_sync_lugar_carga_unidades_replaces_pivot_rows(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_table_exists", lambda _db, table: True)
    added: list = []
    deleted: list = []

    class PivotQuery:
        def filter(self, *_args, **_kwargs):
            return self

        def delete(self):
            deleted.append(True)
            return 0

    class PivotDb(FakeDb):
        def query(self, *args, **_kwargs):
            if args and args[0] is admin_legacy.LugarCargaUnidadNegocio:
                return PivotQuery()
            return FakeDb(self.row).query(*args)

        def add(self, obj):
            added.append(obj)

    row = LugarCargaRow()
    row.unidad_negocio = 1
    db = PivotDb(row)

    admin_legacy._sync_lugar_carga_unidades(db, row, [2, 3, 2, -1, 0])

    assert row.unidad_negocio == 2
    assert [obj.unidad_negocio for obj in added] == [2, 3]
    assert all(obj.idLugarCarga == 42 for obj in added)
    assert all(obj.prioridad == 100 for obj in added)
    assert all(obj.es_default == 0 for obj in added)
    assert all(obj.activo is True for obj in added)
    assert deleted == [True]


def test_update_lugar_carga_persists_unidad_ids(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_lugar_carga_unidad_ids", lambda _db, _row: [4, 5])
    monkeypatch.setattr(admin_legacy, "_sync_lugar_carga_unidades", lambda *_args: None)
    row = LugarCargaRow()
    row.unidad_negocio = 1
    db = FakeDb(row)
    payload = LugarCargaUpdate(unidad_ids=[4, 5])

    response = asyncio.run(admin_legacy.update_lugar_carga(42, payload, db=db, _=object()))

    assert response.unidad_ids == [4, 5]
    assert response.unidad_negocio == 4
    assert db.commits == 1
