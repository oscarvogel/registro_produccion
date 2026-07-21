import asyncio

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.api.routes import admin_legacy
from app.core.database import Base
from app.models.personal import Personal
from app.schemas.admin import PersonalCreate


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
    Base.metadata.create_all(engine, tables=[Personal.__table__])
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()


def test_personal_model_porcentaje_column_is_not_null_with_default():
    column = Personal.__table__.c.porcentaje
    assert column.nullable is False
    assert column.default is not None
    assert column.default.arg == 0.0


def test_create_personal_sets_porcentaje_so_insert_does_not_raise_integrity_error():
    db = _make_session()
    payload = PersonalCreate(nombre="Operario Porcentaje", dni="12345678")

    response = asyncio.run(admin_legacy.create_personal(payload, db, _admin_user()))

    persisted = db.execute(
        select(Personal).where(Personal.idPersonal == response.idPersonal)
    ).scalar_one()
    assert persisted.porcentaje == 0.0