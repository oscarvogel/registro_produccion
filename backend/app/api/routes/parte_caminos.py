from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.api.routes.produccion import _form_submission_lock, _validate_restricted_payload
from app.models.carga_comb import CargaComb
from app.models.personal import Personal
from app.models.produccion import TableroProduccion
from app.models.tipo_proceso import TipoDeProceso
from app.models.unidad_negocio import UnidadNegocio
from app.schemas.parte_caminos import ParteCaminosCreate, ParteCaminosResponse
from app.schemas.produccion import TableroProduccionCreate

router = APIRouter(prefix="/produccion/caminos", tags=["produccion"])


def _response_from_rows(form_uuid: str, rows: list[TableroProduccion]) -> ParteCaminosResponse:
    return ParteCaminosResponse(
        form_uuid=form_uuid,
        registros_creados=len(rows),
        ids=[int(row.id) for row in rows],
        total_km_perfilado=round(sum(float(row.km_perfilado or 0) for row in rows), 2),
        total_hr_disposicion=round(sum(float(row.hr_disposicion or 0) for row in rows), 2),
        total_hr_remolque=round(sum(float(row.hr_remolque or 0) for row in rows), 2),
    )


def _validate_location(tipo: TipoDeProceso, predio: str, acta: str, rodal: str) -> None:
    def missing(value: str) -> bool:
        return not value or not value.strip() or value.strip() == "0"

    if tipo.requiere_predio and missing(predio):
        raise HTTPException(status_code=422, detail=f"{tipo.nombre}: el predio es obligatorio")
    if tipo.requiere_acta and missing(acta):
        raise HTTPException(status_code=422, detail=f"{tipo.nombre}: el acta es obligatoria")
    if tipo.requiere_rodal and missing(rodal):
        raise HTTPException(status_code=422, detail=f"{tipo.nombre}: el rodal es obligatorio")


def _validate_hours_warning(data: ParteCaminosCreate) -> None:
    """Issue #126: keep the cross-hours rule non-blocking in the first cut.

    ``km_perfilado`` is distance, not hours, so only explicit hour metrics can
    be compared with the jornada. The current product decision is to warn in
    the UI rather than reject the request. Backend business invariants that can
    be evaluated unambiguously remain blocking.
    """
    return None


