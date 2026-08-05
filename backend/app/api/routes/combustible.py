from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.carga_comb import CargaComb
from app.models.lugar_carga import LugarCarga
from app.models.lugar_carga_unidad_negocio import LugarCargaUnidadNegocio
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


def _table_exists(db: Session, table_name: str) -> bool:
    try:
        return inspect(db.get_bind()).has_table(table_name)
    except SQLAlchemyError:
        return False


def _lugar_carga_habilitado(db: Session, lugar_id: int, unidad_id: int) -> bool:
    lugar = (
        db.query(LugarCarga)
        .filter(
            LugarCarga.idLugarCarga == lugar_id,
            LugarCarga.activo == 1,
        )
        .first()
    )
    if not lugar:
        return False

    if _table_exists(db, "lugar_carga_unidad_negocio"):
        vinculo = (
            db.query(LugarCargaUnidadNegocio)
            .filter(
                LugarCargaUnidadNegocio.idLugarCarga == lugar_id,
                LugarCargaUnidadNegocio.unidad_negocio == unidad_id,
                LugarCargaUnidadNegocio.activo.is_(True),
            )
            .first()
        )
        if vinculo:
            return True

    return int(lugar.unidad_negocio or 0) == unidad_id


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
        id_lugar_carga=int(row.idLugarCarga or 0),
        id_tipo_comb=int(row.idTipoComb or 0),
        remito=row.remito or "",
        remito2=row.remito2 or "",
        remito3=row.remito3 or "",
        form_uuid=row.form_uuid or "",
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

    existing = (
        db.query(CargaComb)
        .filter(
            CargaComb.personal == user.idPersonal,
            CargaComb.form_uuid == payload.form_uuid,
        )
        .first()
    )
    if existing:
        existing_movil = (
            db.query(Movil)
            .filter(Movil.idMovil == existing.idMovil)
            .first()
        )
        return _to_carga_response(existing, existing_movil or movil, user)

    # Issue #124 (parte 2): ademas del dedupe por form_uuid (idempotencia del
    # mismo formulario), bloqueamos cargas con la misma clave natural
    # (idMovil, Fecha, Litros, remito, tipo_mov='E') para el mismo operador.
    # Esto cubre el doble submit desde la UI (doble click, doble tab, retry
    # de red) que genera form_uuids distintos pero la misma carga.
    if payload.remito:
        natural_key_dup = (
            db.query(CargaComb)
            .filter(
                CargaComb.personal == user.idPersonal,
                CargaComb.idMovil == payload.id_movil,
                CargaComb.Fecha == payload.fecha,
                CargaComb.Litros == payload.litros,
                CargaComb.remito == payload.remito,
                CargaComb.tipo_mov == "E",
            )
            .first()
        )
        if natural_key_dup:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Ya existe una carga de {payload.litros} L del movil "
                    f"{payload.id_movil} con remito {payload.remito} en "
                    f"{payload.fecha} (id carga {natural_key_dup.idCargaComb}). "
                    f"No se duplica el egreso de stock."
                ),
            )

    if not _lugar_carga_habilitado(db, payload.id_lugar_carga, movil_unidad):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lugar de carga no encontrado o no habilitado para la unidad de negocio",
        )

    now = datetime.now()
    row = CargaComb(
        idMovil=payload.id_movil,
        idTipoComb=payload.id_tipo_comb,
        Fecha=payload.fecha,
        KM=payload.km,
        Litros=payload.litros,
        idLugarCarga=payload.id_lugar_carga,
        UnidadNegocio=movil_unidad,
        personal=user.idPersonal,
        tipo_mov="E",
        tabla="carga_combustible",
        _usuario="web",
        _fecha=now.date(),
        _hora=now.strftime("%H:%M:%S"),
        remito=payload.remito.strip(),
        remito2=payload.remito2.strip(),
        remito3=payload.remito3.strip(),
        form_uuid=payload.form_uuid,
        observaciones=(payload.observaciones or "").strip(),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = (
            db.query(CargaComb)
            .filter(
                CargaComb.personal == user.idPersonal,
                CargaComb.form_uuid == payload.form_uuid,
            )
            .first()
        )
        if existing:
            existing_movil = (
                db.query(Movil)
                .filter(Movil.idMovil == existing.idMovil)
                .first()
            )
            return _to_carga_response(existing, existing_movil or movil, user)
        raise
    db.refresh(row)
    return _to_carga_response(row, movil, user)
