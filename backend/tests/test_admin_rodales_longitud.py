"""Tests for the rodal name validation in the admin CRUD.

Regression from production (2026-10-21): the rodales admin CRUD accepted a
free-text name like "PIRAY MEDIO - RODAL 90" (23 chars). The catalog column
is varchar(50) so the row was created without complaints, but
``tablero_produccion.rodal`` is varchar(10) and holds the rodal CODE. When
an operator selected that rodal, the INSERT was rejected by MySQL with
error 1406 and the API answered 503.

The admin CRUD now rejects names that do not fit the legacy column, so the
catalog can only hold codes.
"""
import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.api.routes import admin_legacy
from app.core.database import Base
from app.core.legacy_columns import RODAL_MAX_LENGTH
from app.models.personal import Personal
from app.models.ubicacion import Rodal
from app.schemas.admin import RodalCreate, RodalUpdate


def _admin_user() -> Personal:
    return Personal(
        idPersonal=1,
        Nombre="Admin Test",
        is_admin=1,
        encargado=0,
        activo=1,
        porcentaje=0.0,
        unidad_negocio=1,
        dni="1",
    )


def _make_session():
    engine = create_engine("sqlite://", echo=False)
    Base.metadata.create_all(engine, tables=[Rodal.__table__])
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()


def test_create_rodal_rejects_a_label_longer_than_the_legacy_column():
    db = _make_session()
    payload = RodalCreate(rodal="PIRAY MEDIO - RODAL 90", idPredio=110)

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(admin_legacy.create_rodal(payload, db, _admin_user()))

    assert excinfo.value.status_code == 400
    assert "codigo" in str(excinfo.value.detail)
    assert db.execute(select(Rodal)).scalars().all() == []


def test_create_rodal_accepts_a_code():
    db = _make_session()
    payload = RodalCreate(rodal="90", idPredio=110)

    response = asyncio.run(admin_legacy.create_rodal(payload, db, _admin_user()))

    persisted = db.execute(
        select(Rodal).where(Rodal.idRodal == response.idRodal)
    ).scalar_one()
    assert persisted.Rodal == "90"


def test_update_rodal_rejects_a_label_longer_than_the_legacy_column():
    db = _make_session()
    created = asyncio.run(
        admin_legacy.create_rodal(RodalCreate(rodal="90", idPredio=110), db, _admin_user())
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            admin_legacy.update_rodal(
                created.idRodal,
                RodalUpdate(rodal="PIRAY MEDIO - RODAL 90"),
                db,
                _admin_user(),
            )
        )

    assert excinfo.value.status_code == 400
    persisted = db.execute(
        select(Rodal).where(Rodal.idRodal == created.idRodal)
    ).scalar_one()
    assert persisted.Rodal == "90"


def test_rodal_limit_matches_the_legacy_column():
    from app.models.produccion import TableroProduccion

    assert TableroProduccion.__table__.c.rodal.type.length == RODAL_MAX_LENGTH
