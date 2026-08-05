import asyncio
from contextlib import contextmanager
from datetime import date
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import combustible, produccion
from app.core.database import Base
from app.models.carga_comb import CargaComb
from app.models.lugar_carga import LugarCarga
from app.models.lugar_carga_unidad_negocio import LugarCargaUnidadNegocio
from app.models.movil import Movil
from app.models.personal_unidad_negocio import PersonalUnidadNegocio
from app.models.produccion import TableroProduccion
from app.schemas.combustible import CargaCombustibleCreate
from app.schemas.produccion import TableroProduccionCreate


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            Movil.__table__,
            PersonalUnidadNegocio.__table__,
            LugarCarga.__table__,
            LugarCargaUnidadNegocio.__table__,
            TableroProduccion.__table__,
            CargaComb.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    session.add(
        Movil(
            idMovil=10,
            Patente="TEST-10",
            Detalle="FORWA-N°2",
            idUnidadNegocio=1,
            activo=1,
        )
    )
    session.add(PersonalUnidadNegocio(idPersonal=5, idUnidadNegocio=1))
    session.add(
        LugarCarga(
            idLugarCarga=42,
            Detalle="Pañol COSECHA CTL",
            activo=1,
            unidad_negocio=1,
        )
    )
    session.add(
        LugarCargaUnidadNegocio(
            idLugarCarga=42,
            unidad_negocio=1,
            activo=True,
        )
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _user():
    return SimpleNamespace(
        idPersonal=5,
        Nombre="Operador Test",
        unidad_negocio=1,
    )


def _payload(form_uuid: str) -> CargaCombustibleCreate:
    return CargaCombustibleCreate(
        form_uuid=form_uuid,
        fecha=date(2026, 7, 29),
        id_movil=10,
        litros=160,
        km=14855,
        id_lugar_carga=42,
        id_tipo_comb=1,
        remito="R-0001",
        remito2="R-0002",
        remito3="R-0003",
        observaciones="Carga real de prueba",
    )


def test_schema_requires_a_real_km_or_hour_meter_reading():
    with pytest.raises(ValidationError):
        CargaCombustibleCreate(
            form_uuid="carga-1",
            fecha=date(2026, 7, 29),
            id_movil=10,
            litros=160,
            km=0,
            id_lugar_carga=42,
            remito="R-0001",
        )


def test_combustible_endpoint_writes_a_standalone_inventory_movement(db):
    result = asyncio.run(
        combustible.create_carga_combustible(
            _payload("carga-fisica-1"),
            db=db,
            user=_user(),
        )
    )

    rows = db.query(CargaComb).all()
    assert len(rows) == 1
    row = rows[0]
    assert result.id_carga == row.idCargaComb
    assert row.tipo_mov == "E"
    assert row.tabla == "carga_combustible"
    assert row.KM == 14855
    assert float(row.Litros) == 160
    assert row.idLugarCarga == 42
    assert row.idTipoComb == 1
    assert row.remito == "R-0001"
    assert row.remito2 == "R-0002"
    assert row.remito3 == "R-0003"
    assert row.form_uuid == "carga-fisica-1"


def test_retrying_the_same_form_uuid_is_idempotent(db):
    first = asyncio.run(
        combustible.create_carga_combustible(
            _payload("carga-fisica-reintentada"),
            db=db,
            user=_user(),
        )
    )
    second = asyncio.run(
        combustible.create_carga_combustible(
            _payload("carga-fisica-reintentada"),
            db=db,
            user=_user(),
        )
    )

    assert second.id_carga == first.id_carga
    assert db.query(CargaComb).count() == 1


def test_same_explicit_event_id_cannot_be_written_again_from_the_other_flow(
    db,
    monkeypatch,
):
    monkeypatch.setattr(
        produccion,
        "_validate_restricted_payload",
        lambda *_args, **_kwargs: None,
    )

    @contextmanager
    def no_lock(*_args, **_kwargs):
        yield

    monkeypatch.setattr(produccion, "_form_submission_lock", no_lock)

    production_payload = TableroProduccionCreate(
        fecha=date(2026, 7, 29),
        form_uuid="abastecimiento-compartido",
        cod_operador=5,
        cod_equipo=10,
        cod_un=1,
        combustible=160,
        km_combustible=14855,
        lugar_carga=42,
        remito="R-0001",
    )
    asyncio.run(
        produccion.create_produccion(
            production_payload,
            db=db,
            user=_user(),
        )
    )

    result = asyncio.run(
        combustible.create_carga_combustible(
            _payload("abastecimiento-compartido"),
            db=db,
            user=_user(),
        )
    )

    rows = db.query(CargaComb).all()
    assert len(rows) == 1
    assert rows[0].tabla == "tablero_produccion"
    assert result.id_carga == rows[0].idCargaComb


def test_identical_real_loads_with_different_ids_are_rejected(db):
    """Issue #124 (parte 2): dos cargas con el mismo (movil, fecha, litros,
    remito) y mismo operador se consideran la misma carga fisica aunque
    tengan form_uuids distintos. La segunda debe rebotar con 409 para no
    duplicar el egreso de stock.
    """
    from fastapi import HTTPException

    asyncio.run(
        combustible.create_carga_combustible(
            _payload("carga-fisica-a"),
            db=db,
            user=_user(),
        )
    )
    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            combustible.create_carga_combustible(
                _payload("carga-fisica-b"),
                db=db,
                user=_user(),
            )
        )
    assert excinfo.value.status_code == 409
    assert db.query(CargaComb).count() == 1


