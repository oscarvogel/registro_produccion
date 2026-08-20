from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.motivo_no_operativo import MotivoNoOperativo, MotivoNoOperativoUnidadNegocio
from app.models.unidad_negocio import UnidadNegocio
from app.api.routes.motivos_no_operativos import _sync_unidades


def _db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine, tables=[
        UnidadNegocio.__table__,
        MotivoNoOperativo.__table__,
        MotivoNoOperativoUnidadNegocio.__table__,
    ])
    return sessionmaker(bind=engine)()


def test_sync_unidades_activa_solo_las_seleccionadas():
    db = _db()
    db.add_all([
        UnidadNegocio(idUnidadNegocio=1, nombre="UN 1"),
        UnidadNegocio(idUnidadNegocio=2, nombre="UN 2"),
    ])
    motivo = MotivoNoOperativo(codigo="falla", nombre="FALLA", activo=True)
    db.add(motivo)
    db.flush()

    _sync_unidades(db, motivo.id, [1, 2])
    db.flush()
    assert {row.unidad_negocio for row in db.query(MotivoNoOperativoUnidadNegocio).filter_by(activo=True).all()} == {1, 2}

    _sync_unidades(db, motivo.id, [2])
    db.flush()
    activos = db.query(MotivoNoOperativoUnidadNegocio).filter_by(idMotivo=motivo.id, activo=True).all()
    assert [row.unidad_negocio for row in activos] == [2]


def test_motivo_global_inactivo_no_debe_considerarse_disponible():
    db = _db()
    motivo = MotivoNoOperativo(codigo="clima", nombre="CLIMA", activo=False)
    db.add(motivo)
    db.commit()
    assert db.query(MotivoNoOperativo).filter(MotivoNoOperativo.activo.is_(True)).count() == 0
