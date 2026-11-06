import asyncio
from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import combustible, dashboard, produccion
from app.core.database import Base
from app.models.carga_comb import CargaComb
from app.models.evidencia import ProduccionEvidencia
from app.models.movil import Movil
from app.models.personal_unidad_negocio import PersonalUnidadNegocio
from app.models.produccion import TableroProduccion
from app.services.combustible_resumen import (
    litros_por_parte,
    resumen_combustible_equipos,
)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            Movil.__table__,
            PersonalUnidadNegocio.__table__,
            TableroProduccion.__table__,
            CargaComb.__table__,
            ProduccionEvidencia.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    session.add_all([
        Movil(idMovil=10, Patente="TEST-10", Detalle="GRUA N11", idUnidadNegocio=1, activo=1),
        Movil(idMovil=11, Patente="TEST-11", Detalle="GRUA N12", idUnidadNegocio=1, activo=1),
        Movil(idMovil=12, Patente="TEST-12", Detalle="GRUA N13", idUnidadNegocio=1, activo=1),
        Movil(idMovil=20, Patente="TEST-20", Detalle="OTRA UN", idUnidadNegocio=2, activo=1),
        PersonalUnidadNegocio(idPersonal=5, idUnidadNegocio=1),
    ])
    session.add_all([
        _parte(100, 10, 5, 100, 105),
        _parte(101, 10, 6, 105, 110),
        _parte(102, 11, 5, 200, 208),
        # Parte con litros declarados en tablero_produccion pero sin movimiento
        # en cargacomb: el detalle debe mostrar 0, no el dato declarado.
        _parte(103, 12, 5, 110, 112, combustible=7),
    ])
    session.add_all([
        _carga(id_movil=10, fecha=date(2026, 11, 3), litros=90, idtabla="100", tabla="tablero_produccion", km=1010),
        _carga(id_movil=10, fecha=date(2026, 11, 3), litros=95, idtabla="000000000101", tabla="PRODUCCION", km=1020),
        _carga(id_movil=10, fecha=date(2026, 11, 3), litros=170, idtabla="0", tabla="0", km=1030),
        _carga(id_movil=11, fecha=date(2026, 11, 4), litros=150, idtabla="102", tabla="tablero_produccion", km=2000),
        _carga(id_movil=11, fecha=date(2026, 11, 4), litros=50, idtabla="0", tabla="0", km=2010),
        _carga(id_movil=10, fecha=date(2026, 10, 1), litros=999, idtabla="0", tabla="0", km=1000),
        _carga(id_movil=20, fecha=date(2026, 11, 3), litros=300, idtabla="0", tabla="0", km=3000),
    ])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _parte(parte_id, equipo, operador, hr_inicio, hr_fin, combustible=0):
    return TableroProduccion(
        id=parte_id,
        fecha=date(2026, 11, 3),
        equipo="GRUA",
        operador="OPERADOR",
        cod_equipo=equipo,
        cod_operador=operador,
        cod_un=1,
        hr_inicio=hr_inicio,
        hr_fin=hr_fin,
        combustible=combustible,
        espada=0,
        puntera=0,
        cadena=0,
        pinon=0,
        origen="",
        tabla="",
    )


def _carga(*, id_movil, fecha, litros, idtabla, tabla, km=0, tipo_mov="E", pase=0):
    return CargaComb(
        idMovil=id_movil,
        idTipoComb=1,
        Fecha=fecha,
        Litros=litros,
        UnidadNegocio=1,
        personal=5,
        tipo_mov=tipo_mov,
        idtabla=idtabla,
        tabla=tabla,
        KM=km,
        pase=pase,
    )


def _user():
    return SimpleNamespace(idPersonal=5, Nombre="Operador Test", unidad_negocio=1)


def test_litros_por_parte_encuentra_idtabla_con_y_sin_padding(db):
    litros = litros_por_parte(db, [100, 101, 102])

    assert litros[100] == 90
    assert litros[101] == 95
    assert litros[102] == 150