def test_form_uuid_matches_the_database_contract():
    assert CargaComb.__table__.c.form_uuid.type.length == 36
    constraint_names = {
        constraint.name
        for constraint in CargaComb.__table__.constraints
    }
    assert "uq_cargacomb_personal_form_uuid" in constraint_names


# ─── Issue #124: normalizacion de remito a formato canonico ────────────────


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        ("1", "000000000001"),
        ("11278", "000000011278"),
        ("011278", "000000011278"),
        ("000000011278", "000000011278"),
        ("R-0001", "R-0001"),
        ("99-99999", "009900099999"),
        ("02-1335", "000200001335"),
    ],
)
def test_schema_combustible_normaliza_remito(entrada, esperado):
    payload = CargaCombustibleCreate(
        form_uuid="carga-1",
        fecha=date(2026, 7, 29),
        id_movil=10,
        litros=160,
        km=14855,
        id_lugar_carga=42,
        remito=entrada,
    )
    assert payload.remito == esperado


def test_schema_combustible_rechaza_remito_con_caracteres_invalidos():
    with pytest.raises(ValidationError, match="letras, numeros y guion"):
        CargaCombustibleCreate(
            form_uuid="carga-1",
            fecha=date(2026, 7, 29),
            id_movil=10,
            litros=160,
            km=14855,
            id_lugar_carga=42,
            remito="11.278",
        )


def test_combustible_endpoint_persiste_remito_normalizado(db):
    """Si el operador tipea ``11278`` (sin padding), el endpoint debe
    guardar ``000000011278`` para no chocar con cargas equivalentes
    que ya estaban en la base con el formato padded.
    """
    payload = CargaCombustibleCreate(
        form_uuid="carga-con-remito-corto",
        fecha=date(2026, 7, 29),
        id_movil=10,
        litros=160,
        km=14855,
        id_lugar_carga=42,
        id_tipo_comb=1,
        remito="11278",
    )

    asyncio.run(
        combustible.create_carga_combustible(
            payload, db=db, user=_user()
        )
    )

    row = db.query(CargaComb).one()
    assert row.remito == "000000011278"


# ─── Issue #124 (parte 2): dedupe por clave natural ─────────────────────


def test_combustible_endpoint_rechaza_carga_duplicada_con_otro_form_uuid(db):
    """Cubre el doble submit del mismo operador: dos form_uuids distintos
    para la misma carga fisica. La segunda llamada debe rebotar con 409.
    """
    first = CargaCombustibleCreate(
        form_uuid="carga-original",
        fecha=date(2026, 7, 29),
        id_movil=10,
        litros=160,
        km=14855,
        id_lugar_carga=42,
        id_tipo_comb=1,
        remito="000000011278",
    )
    asyncio.run(
        combustible.create_carga_combustible(
            first, db=db, user=_user()
        )
    )

    # Misma carga, distinto form_uuid (retry de red, doble click, etc.).
    duplicate = CargaCombustibleCreate(
        form_uuid="carga-retry",
        fecha=date(2026, 7, 29),
        id_movil=10,
        litros=160,
        km=14856,  # KM puede variar
        id_lugar_carga=42,
        id_tipo_comb=1,
        remito="000000011278",
    )

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            combustible.create_carga_combustible(
                duplicate, db=db, user=_user()
            )
        )
    assert excinfo.value.status_code == 409
    assert "Ya existe una carga" in excinfo.value.detail

    # Solo se persiste la primera.
    assert db.query(CargaComb).count() == 1


def test_combustible_endpoint_permite_cargas_distintas(db):
    """Cargas con la misma fecha y movil pero distinto remito son legitimas."""
    a = CargaCombustibleCreate(
        form_uuid="carga-a",
        fecha=date(2026, 7, 29),
        id_movil=10,
        litros=160,
        km=14855,
        id_lugar_carga=42,
        id_tipo_comb=1,
        remito="000000011278",
    )
    b = CargaCombustibleCreate(
        form_uuid="carga-b",
        fecha=date(2026, 7, 29),
        id_movil=10,
        litros=160,
        km=14855,
        id_lugar_carga=42,
        id_tipo_comb=1,
        remito="000000011279",  # remito distinto
    )
    asyncio.run(combustible.create_carga_combustible(a, db=db, user=_user()))
    asyncio.run(combustible.create_carga_combustible(b, db=db, user=_user()))

    assert db.query(CargaComb).count() == 2
