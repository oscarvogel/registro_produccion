import asyncio
from contextlib import contextmanager
from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import parte_caminos
from app.core.database import Base
from app.models.carga_comb import CargaComb
from app.models.produccion import TableroProduccion
from app.models.tipo_proceso import TipoDeProceso
from app.models.unidad_negocio import UnidadNegocio
from app.schemas.parte_caminos import ParteCaminosCreate


@pytest.fixture
def caminos_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            UnidadNegocio.__table__,
            TipoDeProceso.__table__,
            TableroProduccion.__table__,
            CargaComb.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    session.add(UnidadNegocio(idUnidadNegocio=7, Nombre=" Caminos ", Prefijo="CAM"))
    session.add_all(
        [
            TipoDeProceso(id=20, nombre=" DISPOSICION ", activo=1),
            TipoDeProceso(id=21, nombre=" REMOLQUE ", activo=1),
        ]
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _payload() -> ParteCaminosCreate:
    return ParteCaminosCreate.model_validate(
        {
            "form_uuid": "11111111-2222-3333-4444-555555555555",
            "fecha": date(2026, 8, 14),
            "cod_equipo": 10,
            "equipo": "  FORWA-N°2 - PAT-001  ",
            "cod_operador": 22,
            "operador": "  Operador Caminos  ",
            "cod_un": 7,
            "UN": "  Caminos  ",
            "hr_inicio": 1,
            "hr_fin": 20,
            "combustible": 120,
            "km_combustible": 14855,
            "lugar_carga": 42,
            "id_tipo_comb": 1,
            "remito": " 123 ",
            "observaciones": "  parte con dos procesos  ",
            "procesos": [
                {
                    "tipo_proceso_id": 20,
                    "predio": "  PUERTO BOSSETTI  ",
                    "acta": "  ACTA-1  ",
                    "rodal": "  R-1  ",
                    "hr_disposicion": 12,
                },
                {
                    "tipo_proceso_id": 21,
                    "predio": "  PUERTO BOSSETTI  ",
                    "acta": "  ACTA-2  ",
                    "rodal": "  R-2  ",
                    "hr_remolque": 5,
                },
            ],
        }
    )


def test_caminos_persists_one_row_per_process_and_one_fuel_movement(
    caminos_db,
    monkeypatch,
):
    monkeypatch.setattr(
        parte_caminos,
        "_validate_restricted_payload",
        lambda *_args, **_kwargs: None,
    )

    @contextmanager
    def no_lock(*_args, **_kwargs):
        yield

    monkeypatch.setattr(parte_caminos, "_form_submission_lock", no_lock)

    result = asyncio.run(
        parte_caminos.create_parte_caminos(
            _payload(),
            db=caminos_db,
            user=SimpleNamespace(idPersonal=22),
        )
    )

    rows = caminos_db.query(TableroProduccion).order_by(TableroProduccion.id).all()
    assert result.registros_creados == 2
    assert len(rows) == 2
    assert {row.form_uuid for row in rows} == {"11111111-2222-3333-4444-555555555555"}
    assert {row.UN for row in rows} == {"Caminos"}
    assert {row.equipo for row in rows} == {"FORWA-N°2 - PAT-001"}
    assert {row.operador for row in rows} == {"Operador Caminos"}
    assert {row.fecha for row in rows} == {date(2026, 8, 14)}
    assert {(row.cod_operador, row.cod_equipo, row.cod_un, row.hr_inicio, row.hr_fin, row.combustible) for row in rows} == {
        (22, 10, 7, 1, 20, 120)
    }
    assert {row.observaciones for row in rows} == {"parte con dos procesos"}
    assert {row.tipo_proceso_id for row in rows} == {20, 21}
    assert {row.operacion for row in rows} == {"DISPOSICION", "REMOLQUE"}
    assert all("+" not in row.operacion for row in rows)

    disposition = next(row for row in rows if row.tipo_proceso_id == 20)
    towing = next(row for row in rows if row.tipo_proceso_id == 21)
    assert (disposition.hr_disposicion, disposition.hr_remolque) == (12, 0)
    assert (towing.hr_disposicion, towing.hr_remolque) == (0, 5)
    assert {row.predio for row in rows} == {"PUERTO BOSSETTI"}
    assert (disposition.acta, disposition.rodal) == ("ACTA-1", "R-1")
    assert (towing.acta, towing.rodal) == ("ACTA-2", "R-2")

    fuel_rows = caminos_db.query(CargaComb).all()
    assert len(fuel_rows) == 1
    assert fuel_rows[0].form_uuid == "11111111-2222-3333-4444-555555555555"
    assert float(fuel_rows[0].Litros) == 120
    assert fuel_rows[0].idtabla == str(rows[0].id)
