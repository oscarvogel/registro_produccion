import asyncio

from app.api.routes import admin_legacy
from app.schemas.admin import TipoProcesoCreate, TipoProcesoUpdate


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

    def query(self, *_args, **_kwargs):
        return FakeQuery(self.row)

    def commit(self):
        self.commits += 1

    def refresh(self, row):
        self.refreshed.append(row)


class TipoProcesoRow:
    id = 7
    nombre = "Fresa"
    campos = "tn_despachadas"
    activo = 1
    requiere_acta = False
    requiere_predio = False
    requiere_rodal = False


def test_tipo_proceso_create_defaults_location_requirements_to_false():
    payload = TipoProcesoCreate(nombre="Fresa")

    assert payload.requiere_acta is False
    assert payload.requiere_predio is False
    assert payload.requiere_rodal is False


def test_tipo_proceso_response_serializes_location_requirement_flags(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_tipo_proceso_unidad_ids", lambda _db, _row: [3])
    row = TipoProcesoRow()
    row.requiere_acta = True
    row.requiere_predio = False
    row.requiere_rodal = True

    response = admin_legacy._to_tipo_proceso_response(object(), row)

    assert response.requiere_acta is True
    assert response.requiere_predio is False
    assert response.requiere_rodal is True


def test_update_tipo_proceso_persists_location_requirement_flags(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_sync_tipo_proceso_unidades", lambda *_args: None)
    monkeypatch.setattr(admin_legacy, "_tipo_proceso_unidad_ids", lambda _db, _row: [])
    row = TipoProcesoRow()
    db = FakeDb(row)
    payload = TipoProcesoUpdate(
        requiere_acta=True,
        requiere_predio=True,
        requiere_rodal=False,
    )

    response = asyncio.run(admin_legacy.update_tipo_proceso(7, payload, db=db, _=object()))

    assert row.requiere_acta is True
    assert row.requiere_predio is True
    assert row.requiere_rodal is False
    assert response.requiere_acta is True
    assert response.requiere_predio is True
    assert response.requiere_rodal is False
    assert db.commits == 1
