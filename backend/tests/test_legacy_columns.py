"""Tests for the normalization of catalog values written to ``tablero_produccion``.

Regression from production (2026-10-21): the operator could not save a part
because the API answered 503. The cause was a catalog value wider than the
legacy column:

    rodales.Rodal  varchar(50)  ->  tablero_produccion.rodal  varchar(10)

The rodal entered in the admin CRUD was the label "PIRAY MEDIO - RODAL 90"
(23 chars). MySQL rejected the INSERT with error 1406 ("Data too long for
column 'rodal'") and the global SQLAlchemy handler turned it into a generic
503 ("No se pudieron cargar los datos necesarios..."), so the operator had no
way to know what to fix.

These tests cover:

1. The normalizers: a rodal label is reduced to its code, an acta that does
   not fit is rejected, and descriptive texts are trimmed/fitted.
2. The limits stay in sync with the legacy column widths.
3. ``POST /produccion`` stores the rodal code and answers 422 (instead of a
   503) when the value cannot be reduced.
"""
import asyncio
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes import produccion
from app.core.legacy_columns import (
    ACTA_MAX_LENGTH,
    EQUIPO_MAX_LENGTH,
    OPERADOR_MAX_LENGTH,
    PREDIO_MAX_LENGTH,
    RODAL_MAX_LENGTH,
    fit_legacy_text,
    normalize_acta,
    normalize_rodal,
)
from app.models.produccion import TableroProduccion
from app.schemas.produccion import TableroProduccionCreate


REPO_ROOT = Path(__file__).resolve().parents[2]


# --- normalize_rodal --------------------------------------------------------


def test_short_rodal_code_is_kept_as_is():
    assert normalize_rodal("90") == "90"


def test_rodal_code_is_trimmed():
    assert normalize_rodal("  90  ") == "90"


def test_blank_rodal_is_empty():
    assert normalize_rodal("") == ""
    assert normalize_rodal(None) == ""


def test_rodal_label_is_reduced_to_its_code():
    """The exact value the operator typed in the rodales admin CRUD."""
    assert normalize_rodal("PIRAY MEDIO - RODAL 90") == "90"


def test_rodal_label_code_is_found_in_any_position():
    assert normalize_rodal("RODAL 90 - PIRAY MEDIO") == "90"
    assert normalize_rodal("Predio PIRAY MEDIO, Rodal 96") == "96"


def test_rodal_label_without_code_is_rejected_with_an_actionable_message():
    with pytest.raises(ValueError) as excinfo:
        normalize_rodal("PIRAY MEDIO - TROCHA 5")

    assert "codigo" in str(excinfo.value)


def test_rodal_longer_than_the_column_without_a_code_is_rejected():
    with pytest.raises(ValueError):
        normalize_rodal("LOTES DEL PREDIO PIRAY MEDIO SUR")


# --- normalize_acta ---------------------------------------------------------


def test_acta_is_kept_when_it_fits_the_column():
    assert normalize_acta("7900001519") == "7900001519"


def test_acta_longer_than_the_column_is_rejected():
    """An acta number is a reference: truncating it would point to another
    acta, so it is rejected instead."""
    with pytest.raises(ValueError):
        normalize_acta("79000015190000")


# --- fit_legacy_text --------------------------------------------------------


def test_fit_legacy_text_removes_the_padding_of_the_catalog():
    """`predios.Nombre` is varchar(100) padded with spaces; the legacy
    column is varchar(50)."""
    assert fit_legacy_text("PIRAY KM 4" + " " * 94, PREDIO_MAX_LENGTH) == "PIRAY KM 4"


def test_fit_legacy_text_truncates_to_the_column_width():
    assert fit_legacy_text("A" * 250, EQUIPO_MAX_LENGTH) == "A" * EQUIPO_MAX_LENGTH


def test_fit_legacy_text_keeps_short_values_untouched():
    assert fit_legacy_text("PIRAY MEDIO", PREDIO_MAX_LENGTH) == "PIRAY MEDIO"
    assert fit_legacy_text(None, PREDIO_MAX_LENGTH) == ""


