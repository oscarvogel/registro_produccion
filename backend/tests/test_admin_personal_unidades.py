from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.routes import admin_legacy
from app.models.personal import Personal
from app.models.personal_unidad_negocio import PersonalUnidadNegocio


def test_sync_personal_unidades_persists_more_than_one_business_unit():
    engine = create_engine("sqlite:///:memory:")
    Personal.__table__.create(engine)
    PersonalUnidadNegocio.__table__.create(engine)

    with Session(engine) as db:
        person = Personal(
            Nombre="Ana Alvarez",
            porcentaje=0,
            activo=1,
            unidad_negocio=1,
        )
        db.add(person)
        db.flush()

        admin_legacy._sync_personal_unidades(db, person, [1, 2])
        db.flush()

        stored_unit_ids = [
            row.idUnidadNegocio
            for row in (
                db.query(PersonalUnidadNegocio)
                .filter(PersonalUnidadNegocio.idPersonal == person.idPersonal)
                .order_by(PersonalUnidadNegocio.idUnidadNegocio)
                .all()
            )
        ]

        assert person.unidad_negocio == 1
        assert stored_unit_ids == [1, 2]