def test_resumen_equipos_incluye_todas_las_fuentes_y_usa_horometro_por_equipo(db):
    resumen = resumen_combustible_equipos(
        db,
        [10, 11],
        date(2026, 11, 1),
        date(2026, 11, 5),
    )

    # 90 (parte) + 95 (parte con padding) + 170 (manual) + 150 + 50 (equipo 11)
    assert resumen["total_egresos"] == 555
    # 30 h del equipo 10 (KM 1000->1030) + 10 h del equipo 11 (KM 2000->2010)
    assert resumen["total_horas"] == 40
    assert resumen["consumo_por_hora"] == pytest.approx(13.88, abs=0.01)
    assert resumen["equipos"] == [10, 11]

    por_equipo = {item["id_movil"]: item for item in resumen["por_equipo"]}
    assert por_equipo[10]["total_egresos"] == 355
    assert por_equipo[10]["total_horas"] == 30
    assert por_equipo[10]["consumo_por_hora"] == pytest.approx(11.83, abs=0.01)
    assert por_equipo[11]["total_egresos"] == 200
    assert por_equipo[11]["total_horas"] == 10
    assert por_equipo[11]["consumo_por_hora"] == pytest.approx(20.0, abs=0.01)


def test_endpoint_excluye_equipos_de_otra_unidad_de_negocio(db):
    result = asyncio.run(
        combustible.get_resumen_equipos(
            equipos="10,11,20",
            fecha_desde=date(2026, 11, 1),
            fecha_hasta=date(2026, 11, 5),
            db=db,
            user=_user(),
        )
    )

    assert result.equipos == [10, 11]
    assert result.total_egresos == 555
    assert result.total_horas == 40
    assert {item.id_movil for item in result.por_equipo} == {10, 11}


def test_detalle_de_registro_usa_los_litros_del_libro(db):
    result = asyncio.run(
        dashboard.get_registro_detalle(
            101,
            user=SimpleNamespace(
                idPersonal=5,
                is_admin=1,
                encargado=0,
                unidad_negocio=1,
            ),
            db=db,
        )
    )

    assert result.id == 101
    assert result.combustible == 95


def test_listado_de_registros_usa_los_litros_del_libro(db):
    response = asyncio.run(
        dashboard.list_registros(
            page=1,
            page_size=10,
            user=SimpleNamespace(
                idPersonal=5,
                is_admin=1,
                encargado=0,
                unidad_negocio=1,
            ),
            db=db,
        )
    )

    parte = next(item for item in response.items if item.id == 101)
    assert parte.combustible == 95


def test_detalle_sin_movimiento_vinculado_no_usa_litros_declarados(db):
    result = asyncio.run(
        dashboard.get_registro_detalle(
            103,
            user=SimpleNamespace(
                idPersonal=5,
                is_admin=1,
                encargado=0,
                unidad_negocio=1,
            ),
            db=db,
        )
    )

    assert result.id == 103
    assert result.combustible == 0


def test_listado_sin_movimiento_vinculado_no_usa_litros_declarados(db):
    response = asyncio.run(
        dashboard.list_registros(
            page=1,
            page_size=20,
            user=SimpleNamespace(
                idPersonal=5,
                is_admin=1,
                encargado=0,
                unidad_negocio=1,
            ),
            db=db,
        )
    )

    parte = next(item for item in response.items if item.id == 103)
    assert parte.combustible == 0


def test_mis_registros_sin_movimiento_vinculado_no_usa_litros_declarados(db):
    response = asyncio.run(
        produccion.get_mis_registros(
            fecha_desde=date(2026, 11, 1),
            fecha_hasta=date(2026, 11, 5),
            user=_user(),
            db=db,
        )
    )

    parte = next(item for item in response.registros if item.id == 103)
    assert parte.combustible == 0


def test_resumen_equipo_sin_cargas_no_calcula_consumo(db):
    resumen = resumen_combustible_equipos(
        db,
        [12],
        date(2026, 11, 1),
        date(2026, 11, 5),
    )

    item = resumen["por_equipo"][0]
    assert item["id_movil"] == 12
    assert item["total_egresos"] == 0
    assert item["total_horas"] == 0
    assert item["consumo_por_hora"] is None


def test_endpoint_sin_equipos_habilitados_devuelve_ceros(db):
    result = asyncio.run(
        combustible.get_resumen_equipos(
            equipos="20",
            fecha_desde=date(2026, 11, 1),
            fecha_hasta=date(2026, 11, 5),
            db=db,
            user=_user(),
        )
    )

    assert result.equipos == []
    assert result.por_equipo == []
    assert result.total_egresos == 0
    assert result.total_horas == 0
    assert result.consumo_por_hora is None
