"""Tests de regresion para el combustible asociado a un parte.

Issue #95: cuando el operador marca "Se cargo combustible?", ademas de los
litros tiene que poder cargar hasta 3 remitos. Esos valores se persisten en
``tablero_produccion.remito/remito2/remito3``.

Issue #105: una carga informada en Produccion crea exactamente un egreso en
``cargacomb`` dentro de la misma transaccion. El endpoint de Combustible queda
para abastecimientos que no tienen parte de produccion.
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
        form_uuid="parte-combustible-1",
        combustible=150,
        km_combustible=14855,
        lugar_carga=42,
        remito="R-0001",
        remito2="R-0002",
        remito3="R-0003",
    )

    assert payload.remito == "R-0001"
    assert payload.remito2 == "R-0002"
    assert payload.remito3 == "R-0003"
    assert payload.km_combustible == 14855


def test_schema_remito_defaults_to_empty_string():
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        combustible=0,
    )

    assert payload.remito == ""
    assert payload.remito2 == ""
    assert payload.remito3 == ""


@pytest.mark.parametrize(
    ("overrides", "expected_message"),
    [
        ({"form_uuid": ""}, "identidad estable"),
        ({"km_combustible": 0}, "kilometraje u horometro"),
        ({"lugar_carga": 0}, "lugar de carga"),
        ({"remito": ""}, "Remito 1"),
    ],
)
def test_schema_requires_complete_stock_data_when_fuel_is_loaded(
    overrides,
    expected_message,
):
    data = {
        "fecha": date(2026, 7, 28),
        "form_uuid": "parte-combustible-completo",
        "combustible": 80,
        "km_combustible": 14855,
        "lugar_carga": 42,
        "remito": "R-0001",
    }
    data.update(overrides)

    with pytest.raises(ValidationError, match=expected_message):
        TableroProduccionCreate(**data)


@pytest.mark.parametrize("field", ["remito", "remito2", "remito3"])
def test_schema_rejects_remito_longer_than_twelve_chars(field):
    with pytest.raises(ValidationError):
        TableroProduccionCreate(
            fecha=date(2026, 7, 28),
            combustible=0,
            **{field: "x" * 13},
        )


# ─── Issue #124: normalizacion de remito a formato canonico ────────────────


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("1", "000000000001"),
        ("11278", "000000011278"),
        ("011278", "000000011278"),
        ("000000011278", "000000011278"),
        ("21325", "000000021325"),
        ("R-0001", "R-0001"),
    ],
)
def test_schema_normaliza_remito_numerico_y_alfanumerico(entrada, esperado):
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        combustible=0,
        remito=entrada,
    )
    assert payload.remito == esperado


@pytest.mark.parametrize(
    ("remito2", "remito3", "exp2", "exp3"),
    [
        ("11278", "21325", "000000011278", "000000021325"),
        ("R-0002", "R-0003", "R-0002", "R-0003"),
        ("", "", "", ""),
    ],
)
def test_schema_normaliza_remito2_y_remito3(remito2, remito3, exp2, exp3):
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        combustible=0,
        remito2=remito2,
        remito3=remito3,
    )
    assert payload.remito2 == exp2
    assert payload.remito3 == exp3


def test_schema_rechaza_remito_con_caracteres_invalidos():
    with pytest.raises(ValidationError, match="letras, numeros y guion"):
        TableroProduccionCreate(
            fecha=date(2026, 7, 28),
            combustible=0,
            remito="11.278",
        )


def test_schema_rechaza_remito_numerico_con_mas_de_12_digitos():
    # El max_length=12 del schema lo corta antes de llegar a mi validador.
    with pytest.raises(ValidationError, match="at most 12 characters"):
        TableroProduccionCreate(
            fecha=date(2026, 7, 28),
            combustible=0,
            remito="1234567890123",
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


def test_create_persists_part_and_stock_movement_in_one_transaction(monkeypatch):
    db = FakeDb()
    _bypass_external_deps(monkeypatch)

    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        form_uuid="parte-combustible-atomic",
        UN="BIOMASA FRESA",
        cod_un=1,
        cod_equipo=10,
        cod_operador=5,
        combustible=150,
        km_combustible=14855,
        lugar_carga=42,
        id_tipo_comb=2,
        remito="R-0001",
        remito2="R-0002",
        remito3="R-0003",
    )

    asyncio.run(produccion.create_produccion(payload, db=db, user=SimpleNamespace()))

    assert db.commits == 1
    assert len(db.added) == 2

    tablero = db.added[0]
    carga = db.added[1]

    assert tablero.remito == "R-0001"
    assert tablero.remito2 == "R-0002"
    assert tablero.remito3 == "R-0003"
    assert tablero.combustible == 150
    assert tablero.lugar_carga == 42
    assert carga.idMovil == 10
    assert carga.idTipoComb == 2
    assert carga.Fecha == date(2026, 7, 28)
    assert carga.KM == 14855
    assert carga.Litros == 150
    assert carga.idLugarCarga == 42
    assert carga.UnidadNegocio == 1
    assert carga.personal == 5
    assert carga.idtabla == "1"
    assert carga.tabla == "tablero_produccion"
    assert carga.tipo_mov == "E"
    assert carga.remito == "R-0001"
    assert carga.remito2 == "R-0002"
    assert carga.remito3 == "R-0003"
    assert carga.form_uuid == "parte-combustible-atomic"


def test_create_does_not_create_cargacomb_when_combustible_is_zero(monkeypatch):
    db = FakeDb()
    _bypass_external_deps(monkeypatch)

    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        combustible=0,
    )

    asyncio.run(produccion.create_produccion(payload, db=db, user=SimpleNamespace()))

    assert len(db.added) == 1
    tablero = db.added[0]
    assert tablero.combustible == 0


def test_schema_rejects_fuel_without_remito():
    with pytest.raises(ValidationError, match="Remito 1"):
        TableroProduccionCreate(
            fecha=date(2026, 7, 28),
            form_uuid="parte-sin-remito",
            combustible=80,
            km_combustible=14855,
            lugar_carga=42,
            remito="",
        )


# ─── Issue #124: el endpoint persiste el remito ya normalizado ─────────────


def test_create_persists_normalized_remito_in_part_and_carga(monkeypatch):
    db = FakeDb()
    _bypass_external_deps(monkeypatch)

    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 28),
        form_uuid="parte-con-remito-corto",
        UN="BIOMASA FRESA",
        cod_un=1,
        cod_equipo=10,
        cod_operador=5,
        combustible=150,
        km_combustible=14855,
        lugar_carga=42,
        id_tipo_comb=2,
        remito="11278",  # entra sin padding
        remito2="21325",  # idem
        remito3="R-0003",  # alfanumerico: se conserva
    )

    asyncio.run(produccion.create_produccion(payload, db=db, user=SimpleNamespace()))

    tablero = db.added[0]
    carga = db.added[1]
    assert tablero.remito == "000000011278"
    assert tablero.remito2 == "000000021325"
    assert tablero.remito3 == "R-0003"
    assert carga.remito == "000000011278"
    assert carga.remito2 == "000000021325"
    assert carga.remito3 == "R-0003"
