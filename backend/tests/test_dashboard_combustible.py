from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from app.api.routes import dashboard
from app.core.database import Base
from app.models.carga_comb import CargaComb
from app.models.movil import Movil
from app.models.produccion import TableroProduccion


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            Movil.__table__,
            TableroProduccion.__table__,
            CargaComb.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    session.add_all([
        Movil(idMovil=1653, Patente="GRUA -N11", Detalle="GRUA HYUNDAI R180LC-9S", idUnidadNegocio=107, activo=1),
        Movil(idMovil=999, Patente="OTRA", Detalle="OTRA MAQUINA", idUnidadNegocio=107, activo=1),
    ])
    session.add_all([
        _parte(100000423, 1653, date(2026, 11, 3), tipo_proceso_id=1),
        _parte(100000456, 1653, date(2026, 11, 4), tipo_proceso_id=1),
    ])
    session.add_all([
        _carga(1653, 107, date(2026, 11, 3), 95, "100000423", "tablero_produccion"),
        _carga(1653, 107, date(2026, 11, 4), 150, "000100000456", "PRODUCCION"),
        _carga(1653, 107, date(2026, 11, 3), 170, "0", "0"),
        _carga(1653, 107, date(2026, 10, 31), 999, "0", "0"),
        _carga(1653, 108, date(2026, 11, 3), 50, "0", "0"),
        _carga(999, 107, date(2026, 11, 3), 60, "0", "0"),
    ])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _parte(parte_id, equipo, fecha, *, tipo_proceso_id):
    return TableroProduccion(
        id=parte_id,
        fecha=fecha,
        equipo="GRUA",
        operador="OPERADOR",
        cod_equipo=equipo,
        cod_operador=5,
        cod_un=107,
        tipo_proceso_id=tipo_proceso_id,
        hr_inicio=0,
        hr_fin=0,
        combustible=0,
    )


def _carga(movil, unidad, fecha, litros, idtabla, tabla):
    return CargaComb(
        idMovil=movil,
        idTipoComb=1,
        Fecha=fecha,
        Litros=litros,
        UnidadNegocio=unidad,
        personal=5,
        tipo_mov="E",
        idtabla=idtabla,
        tabla=tabla,
    )


def test_fuel_total_uses_cargacomb_for_the_equipment_scope(db):
    total = dashboard._fuel_total(
        db, 107, None, 1653, date(2026, 11, 1), date(2026, 11, 30)
    )

    assert total == 415


def test_fuel_total_with_process_filter_uses_only_linked_movements(db):
    total = dashboard._fuel_total(
        db,
        107,
        {"mode": "tipo", "ids": [1]},
        1653,
        date(2026, 11, 1),
        date(2026, 11, 30),
    )

    # 95 + 150; la carga manual de 170 L no está vinculada a un parte.
    assert total == 245


def test_compute_kpi_value_for_fuel_uses_the_stock_ledger(db):
    kpi = SimpleNamespace(campo_origen="combustible", agregacion="SUM")

    valor = dashboard._compute_kpi_value(
        db, kpi, None, 1653, date(2026, 11, 1), date(2026, 11, 30), 107
    )

    assert valor == 415


def test_fuel_evolution_groups_by_load_date(db):
    query = dashboard._fuel_query(
        db, 107, None, 1653, date(2026, 11, 1), date(2026, 11, 30)
    )
    rows = (
        query.with_entities(CargaComb.Fecha, func.sum(CargaComb.Litros).label("valor"))
        .group_by(CargaComb.Fecha)
        .order_by(CargaComb.Fecha)
        .all()
    )

    assert [(str(row[0]), float(row[1])) for row in rows] == [
        ("2026-11-03", 265.0),
        ("2026-11-04", 150.0),
    ]
