import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import admin_catalogs, admin_legacy
from app.core.database import Base
from app.models.cliente import Cliente
from app.models.ubicacion import Predio
from app.schemas.admin import PredioCreate, PredioUpdate


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[Cliente.__table__, Predio.__table__],
    )
    session = sessionmaker(bind=engine)()
    session.add_all([
        Cliente(
            id=1,
            cuit="20-00589501-5",
            razon_social="WEIDMANN ERNESTO PEDRO",
            localidad="PUERTO RICO",
            operaciones=0,
        ),
        Cliente(
            id=2,
            cuit="20-02083476-6",
            razon_social="SUCESION DE GASTIAZORO HORACIO JOSE",
            localidad="UBAJAY",
            operaciones=0,
        ),
    ])
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _admin():
    return SimpleNamespace(idPersonal=1, is_admin=1)


def test_list_clientes_devuelve_el_catalogo_legacy(db):
    rows = asyncio.run(admin_legacy.list_clientes(db=db, _=_admin()))

    assert {row.cuit for row in rows} == {"20-00589501-5", "20-02083476-6"}
    assert all(row.razon_social for row in rows)


def test_list_clientes_filtra_por_cuit_y_razon_social(db):
    por_razon = asyncio.run(admin_legacy.list_clientes(db=db, buscar="WEIDMANN", _=_admin()))
    por_cuit = asyncio.run(admin_legacy.list_clientes(db=db, buscar="20-0208", _=_admin()))

    assert [row.cuit for row in por_razon] == ["20-00589501-5"]
    assert [row.cuit for row in por_cuit] == ["20-02083476-6"]


def test_validar_empresa_cliente_acepta_un_cuit_existente(db):
    admin_legacy._validar_empresa_cliente(db, "20-00589501-5")


def test_validar_empresa_cliente_rechaza_un_cuit_inexistente(db):
    with pytest.raises(HTTPException) as excinfo:
        admin_legacy._validar_empresa_cliente(db, "99-99999999-9")

    assert excinfo.value.status_code == 422
    assert "no existe" in excinfo.value.detail


def test_create_predio_rechaza_empresa_inexistente(db):
    payload = PredioCreate(nombre="Predio X", empresa="99-99999999-9")

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(admin_legacy.create_predio(payload, db=db, _=_admin()))

    assert excinfo.value.status_code == 422
    assert db.query(Predio).count() == 0


def test_create_predio_acepta_empresa_existente(db):
    payload = PredioCreate(nombre="Predio X", empresa="20-00589501-5")

    result = asyncio.run(admin_legacy.create_predio(payload, db=db, _=_admin()))

    assert result.nombre == "Predio X"
    assert result.empresa == "20-00589501-5"
    assert db.query(Predio).count() == 1


def test_update_predio_rechaza_empresa_inexistente(db):
    db.add(Predio(idPredio=1, Nombre="Predio 1", empresa="20-00589501-5"))
    db.commit()

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(
            admin_legacy.update_predio(
                1,
                PredioUpdate(empresa="99-99999999-9"),
                db=db,
                _=_admin(),
            )
        )

    assert excinfo.value.status_code == 422


def test_router_admin_expone_el_listado_de_clientes():
    paths = {route.path for route in admin_catalogs.router.routes}

    assert "/admin/clientes" in paths
