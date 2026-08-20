import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.motivo_no_operativo import MotivoNoOperativo, MotivoNoOperativoUnidadNegocio
from app.models.personal import Personal
from app.models.unidad_negocio import UnidadNegocio
from app.schemas.motivo_no_operativo import (
    MotivoNoOperativoCatalogoItem,
    MotivoNoOperativoCreate,
    MotivoNoOperativoResponse,
    MotivoNoOperativoUpdate,
)

router = APIRouter(tags=["motivos-no-operativos"])


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", normalized).strip("_").lower()
    return normalized[:40] or "motivo"


def _unidad_ids(db: Session, motivo_id: int) -> list[int]:
    return [
        int(value)
        for (value,) in (
            db.query(MotivoNoOperativoUnidadNegocio.unidad_negocio)
            .filter(
                MotivoNoOperativoUnidadNegocio.idMotivo == motivo_id,
                MotivoNoOperativoUnidadNegocio.activo.is_(True),
            )
            .order_by(MotivoNoOperativoUnidadNegocio.unidad_negocio)
            .all()
        )
    ]


def _response(db: Session, row: MotivoNoOperativo) -> MotivoNoOperativoResponse:
    return MotivoNoOperativoResponse(
        id=row.id,
        codigo=row.codigo,
        nombre=row.nombre,
        activo=bool(row.activo),
        unidad_ids=_unidad_ids(db, row.id),
    )


def _sync_unidades(db: Session, motivo_id: int, unidad_ids: list[int]) -> None:
    valid_ids = {
        int(value)
        for (value,) in db.query(UnidadNegocio.idUnidadNegocio).filter(
            UnidadNegocio.idUnidadNegocio.in_(unidad_ids or [-1])
        ).all()
    }
    existing = {
        int(row.unidad_negocio): row
        for row in db.query(MotivoNoOperativoUnidadNegocio).filter(
            MotivoNoOperativoUnidadNegocio.idMotivo == motivo_id
        ).all()
    }
    for unidad_id, row in existing.items():
        row.activo = unidad_id in valid_ids
    for unidad_id in valid_ids:
        if unidad_id not in existing:
            db.add(MotivoNoOperativoUnidadNegocio(idMotivo=motivo_id, unidad_negocio=unidad_id, activo=True))


@router.get("/catalogos/motivos-no-operativos", response_model=list[MotivoNoOperativoCatalogoItem])
def list_catalogo_motivos(
    un_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_user),
):
    query = db.query(MotivoNoOperativo).filter(MotivoNoOperativo.activo.is_(True))
    if un_id is not None:
        query = query.join(
            MotivoNoOperativoUnidadNegocio,
            MotivoNoOperativoUnidadNegocio.idMotivo == MotivoNoOperativo.id,
        ).filter(
            MotivoNoOperativoUnidadNegocio.unidad_negocio == un_id,
            MotivoNoOperativoUnidadNegocio.activo.is_(True),
        )
    return query.order_by(MotivoNoOperativo.nombre).all()


@router.get("/admin/motivos-no-operativos", response_model=list[MotivoNoOperativoResponse])
def admin_list_motivos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=1000),
    buscar: str = "",
    unidad_id: int | None = Query(default=None, ge=1),
    activo: int | None = Query(default=None, ge=0, le=1),
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(MotivoNoOperativo)
    if buscar.strip():
        term = f"%{buscar.strip()}%"
        query = query.filter(or_(MotivoNoOperativo.nombre.ilike(term), MotivoNoOperativo.codigo.ilike(term)))
    if activo in (0, 1):
        query = query.filter(MotivoNoOperativo.activo.is_(bool(activo)))
    if unidad_id:
        query = query.join(
            MotivoNoOperativoUnidadNegocio,
            MotivoNoOperativoUnidadNegocio.idMotivo == MotivoNoOperativo.id,
        ).filter(
            MotivoNoOperativoUnidadNegocio.unidad_negocio == unidad_id,
            MotivoNoOperativoUnidadNegocio.activo.is_(True),
        )
    rows = query.order_by(MotivoNoOperativo.nombre).offset(skip).limit(limit).all()
    return [_response(db, row) for row in rows]


@router.post("/admin/motivos-no-operativos", response_model=MotivoNoOperativoResponse, status_code=status.HTTP_201_CREATED)
def admin_create_motivo(
    payload: MotivoNoOperativoCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    codigo = (payload.codigo or _slug(payload.nombre)).strip().lower()
    if db.query(MotivoNoOperativo).filter(MotivoNoOperativo.codigo == codigo).first():
        raise HTTPException(status_code=409, detail="Ya existe un motivo con ese codigo")
    row = MotivoNoOperativo(codigo=codigo, nombre=payload.nombre.strip().upper(), activo=payload.activo)
    db.add(row)
    db.flush()
    _sync_unidades(db, row.id, payload.unidad_ids)
    db.commit()
    db.refresh(row)
    return _response(db, row)


@router.put("/admin/motivos-no-operativos/{motivo_id}", response_model=MotivoNoOperativoResponse)
def admin_update_motivo(
    motivo_id: int,
    payload: MotivoNoOperativoUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(MotivoNoOperativo).filter(MotivoNoOperativo.id == motivo_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    values = payload.model_dump(exclude_unset=True)
    unidad_ids = values.pop("unidad_ids", None)
    if "nombre" in values and values["nombre"] is not None:
        row.nombre = values["nombre"].strip().upper()
    if "codigo" in values and values["codigo"] is not None:
        codigo = values["codigo"].strip().lower()
        duplicate = db.query(MotivoNoOperativo).filter(
            MotivoNoOperativo.codigo == codigo,
            MotivoNoOperativo.id != motivo_id,
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="Ya existe un motivo con ese codigo")
        row.codigo = codigo
    if "activo" in values and values["activo"] is not None:
        row.activo = bool(values["activo"])
    if unidad_ids is not None:
        _sync_unidades(db, motivo_id, unidad_ids)
    db.commit()
    db.refresh(row)
    return _response(db, row)


@router.delete("/admin/motivos-no-operativos/{motivo_id}")
def admin_disable_motivo(
    motivo_id: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(MotivoNoOperativo).filter(MotivoNoOperativo.id == motivo_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    row.activo = False
    db.commit()
    return {"ok": True, "id": motivo_id}