# --- The limits must match the legacy columns --------------------------------


def test_limits_match_the_legacy_column_widths():
    table = TableroProduccion.__table__
    assert table.c.rodal.type.length == RODAL_MAX_LENGTH
    assert table.c.acta.type.length == ACTA_MAX_LENGTH
    assert table.c.predio.type.length == PREDIO_MAX_LENGTH
    assert table.c.equipo.type.length == EQUIPO_MAX_LENGTH
    assert table.c.operador.type.length == OPERADOR_MAX_LENGTH


def test_legacy_schema_declares_the_same_rodal_width():
    """`tablero_produccion` no se migro: el ancho sigue siendo el del
    esquema legacy (ver `migrations.sql`, que solo ensancha `equipo`)."""
    migrations = (REPO_ROOT / "migrations.sql").read_text(encoding="utf-8")

    assert "MODIFY COLUMN equipo VARCHAR(100) NOT NULL DEFAULT ''" in migrations
    assert "MODIFY COLUMN rodal" not in migrations


# --- POST /produccion --------------------------------------------------------


class _FakeQuery:
    def __init__(self):
        self.rows = []

    def filter(self, *_args):
        return self

    def first(self):
        return None

    def scalar(self):
        return 0

    def all(self):
        return []


class _FakeConnection:
    def execute(self, _statement, _params=None):
        return SimpleNamespace(scalar=lambda: 1)

    def close(self):
        pass


class _FakeBind:
    def connect(self):
        return _FakeConnection()


class _FakeDb:
    def __init__(self):
        self.added = []
        self.bind = _FakeBind()

    def get_bind(self):
        return self.bind

    def query(self, *_args):
        return _FakeQuery()

    def add(self, row):
        self.added.append(row)

    def flush(self):
        pass

    def commit(self):
        pass

    def refresh(self, row):
        pass

    def rollback(self):
        pass


def _operador():
    return SimpleNamespace(
        idPersonal=1,
        encargado=0,
        unidad_negocio=1,
    )


def _payload(**overrides):
    data = {
        "fecha": date(2026, 10, 20),
        "UN": "FULL TREE",
        "operacion": "PROCESO",
        "equipo": "Procesador JOHN DEERE 1470G -N 2 ARAUCO",
        "operador": "OPERADOR PRUEBA",
        "predio": "PIRAY MEDIO",
        "acta": "7900001519",
    }
    data.update(overrides)
    return TableroProduccionCreate(**data)


def test_create_saves_the_rodal_code_instead_of_the_label():
    """The payload the operator sent: the label did not fit the legacy
    column and the INSERT was rejected with MySQL 1406."""
    db = _FakeDb()

    asyncio.run(
        produccion.create_produccion(
            _payload(rodal="PIRAY MEDIO - RODAL 90"),
            db=db,
            user=_operador(),
        )
    )

    assert len(db.added) == 1
    assert db.added[0].rodal == "90"


def test_create_keeps_a_short_rodal_code_untouched():
    db = _FakeDb()

    asyncio.run(produccion.create_produccion(_payload(rodal="90"), db=db, user=_operador()))

    assert db.added[0].rodal == "90"


def test_create_answers_422_when_the_rodal_cannot_be_reduced():
    db = _FakeDb()

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            produccion.create_produccion(
                _payload(rodal="PIRAY MEDIO - TROCHA 5"),
                db=db,
                user=_operador(),
            )
        )

    assert excinfo.value.status_code == 422
    assert db.added == []


def test_create_trims_the_padded_predio_name():
    db = _FakeDb()

    asyncio.run(
        produccion.create_produccion(
            _payload(predio="PIRAY KM 4" + " " * 94),
            db=db,
            user=_operador(),
        )
    )

    assert db.added[0].predio == "PIRAY KM 4"


def test_create_truncates_a_machine_description_to_the_legacy_width():
    db = _FakeDb()

    asyncio.run(
        produccion.create_produccion(
            _payload(equipo="A" * 250),
            db=db,
            user=_operador(),
        )
    )

    assert len(db.added[0].equipo) == EQUIPO_MAX_LENGTH
