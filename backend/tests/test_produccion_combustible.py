import asyncio
from datetime import date
from types import SimpleNamespace

from app.api.routes import produccion
from app.models.carga_comb import CargaComb
from app.schemas.produccion import TableroProduccionCreate


class FakeMaxQuery:
    def scalar(self):
        return 0


class FakeDb:
    def __init__(self):
        self.added = []

    def query(self, *_args, **_kwargs):
        return FakeMaxQuery()

    def add(self, row):
        self.added.append(row)

    def flush(self):
        pass

    def commit(self):
        pass

    def refresh(self, _row):
        pass


def test_create_produccion_records_combustible_as_egreso(monkeypatch):
    monkeypatch.setattr(produccion, "_validate_restricted_payload", lambda *_args: None)
    db = FakeDb()
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 15),
        cod_equipo=10,
        cod_operador=20,
        cod_un=30,
        combustible=150,
    )

    asyncio.run(
        produccion.create_produccion(
            data=payload,
            db=db,
            user=SimpleNamespace(),
        )
    )

    carga = next(row for row in db.added if isinstance(row, CargaComb))
    assert carga.tipo_mov == "E"
