from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.carga_comb import CargaComb
from app.models.movil import Movil
from app.models.personal import Personal
from app.models.personal_unidad_negocio import PersonalUnidadNegocio
from app.schemas.combustible import (
    CargaCombustibleCreate,
    CargaCombustibleResponse,
    CombustibleMovilResponse,
)

router = APIRouter(prefix="/combustible", tags=["combustible"])


def _user_unidad_ids(db: Session, user: Personal) -> list[int]:
    try:
        rows = (
            db.query(PersonalUnidadNegocio.idUnidadNegocio)
            .filter(PersonalUnidadNegocio.idPersonal == user.idPersonal)
            .all()
        )
    except SQLAlchemyError:
        db.rollback()
        rows = []

    ids = []
    for (unidad_id,) in rows:
        parsed = int(unidad_id or 0)
        if parsed > 0 and parsed not in ids:
            ids.append(parsed)

    fallback = int(user.unidad_negocio or 0)
    if fallback > 0 and fallback not in ids:
        ids.append(fallback)
    return ids


def _to_movil_response(row: Movil) -> CombustibleMovilResponse:
    return CombustibleMovilResponse(
        idMovil=row.idMovil,
        patente=row.Patente or "",
        detalle=row.Detalle or "",
        id_unidad_negocio=int(row.idUnidadNegocio or 0),
    )


def _to_carga_response(row: CargaComb, movil: Movil, user: Personal) -> CargaCombustibleResponse:
    return CargaCombustibleResponse(
        id_carga=row.idCargaComb,
        fecha=row.Fecha,
        id_movil=row.idMovil,
        movil=movil.Detalle or "",
        patente=movil.Patente or "",
        id_operador=user.idPersonal,
        operador=user.Nombre or "",
        unidad_negocio=int(row.UnidadNegocio or 0),
        litros=float(row.Litros or 0),
        km=int(row.KM or 0),
        observaciones=row.observaciones,
    )


@router.get("/moviles", response_model=list[CombustibleMovilResponse])
async def list_moviles_combustible(
    buscar: str | None = None,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    unidad_ids = _user_unidad_ids(db, user)
    if not unidad_ids:
        return []

    query = db.query(Movil).filter(Movil.idUnidadNegocio.in_(unidad_ids), Movil.activo == 1)
    if buscar:
        pattern = f"%{buscar.strip()}%"
        query = query.filter((Movil.Detalle.ilike(pattern)) | (Movil.Patente.ilike(pattern)))

    rows = query.order_by(Movil.Detalle).limit(limit).all()
    return [_to_movil_response(row) for row in rows]


@router.post("/cargas", response_model=CargaCombustibleResponse, status_code=status.HTTP_201_CREATED)
async def create_carga_combustible(
    payload: CargaCombustibleCreate,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    movil = db.query(Movil).filter(Movil.idMovil == payload.id_movil, Movil.activo == 1).first()
    if not movil:
        raise HTTPException(status_code=400, detail="Movil no encontrado o inactivo")

    unidad_ids = _user_unidad_ids(db, user)
    movil_unidad = int(movil.idUnidadNegocio or 0)
    if movil_unidad not in unidad_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No podes registrar combustible para un movil de otra unidad de negocio",
        )

    now = datetime.now()
    row = CargaComb(
        idMovil=payload.id_movil,
        idTipoComb=1,
        Fecha=payload.fecha,
        KM=payload.km,
        Litros=payload.litros,
        UnidadNegocio=movil_unidad,
        personal=user.idPersonal,
        tipo_mov="E",
        tabla="carga_combustible",
        _usuario="web",
        _fecha=now.date(),
        _hora=now.strftime("%H:%M:%S"),
        observaciones=(payload.observaciones or "").strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_carga_response(row, movil, user)
