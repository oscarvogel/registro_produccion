"""Tests de regresion para captura de remitos en el parte de produccion.

Issue #95: cuando el operador marca "Se cargo combustible?", ademas de los
litros tiene que poder cargar hasta 3 remitos. Esos valores se persisten en
``tablero_produccion.remito/remito2/remito3`` y en el ``cargacomb`` que se
crea como movimiento relacionado con los mismos 3 valores.
"""
import asyncio
from contextlib import contextmanager
from datetime import date
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.api.routes import produccion
from app.schemas.produccion import TableroProduccionCreate


# ─── Schema ────────────────────────────────────────────────────────────────


def test_schema_accepts_remito_fields():
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        combustible=150,
        remito="R-0001",
        remito2="R-0002",
        remito3="R-0003",
    )

    assert payload.remito == "R-0001"
    assert payload.remito2 == "R-0002"
    assert payload.remito3 == "R-0003"


def test_schema_remito_defaults_to_empty_string():
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        combustible=0,
    )

    assert payload.remito == ""
    assert payload.remito2 == ""
    assert payload.remito3 == ""


@pytest.mark.parametrize("field", ["remito", "remito2", "remito3"])
def test_schema_rejects_remito_longer_than_twelve_chars(field):
    with pytest.raises(ValidationError):
        TableroProduccionCreate(
            fecha=date(2026, 7, 28),
            combustible=0,
            **{field: "x" * 13},
        )


# ─── Route: persistencia de remitos ────────────────────────────────────────


class FakeQuery:
    """Query en cadena que devuelve ``None`` para first() y 0 para scalar()."""

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return None

    def scalar(self):
        return 0


class FakeDb:
    """Doble de ``Session`` que registra lo agregado y mockea el resto."""

    def __init__(self):
        self.added = []
        self.commits = 0
        self.flushes = 0

    def query(self, *_args, **_kwargs):
        return FakeQuery()

    def add(self, row):
        self.added.append(row)

    def flush(self):
        self.flushes += 1

    def commit(self):
        self.commits += 1

    def refresh(self, _row):
        return None


def _bypass_external_deps(monkeypatch):
    monkeypatch.setattr(
        produccion,
        "_validate_restricted_payload",
        lambda *_a, **_k: None,
    )

    @contextmanager
    def no_lock(*_a, **_k):
        yield

    monkeypatch.setattr(produccion, "_form_submission_lock", no_lock)


def test_create_persists_remitos_in_tablero_and_cargacomb(monkeypatch):
    db = FakeDb()
    _bypass_external_deps(monkeypatch)

    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        UN="BIOMASA FRESA",
        cod_un=1,
        cod_equipo=10,
        cod_operador=5,
        combustible=150,
        lugar_carga=42,
        id_tipo_comb=2,
        remito="R-0001",
        remito2="R-0002",
        remito3="R-0003",
    )

    asyncio.run(produccion.create_produccion(payload, db=db, user=SimpleNamespace()))

    assert db.commits == 1
    assert len(db.added) == 2  # TableroProduccion + CargaComb

    tablero = db.added[0]
    carga = db.added[1]

    assert tablero.remito == "R-0001"
    assert tablero.remito2 == "R-0002"
    assert tablero.remito3 == "R-0003"

    assert carga.remito == "R-0001"
    assert carga.remito2 == "R-0002"
    assert carga.remito3 == "R-0003"
    assert carga.tabla == "tablero_produccion"
    assert carga.Litros == 150
    assert carga.idLugarCarga == 42
    assert carga.idTipoComb == 2


def test_create_falls_back_to_defaults_when_lugar_carga_and_tipo_comb_missing(monkeypatch):
    """Si el cliente no manda lugar_carga o id_tipo_comb, el backend usa 1 (Gasoil default)."""
    db = FakeDb()
    _bypass_external_deps(monkeypatch)

    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        cod_equipo=10,
        cod_operador=5,
        combustible=80,
        # Sin lugar_carga, sin id_tipo_comb
    )

    asyncio.run(produccion.create_produccion(payload, db=db, user=SimpleNamespace()))

    carga = db.added[1]
    assert carga.idLugarCarga == 1  # fallback del schema
    assert carga.idTipoComb == 1    # fallback Gasoil


def test_create_does_not_create_cargacomb_when_combustible_is_zero(monkeypatch):
    db = FakeDb()
    _bypass_external_deps(monkeypatch)

    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        combustible=0,
    )

    asyncio.run(produccion.create_produccion(payload, db=db, user=SimpleNamespace()))

    # Solo se persiste el TableroProduccion; no hay CargaComb.
    assert len(db.added) == 1
    tablero = db.added[0]
    assert tablero.combustible == 0


def test_create_persists_empty_remitos_when_combustible_without_remito(monkeypatch):
    db = FakeDb()
    _bypass_external_deps(monkeypatch)

    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        combustible=80,
        remito="",
        remito2="",
        remito3="",
    )

    asyncio.run(produccion.create_produccion(payload, db=db, user=SimpleNamespace()))

    tablero = db.added[0]
    carga = db.added[1]

    assert tablero.remito == ""
    assert tablero.remito2 == ""
    assert tablero.remito3 == ""
    assert carga.remito == ""
    assert carga.remito2 == ""
    assert carga.remito3 == ""