@router.post("", response_model=ParteCaminosResponse, status_code=201)
@router.post("/", response_model=ParteCaminosResponse, status_code=201, include_in_schema=False)
async def create_parte_caminos(
    data: ParteCaminosCreate,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    unidad = (
        db.query(UnidadNegocio)
        .filter(UnidadNegocio.idUnidadNegocio == data.cod_un)
        .first()
    )
    if not unidad or (unidad.Nombre or "").strip().lower() != "caminos":
        raise HTTPException(status_code=422, detail="El parte multi-proceso solo esta habilitado para la UN Caminos")

    _validate_hours_warning(data)

    process_ids = [int(item.tipo_proceso_id) for item in data.procesos]
    tipos = (
        db.query(TipoDeProceso)
        .filter(TipoDeProceso.id.in_(process_ids), TipoDeProceso.activo == 1)
        .all()
    )
    tipos_by_id = {int(tipo.id): tipo for tipo in tipos}
    missing_ids = sorted(set(process_ids) - set(tipos_by_id))
    if missing_ids:
        raise HTTPException(
            status_code=422,
            detail=f"Hay tipos de proceso inexistentes o inactivos: {', '.join(map(str, missing_ids))}",
        )

    # Reuse the same permission + UN/process restriction used by the legacy
    # one-process endpoint. This prevents the multi-process route from becoming
    # a bypass for Full Tree restrictions or unidadnegocio_tipo_proceso.
    for proceso in data.procesos:
        tipo = tipos_by_id[int(proceso.tipo_proceso_id)]
        _validate_location(tipo, proceso.predio, proceso.acta, proceso.rodal)
        validation_payload = TableroProduccionCreate(
            form_uuid=data.form_uuid,
            UN=unidad.Nombre or data.UN,
            operacion=tipo.nombre,
            fecha=data.fecha,
            equipo=data.equipo,
            operador=data.operador,
            cod_operador=data.cod_operador,
            cod_equipo=data.cod_equipo,
            cod_un=data.cod_un,
            hr_inicio=data.hr_inicio,
            hr_fin=data.hr_fin,
            combustible=data.combustible,
            km_combustible=data.km_combustible,
            aceite_cadena=data.aceite_cadena,
            aceite_hidraulico=data.aceite_hidraulico,
            aceite_motor=data.aceite_motor,
            aceite_transmision=data.aceite_transmision,
            aceite_embrague=data.aceite_embrague,
            acta=proceso.acta,
            rodal=proceso.rodal,
            predio=proceso.predio,
            km_perfilado=proceso.km_perfilado,
            hr_disposicion=proceso.hr_disposicion,
            hrs_no_op=data.hrs_no_op,
            motivo_no_op=data.motivo_no_op,
            observaciones=data.observaciones,
            lugar_carga=data.lugar_carga,
            tabla="tipo_de_proceso",
            codigo_tabla=tipo.id,
            id_tipo_comb=data.id_tipo_comb,
            remito=data.remito,
            remito2=data.remito2,
            remito3=data.remito3,
        )
        _validate_restricted_payload(validation_payload, user, db)

    with _form_submission_lock(db, "registro_produccion:create"):
        existing_rows = (
            db.query(TableroProduccion)
            .filter(
                TableroProduccion.form_uuid == data.form_uuid,
                TableroProduccion.cod_operador == data.cod_operador,
            )
            .order_by(TableroProduccion.id)
            .all()
        )
        if existing_rows:
            return _response_from_rows(data.form_uuid, existing_rows)

        if data.combustible > 0 and data.remito:
            existing_carga = (
                db.query(CargaComb)
                .filter(
                    CargaComb.personal == data.cod_operador,
                    CargaComb.idMovil == data.cod_equipo,
                    CargaComb.Fecha == data.fecha,
                    CargaComb.Litros == data.combustible,
                    CargaComb.remito == data.remito,
                    CargaComb.tipo_mov == "E",
                )
                .first()
            )
            if existing_carga:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Ya existe una carga de {data.combustible} L del movil "
                        f"{data.cod_equipo} con remito {data.remito} en {data.fecha}. "
                        "No se duplica el egreso de stock."
                    ),
                )

        max_id = db.query(func.max(TableroProduccion.id)).scalar() or 0
        now = datetime.now()
        rows: list[TableroProduccion] = []

        try:
            for offset, proceso in enumerate(data.procesos, start=1):
                tipo = tipos_by_id[int(proceso.tipo_proceso_id)]
                registro = TableroProduccion(
                    id=int(max_id) + offset,
                    form_uuid=data.form_uuid,
                    UN=unidad.Nombre or data.UN,
                    operacion=tipo.nombre,
                    fecha=data.fecha,
                    equipo=data.equipo,
                    operador=data.operador,
                    cod_operador=data.cod_operador,
                    cod_equipo=data.cod_equipo,
                    cod_un=data.cod_un,
                    hr_inicio=data.hr_inicio,
                    hr_fin=data.hr_fin,
                    combustible=data.combustible,
                    aceite_cadena=data.aceite_cadena,
                    aceite_hidraulico=data.aceite_hidraulico,
                    aceite_motor=data.aceite_motor,
                    aceite_transmision=data.aceite_transmision,
                    aceite_embrague=data.aceite_embrague,
                    acta=proceso.acta,
                    rodal=proceso.rodal,
                    predio=proceso.predio,
                    km_perfilado=proceso.km_perfilado,
                    hr_disposicion=proceso.hr_disposicion,
                    hr_remolque=proceso.hr_remolque,
                    hrs_no_op=data.hrs_no_op,
                    motivo_no_op=data.motivo_no_op,
                    observaciones=data.observaciones,
                    lugar_carga=data.lugar_carga,
                    tabla="tipo_de_proceso",
                    codigo_tabla=tipo.id,
                    tipo_proceso_id=tipo.id,
                    fecha_hora=now,
                    origen="web",
                    remito=data.remito,
                    remito2=data.remito2,
                    remito3=data.remito3,
                )
                db.add(registro)
                rows.append(registro)

            db.flush()

            # Header values are intentionally replicated in the sibling rows
            # for backwards-compatible reporting, but fuel stock must move only
            # once for the whole form_uuid.
            if data.combustible > 0:
                first_id = rows[0].id
                carga = CargaComb(
                    idMovil=data.cod_equipo,
                    idTipoComb=data.id_tipo_comb,
                    Fecha=data.fecha,
                    KM=data.km_combustible,
                    Litros=data.combustible,
                    idLugarCarga=data.lugar_carga,
                    UnidadNegocio=data.cod_un,
                    personal=data.cod_operador,
                    idtabla=str(first_id),
                    tabla="tablero_produccion",
                    tipo_mov="E",
                    _usuario="web",
                    _fecha=now.date(),
                    _hora=now.strftime("%H:%M:%S"),
                    remito=data.remito.strip(),
                    remito2=data.remito2.strip(),
                    remito3=data.remito3.strip(),
                    form_uuid=data.form_uuid,
                )
                db.add(carga)

            db.commit()
            for row in rows:
                db.refresh(row)
            return _response_from_rows(data.form_uuid, rows)
        except Exception:
            db.rollback()
            raise
