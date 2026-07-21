from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, inspect, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db
from app.core.security import get_password_hash
from app.models.asignacion_operativa import AsignacionOperativa
from app.models.lugar_carga import LugarCarga
from app.models.movil import Movil
from app.models.personal import Personal
from app.models.personal_unidad_negocio import PersonalUnidadNegocio
from app.models.produccion import TableroProduccion
from app.models.tipo_proceso import TipoDeProceso, UnidadNegocioTipoProceso
from app.models.tipo_movil import TipoMovil
from app.models.ubicacion import Acta, Predio, Rodal
from app.models.unidad_negocio import UnidadNegocio
from app.schemas.admin import (
    ActaAdminResponse,
    ActaCreate,
    ActaUpdate,
    AdminDashboardEvolutionItem,
    AdminDashboardOverviewResponse,
    AdminDashboardRankingItem,
    AdminDashboardTotals,
    AdminDashboardVariationItem,
    AdminRecentRecordItem,
    AsignacionOperativaCreate,
    AsignacionOperativaResponse,
    AsignacionOperativaUpdate,
    ConfiguracionAccesoUpdate,
    ConfiguracionUsuarioResponse,
    DashboardResumenItem,
    DashboardTipoProcesoItem,
    DashboardUnidadNegocioItem,
    DeleteResponse,
    LugarCargaCreate,
    LugarCargaResponse,
    LugarCargaUpdate,
    MovilCreate,
    MovilResponse,
    MovilUpdate,
    PersonalCreate,
    PersonalResponse,
    PersonalUpdate,
    PredioCreate,
    PredioResponse,
    PredioUpdate,
    RodalCreate,
    RodalResponse,
    RodalUpdate,
    TipoProcesoCreate,
    TipoProcesoResponse,
    TipoProcesoUpdate,
    TipoMovilResponse,
    UnidadNegocioCreate,
    UnidadNegocioResponse,
    UnidadNegocioUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin"])


def _hash_personal_password(password: str) -> str:
    try:
        return get_password_hash(password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _dashboard_unit_sort_key(item: DashboardUnidadNegocioItem) -> tuple[bool, int, str]:
    last_activity = item.resumen.ultima_actividad_fecha
    return (
        last_activity is None,
        -last_activity.toordinal() if last_activity else 0,
        (item.prefijo or item.nombre or "").lower(),
    )


def _table_exists(db: Session, table_name: str) -> bool:
    try:
        return inspect(db.get_bind()).has_table(table_name)
    except SQLAlchemyError:
        return False


def _normalize_ids(values: list[int] | None, fallback: int | None = None) -> list[int]:
    ids: list[int] = []
    for value in values or []:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            continue
        if parsed > 0 and parsed not in ids:
            ids.append(parsed)
    if not ids and fallback:
        ids.append(int(fallback))
    return ids


def _personal_unidad_ids(db: Session, row: Personal) -> list[int]:
    if not _table_exists(db, "personal_unidad_negocio"):
        return _normalize_ids([], row.unidad_negocio)

    ids = [
        int(value)
        for (value,) in (
            db.query(PersonalUnidadNegocio.idUnidadNegocio)
            .filter(PersonalUnidadNegocio.idPersonal == row.idPersonal)
            .order_by(PersonalUnidadNegocio.idUnidadNegocio)
            .all()
        )
    ]
    return _normalize_ids(ids, row.unidad_negocio)


def _personal_unidad_ids_map(db: Session, rows: list[Personal]) -> dict[int, list[int]]:
    rows_by_id = {
        int(row.idPersonal): row
        for row in rows
        if row.idPersonal is not None
    }
    fallback = {
        person_id: _normalize_ids([], row.unidad_negocio)
        for person_id, row in rows_by_id.items()
    }
    if not rows_by_id or not _table_exists(db, "personal_unidad_negocio"):
        return fallback

    relation_rows = (
        db.query(PersonalUnidadNegocio.idPersonal, PersonalUnidadNegocio.idUnidadNegocio)
        .filter(PersonalUnidadNegocio.idPersonal.in_(rows_by_id.keys()))
        .order_by(PersonalUnidadNegocio.idPersonal, PersonalUnidadNegocio.idUnidadNegocio)
        .all()
    )
    grouped: dict[int, list[int]] = {person_id: [] for person_id in rows_by_id}
    for person_id, unidad_id in relation_rows:
        try:
            grouped[int(person_id)].append(int(unidad_id))
        except (TypeError, ValueError):
            continue

    return {
        person_id: _normalize_ids(grouped.get(person_id), rows_by_id[person_id].unidad_negocio)
        for person_id in rows_by_id
    }


def _tipo_proceso_unidad_ids(db: Session, row: TipoDeProceso) -> list[int]:
    if not _table_exists(db, "unidadnegocio_tipo_proceso"):
        return []

    return [
        int(value)
        for (value,) in (
            db.query(UnidadNegocioTipoProceso.un_id)
            .filter(UnidadNegocioTipoProceso.tipo_proceso_id == row.id)
            .order_by(UnidadNegocioTipoProceso.un_id)
            .all()
        )
    ]


def _sync_personal_unidades(db: Session, row: Personal, unidad_ids: list[int] | None) -> None:
    ids = _normalize_ids(unidad_ids, row.unidad_negocio)
    if ids:
        row.unidad_negocio = ids[0]

    if not _table_exists(db, "personal_unidad_negocio"):
        return

    db.query(PersonalUnidadNegocio).filter(PersonalUnidadNegocio.idPersonal == row.idPersonal).delete()
    for unidad_id in ids:
        db.add(PersonalUnidadNegocio(idPersonal=row.idPersonal, idUnidadNegocio=unidad_id))


def _sync_tipo_proceso_unidades(db: Session, row: TipoDeProceso, unidad_ids: list[int] | None) -> None:
    if unidad_ids is None or not _table_exists(db, "unidadnegocio_tipo_proceso"):
        return

    ids = _normalize_ids(unidad_ids)
    db.query(UnidadNegocioTipoProceso).filter(UnidadNegocioTipoProceso.tipo_proceso_id == row.id).delete()
    for unidad_id in ids:
        db.add(UnidadNegocioTipoProceso(un_id=unidad_id, tipo_proceso_id=row.id))


def _ensure_asignacion_consistente(db: Session, id_movil: int, id_chofer: int, id_proceso: int) -> None:
    movil = db.query(Movil).filter(Movil.idMovil == id_movil).first()
    if not movil:
        raise HTTPException(status_code=400, detail="Movil no encontrado")

    chofer = db.query(Personal).filter(Personal.idPersonal == id_chofer).first()
    if not chofer:
        raise HTTPException(status_code=400, detail="Chofer no encontrado")

    proceso = db.query(TipoDeProceso).filter(TipoDeProceso.id == id_proceso).first()
    if not proceso:
        raise HTTPException(status_code=400, detail="Tipo de proceso no encontrado")

    unidad_id = int(movil.idUnidadNegocio or 0)
    if unidad_id <= 0:
        raise HTTPException(status_code=400, detail="El movil debe tener unidad de negocio")

    if unidad_id not in _personal_unidad_ids(db, chofer):
        raise HTTPException(status_code=400, detail="El chofer no pertenece a la unidad del movil")

    if _table_exists(db, "unidadnegocio_tipo_proceso"):
        exists = (
            db.query(UnidadNegocioTipoProceso)
            .filter(
                UnidadNegocioTipoProceso.un_id == unidad_id,
                UnidadNegocioTipoProceso.tipo_proceso_id == id_proceso,
            )
            .first()
        )
        if not exists:
            raise HTTPException(status_code=400, detail="El tipo de proceso no esta habilitado para la unidad del movil")


def _to_personal_response(db: Session, row: Personal) -> PersonalResponse:
    unit_ids_by_person = _personal_unidad_ids_map(db, [row])
    return _to_personal_response_with_units(row, unit_ids_by_person.get(int(row.idPersonal), []))


def _to_personal_response_with_units(row: Personal, unidad_ids: list[int]) -> PersonalResponse:
    return PersonalResponse(
        idPersonal=row.idPersonal,
        nombre=row.Nombre or "",
        dni=row.dni,
        cuit=row.CUIT or "",
        id_puesto=int(row.idPuesto or 1),
        unidad_negocio=int(row.unidad_negocio or 1),
        unidad_ids=unidad_ids,
        tipo_de_proceso_id=row.tipo_de_proceso_id,
        entrada_m=row.EntradaM or "00:00",
        salida_m=row.SalidaM or "00:00",
        entrada_t=row.EntradaT or "00:00",
        salida_t=row.SalidaT or "00:00",
        fecha_nacimiento=row.fecha_nacimiento,
        fecha_ingreso=row.fecha_ingreso,
        telefono=row.telefono or "",
        domicilio=row.domicilio or "",
        activo=int(row.activo or 0),
        encargado=int(row.encargado or 0),
        is_admin=int(row.is_admin or 0),
    )


def _to_movil_response(row: Movil) -> MovilResponse:
    return MovilResponse(
        idMovil=row.idMovil,
        patente=row.Patente or "",
        detalle=row.Detalle or "",
        tipo_proceso=row.tipo_proceso or "1",
        id_unidad_negocio=int(row.idUnidadNegocio or 1),
        cant_neumaticos=int(row.CantNeumaticos or 0),
        capacidad_tanque=int(row.capacidad_tanque or 0),
        consumo_promedio=float(row.consumo_promedio or 0),
        tipo_movil=int(row.tipo_movil or 1),
        anio_fabricacion=int(row.anio_fabricacion or 0),
        nro_chasis=row.nro_chasis or "",
        nro_motor=row.nro_motor or "",
        venc_tecnica=row.VencTecnica,
        ruta=bool(row.Ruta),
        venc_ruta=row.VencRuta,
        activo=int(row.activo or 0),
        observaciones=row.observaciones,
    )


def _to_unidad_response(row: UnidadNegocio) -> UnidadNegocioResponse:
    return UnidadNegocioResponse(
        idUnidadNegocio=row.idUnidadNegocio,
        nombre=row.Nombre or "",
        prefijo=row.Prefijo or "",
        codigo_kobo=row.codigo_kobo or "",
        activo=int(row.activo or 0),
    )


def _to_tipo_proceso_response(db: Session, row: TipoDeProceso) -> TipoProcesoResponse:
    return TipoProcesoResponse(
        id=row.id,
        nombre=row.nombre or "",
        campos=row.campos or "",
        unidad_ids=_tipo_proceso_unidad_ids(db, row),
        requiere_acta=bool(getattr(row, "requiere_acta", False)),
        requiere_predio=bool(getattr(row, "requiere_predio", False)),
        requiere_rodal=bool(getattr(row, "requiere_rodal", False)),
        activo=int(row.activo or 0),
    )


def _to_tipo_movil_response(row: TipoMovil) -> TipoMovilResponse:
    return TipoMovilResponse(
        id=row.id,
        detalle=row.detalle or "",
        activo=int(row.activo or 0),
    )


def _to_lugar_carga_response(row: LugarCarga) -> LugarCargaResponse:
    return LugarCargaResponse(
        idLugarCarga=row.idLugarCarga,
        detalle=row.Detalle or "",
        unidad_negocio=int(row.unidad_negocio or 1),
        activo=int(row.activo or 0),
    )


def _to_predio_response(row: Predio) -> PredioResponse:
    return PredioResponse(
        idPredio=row.idPredio,
        nombre=row.Nombre or "",
        empresa=row.empresa or "",
        codigo_kobo=row.codigo_kobo,
    )


def _to_rodal_response(row: Rodal) -> RodalResponse:
    return RodalResponse(
        idRodal=row.idRodal,
        rodal=row.Rodal or "",
        idPredio=int(row.idPredio or 0),
        vam=float(row.VAM or 0),
        tarifa=float(row.Tarifa or 0),
        extraccion=float(row.Extraccion or 0),
        carga=float(row.Carga or 0),
    )


def _to_acta_admin_response(row: Acta) -> ActaAdminResponse:
    return ActaAdminResponse(
        id=row.id,
        numero=row.numero or "",
        rodal_id=int(row.rodal_id or 0),
        vam=float(row.vam or 0),
        tarifa=float(row.tarifa or 0),
        extraccion=float(row.extraccion or 0),
        carga=float(row.carga or 0),
        periodo=row.periodo,
    )


def _to_asignacion_response(row: AsignacionOperativa) -> AsignacionOperativaResponse:
    return AsignacionOperativaResponse(
        idAsignacion=row.idAsignacion,
        idMovil=int(row.idMovil),
        idChofer=int(row.idChofer),
        idProceso=int(row.idProceso),
    )


def _to_config_user_response(row: Personal) -> ConfiguracionUsuarioResponse:
    return ConfiguracionUsuarioResponse(
        idPersonal=row.idPersonal,
        nombre=row.Nombre or "",
        dni=row.dni,
        activo=int(row.activo or 0),
        encargado=int(row.encargado or 0),
        is_admin=int(row.is_admin or 0),
    )


def _normalize_binary(value: int) -> int:
    return 1 if int(value) == 1 else 0


def _parse_range(fecha_desde: date | None, fecha_hasta: date | None) -> tuple[date, date]:
    today = date.today()
    end = fecha_hasta or today
    start = fecha_desde or (end - timedelta(days=29))
    if start > end:
        raise HTTPException(status_code=400, detail="fecha_desde no puede ser mayor que fecha_hasta")
    return start, end


def _production_base(db: Session, start: date, end: date):
    return db.query(TableroProduccion).filter(
        TableroProduccion.cod_un.isnot(None),
        TableroProduccion.fecha >= start,
        TableroProduccion.fecha <= end,
    )


def _overview_totals(db: Session, start: date, end: date) -> AdminDashboardTotals:
    base = _production_base(db, start, end)
    row = base.with_entities(
        func.count(TableroProduccion.id).label("total_registros"),
        func.coalesce(func.sum(TableroProduccion.produccion), 0).label("produccion_total"),
        func.coalesce(func.sum(TableroProduccion.tn_despachadas), 0).label("tn_despachadas_total"),
        func.coalesce(func.sum(TableroProduccion.combustible), 0).label("combustible_total"),
        func.count(func.distinct(TableroProduccion.cod_un)).label("unidades_activas"),
        func.count(func.distinct(TableroProduccion.cod_operador)).label("operadores_activos"),
        func.count(func.distinct(TableroProduccion.cod_equipo)).label("equipos_activos"),
    ).one()

    return AdminDashboardTotals(
        total_registros=int(row.total_registros or 0),
        produccion_total=round(float(row.produccion_total or 0), 2),
        tn_despachadas_total=round(float(row.tn_despachadas_total or 0), 2),
        combustible_total=int(row.combustible_total or 0),
        unidades_activas=int(row.unidades_activas or 0),
        operadores_activos=int(row.operadores_activos or 0),
        equipos_activos=int(row.equipos_activos or 0),
    )


def _variation_percent(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 2)


def _overview_variations(current: AdminDashboardTotals, previous: AdminDashboardTotals) -> list[AdminDashboardVariationItem]:
    metrics = [
        ("produccion_total", "Produccion", current.produccion_total, previous.produccion_total),
        ("tn_despachadas_total", "TN despachadas", current.tn_despachadas_total, previous.tn_despachadas_total),
        ("total_registros", "Registros", float(current.total_registros), float(previous.total_registros)),
        ("combustible_total", "Combustible", float(current.combustible_total), float(previous.combustible_total)),
    ]
    return [
        AdminDashboardVariationItem(
            key=key,
            label=label,
            current=current_value,
            previous=previous_value,
            variation_percent=_variation_percent(current_value, previous_value),
        )
        for key, label, current_value, previous_value in metrics
    ]


def _share(value: float, total: float) -> float:
    if total <= 0:
        return 0.0
    return round((value / total) * 100, 2)


@router.get("/dashboard/overview", response_model=AdminDashboardOverviewResponse)
async def get_admin_dashboard_overview(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    start, end = _parse_range(fecha_desde, fecha_hasta)
    period_delta = end - start
    previous_end = start - timedelta(days=1)
    previous_start = previous_end - period_delta

    totals = _overview_totals(db, start, end)
    previous_totals = _overview_totals(db, previous_start, previous_end)

    unidad_rows = (
        _production_base(db, start, end)
        .join(UnidadNegocio, UnidadNegocio.idUnidadNegocio == TableroProduccion.cod_un)
        .with_entities(
            UnidadNegocio.idUnidadNegocio.label("id"),
            UnidadNegocio.Nombre.label("nombre"),
            func.count(TableroProduccion.id).label("registros"),
            func.coalesce(func.sum(TableroProduccion.produccion), 0).label("produccion"),
            func.coalesce(func.sum(TableroProduccion.tn_despachadas), 0).label("tn_despachadas"),
            func.coalesce(func.sum(TableroProduccion.combustible), 0).label("combustible"),
        )
        .group_by(UnidadNegocio.idUnidadNegocio, UnidadNegocio.Nombre)
        .order_by(func.coalesce(func.sum(TableroProduccion.produccion), 0).desc())
        .limit(8)
        .all()
    )
    unidad_ranking = [
        AdminDashboardRankingItem(
            id=row.id,
            nombre=row.nombre or "Sin unidad",
            registros=int(row.registros or 0),
            produccion=round(float(row.produccion or 0), 2),
            tn_despachadas=round(float(row.tn_despachadas or 0), 2),
            combustible=int(row.combustible or 0),
            share_percent=_share(float(row.produccion or 0), totals.produccion_total),
        )
        for row in unidad_rows
    ]

    proceso_rows = (
        _production_base(db, start, end)
        .join(TipoDeProceso, TipoDeProceso.id == TableroProduccion.codigo_tabla)
        .with_entities(
            TipoDeProceso.id.label("id"),
            TipoDeProceso.nombre.label("nombre"),
            func.count(TableroProduccion.id).label("registros"),
            func.coalesce(func.sum(TableroProduccion.produccion), 0).label("produccion"),
            func.coalesce(func.sum(TableroProduccion.tn_despachadas), 0).label("tn_despachadas"),
            func.coalesce(func.sum(TableroProduccion.combustible), 0).label("combustible"),
        )
        .group_by(TipoDeProceso.id, TipoDeProceso.nombre)
        .order_by(func.coalesce(func.sum(TableroProduccion.produccion), 0).desc())
        .limit(8)
        .all()
    )
    proceso_ranking = [
        AdminDashboardRankingItem(
            id=row.id,
            nombre=row.nombre or "Sin proceso",
            registros=int(row.registros or 0),
            produccion=round(float(row.produccion or 0), 2),
            tn_despachadas=round(float(row.tn_despachadas or 0), 2),
            combustible=int(row.combustible or 0),
            share_percent=_share(float(row.produccion or 0), totals.produccion_total),
        )
        for row in proceso_rows
    ]

    evolution_rows = (
        _production_base(db, start, end)
        .with_entities(
            TableroProduccion.fecha.label("fecha"),
            func.coalesce(func.sum(TableroProduccion.produccion), 0).label("produccion"),
            func.count(TableroProduccion.id).label("registros"),
        )
        .group_by(TableroProduccion.fecha)
        .order_by(TableroProduccion.fecha)
        .all()
    )
    evolucion = [
        AdminDashboardEvolutionItem(
            fecha=row.fecha,
            produccion=round(float(row.produccion or 0), 2),
            registros=int(row.registros or 0),
        )
        for row in evolution_rows
    ]

    recent_rows = (
        _production_base(db, start, end)
        .order_by(TableroProduccion.fecha.desc(), TableroProduccion.id.desc())
        .limit(8)
        .all()
    )
    recent_records = [
        AdminRecentRecordItem(
            id=row.id,
            fecha=row.fecha,
            unidad=row.UN or "",
            operacion=row.operacion or "",
            operador=row.operador or "",
            equipo=row.equipo or "",
            produccion=float(row.produccion or 0),
            combustible=int(row.combustible or 0),
        )
        for row in recent_rows
    ]

    return AdminDashboardOverviewResponse(
        fecha_desde=start,
        fecha_hasta=end,
        periodo_anterior_desde=previous_start,
        periodo_anterior_hasta=previous_end,
        totals=totals,
        previous_totals=previous_totals,
        variations=_overview_variations(totals, previous_totals),
        unidad_ranking=unidad_ranking,
        proceso_ranking=proceso_ranking,
        evolucion=evolucion,
        recent_records=recent_records,
    )


@router.get("/dashboard", response_model=list[DashboardUnidadNegocioItem])
async def get_admin_dashboard(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    start, end = _parse_range(fecha_desde, fecha_hasta)
    today = date.today()

    unidades = (
        db.query(UnidadNegocio)
        .filter(UnidadNegocio.activo == 1)
        .order_by(UnidadNegocio.Nombre)
        .all()
    )
    if not unidades:
        unidades = db.query(UnidadNegocio).order_by(UnidadNegocio.Nombre).all()

    unidad_ids = [un.idUnidadNegocio for un in unidades]
    totals_by_un = {
        row.cod_un: row
        for row in (
            db.query(
                TableroProduccion.cod_un.label("cod_un"),
                func.count(TableroProduccion.id).label("total_registros"),
                func.coalesce(func.sum(TableroProduccion.produccion), 0).label("produccion_total"),
                func.coalesce(func.sum(TableroProduccion.tn_despachadas), 0).label("tn_despachadas_total"),
                func.coalesce(func.sum(TableroProduccion.combustible), 0).label("combustible_total"),
                func.count(func.distinct(TableroProduccion.cod_operador)).label("operadores_activos"),
                func.count(func.distinct(TableroProduccion.cod_equipo)).label("equipos_activos"),
            )
            .filter(
                TableroProduccion.cod_un.in_(unidad_ids),
                TableroProduccion.fecha >= start,
                TableroProduccion.fecha <= end,
            )
            .group_by(TableroProduccion.cod_un)
            .all()
        )
    }

    today_counts_by_un = {
        cod_un: int(total or 0)
        for cod_un, total in (
            db.query(
                TableroProduccion.cod_un,
                func.count(TableroProduccion.id),
            )
            .filter(
                TableroProduccion.cod_un.in_(unidad_ids),
                TableroProduccion.fecha == today,
            )
            .group_by(TableroProduccion.cod_un)
            .all()
        )
    }

    # Fetch last activity date and summary for each unit, independent of the selected period.
    last_activity_by_un = {}
    if unidad_ids:
        for unidad_id in unidad_ids:
            record = (
                db.query(TableroProduccion)
                .filter(TableroProduccion.cod_un == unidad_id)
                .order_by(TableroProduccion.fecha.desc(), TableroProduccion.id.desc())
                .first()
            )
            if not record:
                continue

            partes = []
            if record.produccion and float(record.produccion) > 0:
                partes.append(f"{record.produccion:.1f} {record.unidad_produccion or 'uds'}")
            if record.tn_despachadas and float(record.tn_despachadas) > 0:
                partes.append(f"{record.tn_despachadas:.1f} TN")
            if record.m3 and int(record.m3) > 0:
                partes.append(f"{record.m3} m3")
            if record.has and float(record.has) > 0:
                partes.append(f"{record.has:.1f} HAS")
            if record.carros and int(record.carros) > 0:
                partes.append(f"{record.carros} carros")
            if record.combustible and int(record.combustible) > 0:
                partes.append(f"{record.combustible} L comb.")

            last_activity_by_un[unidad_id] = {
                "fecha": record.fecha,
                "resumen": ", ".join(partes) if partes else f"{record.operacion or 'Actividad'}",
            }

    tipos_by_un: dict[int, list[TipoDeProceso]] = {un_id: [] for un_id in unidad_ids}
    for un_id, tipo in (
        db.query(UnidadNegocioTipoProceso.un_id, TipoDeProceso)
        .join(TipoDeProceso, UnidadNegocioTipoProceso.tipo_proceso_id == TipoDeProceso.id)
        .filter(UnidadNegocioTipoProceso.un_id.in_(unidad_ids))
        .order_by(UnidadNegocioTipoProceso.un_id, TipoDeProceso.nombre)
        .all()
    ):
        tipos_by_un.setdefault(un_id, []).append(tipo)

    type_totals_by_un_tipo = {
        (row.cod_un, row.codigo_tabla): row
        for row in (
            db.query(
                TableroProduccion.cod_un.label("cod_un"),
                TableroProduccion.codigo_tabla.label("codigo_tabla"),
                func.count(TableroProduccion.id).label("registros"),
                func.coalesce(func.sum(TableroProduccion.produccion), 0).label("produccion"),
            )
            .filter(
                TableroProduccion.cod_un.in_(unidad_ids),
                TableroProduccion.fecha >= start,
                TableroProduccion.fecha <= end,
            )
            .group_by(TableroProduccion.cod_un, TableroProduccion.codigo_tabla)
            .all()
        )
    }

    result: list[DashboardUnidadNegocioItem] = []

    for un in unidades:
        totals = totals_by_un.get(un.idUnidadNegocio)
        tipos_proceso: list[DashboardTipoProcesoItem] = []
        for tipo in tipos_by_un.get(un.idUnidadNegocio, []):
            type_totals = type_totals_by_un_tipo.get((un.idUnidadNegocio, tipo.id))
            tipos_proceso.append(
                DashboardTipoProcesoItem(
                    id=tipo.id,
                    nombre=tipo.nombre or "",
                    registros=int(type_totals.registros or 0) if type_totals else 0,
                    produccion=round(float(type_totals.produccion or 0), 2) if type_totals else 0,
                )
            )

        last_activity = last_activity_by_un.get(un.idUnidadNegocio)
        
        result.append(
            DashboardUnidadNegocioItem(
                id=un.idUnidadNegocio,
                nombre=un.Nombre or "",
                prefijo=un.Prefijo or "",
                resumen=DashboardResumenItem(
                    total_registros=int(totals.total_registros or 0) if totals else 0,
                    produccion_total=round(float(totals.produccion_total or 0), 2) if totals else 0,
                    tn_despachadas_total=round(float(totals.tn_despachadas_total or 0), 2) if totals else 0,
                    combustible_total=int(totals.combustible_total or 0) if totals else 0,
                    operadores_activos=int(totals.operadores_activos or 0) if totals else 0,
                    equipos_activos=int(totals.equipos_activos or 0) if totals else 0,
                    registros_hoy=today_counts_by_un.get(un.idUnidadNegocio, 0),
                    ultima_actividad_fecha=last_activity["fecha"] if last_activity else None,
                    ultima_actividad_resumen=last_activity["resumen"] if last_activity else None,
                ),
                tipos_proceso=tipos_proceso,
            )
        )

    # Sort by last activity date (most recent first), units with no activity go to the end
    result.sort(key=_dashboard_unit_sort_key)

    return result


@router.get("/dashboard/recent-records", response_model=list[AdminRecentRecordItem])
async def get_admin_recent_records(
    fecha: date | None = None,
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(TableroProduccion)
    if fecha:
        query = query.filter(TableroProduccion.fecha == fecha)
    rows = query.order_by(TableroProduccion.fecha.desc(), TableroProduccion.id.desc()).limit(limit).all()

    return [
        AdminRecentRecordItem(
            id=row.id,
            fecha=row.fecha,
            unidad=row.UN or "",
            operacion=row.operacion or "",
            operador=row.operador or "",
            equipo=row.equipo or "",
            produccion=float(row.produccion or 0),
            combustible=int(row.combustible or 0),
        )
        for row in rows
    ]


@router.get("/configuracion/usuarios", response_model=list[ConfiguracionUsuarioResponse])
async def list_usuarios_configuracion(
    buscar: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(Personal)
    if buscar:
        text = f"%{buscar.strip()}%"
        query = query.filter(or_(Personal.Nombre.like(text), Personal.dni.like(text)))

    rows = query.order_by(Personal.Nombre).all()
    return [_to_config_user_response(r) for r in rows]


@router.patch("/configuracion/usuarios/{idPersonal}/acceso", response_model=ConfiguracionUsuarioResponse)
async def update_usuario_acceso(
    idPersonal: int,
    payload: ConfiguracionAccesoUpdate,
    db: Session = Depends(get_db),
    current_admin: Personal = Depends(get_current_admin),
):
    if payload.is_admin not in (0, 1):
        raise HTTPException(status_code=400, detail="is_admin debe ser 0 o 1")

    if current_admin.idPersonal == idPersonal and payload.is_admin == 0:
        raise HTTPException(status_code=400, detail="No puede quitarse el acceso a si mismo")

    user = db.query(Personal).filter(Personal.idPersonal == idPersonal).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.is_admin = payload.is_admin
    db.commit()
    db.refresh(user)
    return _to_config_user_response(user)


@router.get("/personal", response_model=list[PersonalResponse])
async def list_personal(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    unidad_id: int | None = None,
    activo: int | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(Personal)
    if buscar:
        pattern = f"%{buscar.strip()}%"
        query = query.filter(or_(Personal.Nombre.ilike(pattern), Personal.dni.ilike(pattern)))
    if activo in (0, 1):
        query = query.filter(Personal.activo == activo)
    if unidad_id:
        if _table_exists(db, "personal_unidad_negocio"):
            query = (
                query.outerjoin(
                    PersonalUnidadNegocio,
                    PersonalUnidadNegocio.idPersonal == Personal.idPersonal,
                )
                .filter(
                    or_(
                        Personal.unidad_negocio == unidad_id,
                        PersonalUnidadNegocio.idUnidadNegocio == unidad_id,
                    )
                )
                .distinct()
            )
        else:
            query = query.filter(Personal.unidad_negocio == unidad_id)
    rows = query.order_by(Personal.Nombre).offset(skip).limit(limit).all()
    unit_ids_by_person = _personal_unidad_ids_map(db, rows)
    return [
        _to_personal_response_with_units(r, unit_ids_by_person.get(int(r.idPersonal), []))
        for r in rows
    ]


@router.post("/personal", response_model=PersonalResponse, status_code=status.HTTP_201_CREATED)
async def create_personal(
    payload: PersonalCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    nombre = payload.nombre.strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="Nombre es obligatorio")

    row = Personal(
        Nombre=nombre,
        dni=payload.dni,
        CUIT=payload.cuit,
        idPuesto=payload.id_puesto,
        unidad_negocio=payload.unidad_negocio,
        tipo_de_proceso_id=payload.tipo_de_proceso_id,
        EntradaM=payload.entrada_m,
        SalidaM=payload.salida_m,
        EntradaT=payload.entrada_t,
        SalidaT=payload.salida_t,
        fecha_nacimiento=payload.fecha_nacimiento,
        fecha_ingreso=payload.fecha_ingreso,
        telefono=payload.telefono,
        domicilio=payload.domicilio,
        activo=_normalize_binary(payload.activo),
        encargado=_normalize_binary(payload.encargado),
        is_admin=_normalize_binary(payload.is_admin),
        porcentaje=0.0,
        concepto_sueldo=1,
    )

    if payload.password:
        row.password = _hash_personal_password(payload.password)

    db.add(row)
    db.commit()
    db.refresh(row)
    _sync_personal_unidades(db, row, payload.unidad_ids or [payload.unidad_negocio])
    db.commit()
    db.refresh(row)
    return _to_personal_response(db, row)


@router.put("/personal/{idPersonal}", response_model=PersonalResponse)
async def update_personal(
    idPersonal: int,
    payload: PersonalUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Personal).filter(Personal.idPersonal == idPersonal).first()
    if not row:
        raise HTTPException(status_code=404, detail="Personal no encontrado")

    data = payload.model_dump(exclude_unset=True)
    unidad_ids = data.pop("unidad_ids", None)

    if "nombre" in data:
        nombre = (data.pop("nombre") or "").strip()
        if not nombre:
            raise HTTPException(status_code=400, detail="Nombre es obligatorio")
        row.Nombre = nombre

    mapping = {
        "dni": "dni",
        "cuit": "CUIT",
        "id_puesto": "idPuesto",
        "unidad_negocio": "unidad_negocio",
        "tipo_de_proceso_id": "tipo_de_proceso_id",
        "entrada_m": "EntradaM",
        "salida_m": "SalidaM",
        "entrada_t": "EntradaT",
        "salida_t": "SalidaT",
        "fecha_nacimiento": "fecha_nacimiento",
        "fecha_ingreso": "fecha_ingreso",
        "telefono": "telefono",
        "domicilio": "domicilio",
    }

    for source, target in mapping.items():
        if source in data:
            value = data.pop(source)
            setattr(row, target, value)
            if source == "unidad_negocio" and unidad_ids is None:
                unidad_ids = [value]

    if "activo" in data:
        row.activo = _normalize_binary(data.pop("activo"))
    if "encargado" in data:
        row.encargado = _normalize_binary(data.pop("encargado"))
    if "is_admin" in data:
        row.is_admin = _normalize_binary(data.pop("is_admin"))

    if "password" in data:
        password = data.pop("password")
        if password:
            row.password = _hash_personal_password(password)

    if unidad_ids is not None:
        _sync_personal_unidades(db, row, unidad_ids)

    db.commit()
    db.refresh(row)
    return _to_personal_response(db, row)


@router.delete("/personal/{idPersonal}", response_model=DeleteResponse)
async def delete_personal(
    idPersonal: int,
    db: Session = Depends(get_db),
    current_admin: Personal = Depends(get_current_admin),
):
    row = db.query(Personal).filter(Personal.idPersonal == idPersonal).first()
    if not row:
        raise HTTPException(status_code=404, detail="Personal no encontrado")

    if current_admin.idPersonal == idPersonal:
        raise HTTPException(status_code=400, detail="No puede desactivar su propio usuario")

    row.activo = 0
    row.is_admin = 0
    db.commit()
    return DeleteResponse()


@router.get("/moviles", response_model=list[MovilResponse])
async def list_moviles(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    unidad_id: int | None = None,
    activo: int | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(Movil)
    if buscar:
        pattern = f"%{buscar.strip()}%"
        query = query.filter(or_(Movil.Detalle.ilike(pattern), Movil.Patente.ilike(pattern)))
    if unidad_id:
        query = query.filter(Movil.idUnidadNegocio == unidad_id)
    if activo in (0, 1):
        query = query.filter(Movil.activo == activo)
    rows = query.order_by(Movil.Detalle).offset(skip).limit(limit).all()
    return [_to_movil_response(r) for r in rows]


@router.post("/moviles", response_model=MovilResponse, status_code=status.HTTP_201_CREATED)
async def create_movil(
    payload: MovilCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    if not payload.patente.strip() or not payload.detalle.strip():
        raise HTTPException(status_code=400, detail="Patente y detalle son obligatorios")

    row = Movil(
        Patente=payload.patente.strip(),
        Detalle=payload.detalle.strip(),
        tipo_proceso=payload.tipo_proceso,
        idUnidadNegocio=payload.id_unidad_negocio,
        CantNeumaticos=payload.cant_neumaticos,
        capacidad_tanque=payload.capacidad_tanque,
        consumo_promedio=payload.consumo_promedio,
        tipo_movil=payload.tipo_movil,
        anio_fabricacion=payload.anio_fabricacion,
        nro_chasis=payload.nro_chasis,
        nro_motor=payload.nro_motor,
        VencTecnica=payload.venc_tecnica,
        Ruta=payload.ruta,
        VencRuta=payload.venc_ruta,
        activo=_normalize_binary(payload.activo),
        observaciones=payload.observaciones,
    )

    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_movil_response(row)


@router.put("/moviles/{idMovil}", response_model=MovilResponse)
async def update_movil(
    idMovil: int,
    payload: MovilUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Movil).filter(Movil.idMovil == idMovil).first()
    if not row:
        raise HTTPException(status_code=404, detail="Movil no encontrado")

    data = payload.model_dump(exclude_unset=True)

    mapping = {
        "patente": "Patente",
        "detalle": "Detalle",
        "tipo_proceso": "tipo_proceso",
        "id_unidad_negocio": "idUnidadNegocio",
        "cant_neumaticos": "CantNeumaticos",
        "capacidad_tanque": "capacidad_tanque",
        "consumo_promedio": "consumo_promedio",
        "tipo_movil": "tipo_movil",
        "anio_fabricacion": "anio_fabricacion",
        "nro_chasis": "nro_chasis",
        "nro_motor": "nro_motor",
        "venc_tecnica": "VencTecnica",
        "ruta": "Ruta",
        "venc_ruta": "VencRuta",
        "observaciones": "observaciones",
    }

    for source, target in mapping.items():
        if source in data:
            value = data.pop(source)
            if source in ("patente", "detalle") and value is not None:
                value = value.strip()
                if not value:
                    raise HTTPException(status_code=400, detail=f"{source} es obligatorio")
            setattr(row, target, value)

    if "activo" in data:
        row.activo = _normalize_binary(data.pop("activo"))

    db.commit()
    db.refresh(row)
    return _to_movil_response(row)


@router.delete("/moviles/{idMovil}", response_model=DeleteResponse)
async def delete_movil(
    idMovil: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Movil).filter(Movil.idMovil == idMovil).first()
    if not row:
        raise HTTPException(status_code=404, detail="Movil no encontrado")

    row.activo = 0
    db.commit()
    return DeleteResponse()


@router.get("/unidades-negocio", response_model=list[UnidadNegocioResponse])
async def list_unidades_negocio(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    activo: int | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(UnidadNegocio)
    if buscar:
        pattern = f"%{buscar.strip()}%"
        query = query.filter(or_(UnidadNegocio.Nombre.ilike(pattern), UnidadNegocio.Prefijo.ilike(pattern)))
    if activo in (0, 1):
        query = query.filter(UnidadNegocio.activo == activo)
    rows = query.order_by(UnidadNegocio.Nombre).offset(skip).limit(limit).all()
    return [_to_unidad_response(r) for r in rows]


@router.post("/unidades-negocio", response_model=UnidadNegocioResponse, status_code=status.HTTP_201_CREATED)
async def create_unidad_negocio(
    payload: UnidadNegocioCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    nombre = payload.nombre.strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="Nombre es obligatorio")

    row = UnidadNegocio(
        Nombre=nombre,
        Prefijo=payload.prefijo,
        codigo_kobo=payload.codigo_kobo,
        activo=_normalize_binary(payload.activo),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_unidad_response(row)


@router.put("/unidades-negocio/{idUnidadNegocio}", response_model=UnidadNegocioResponse)
async def update_unidad_negocio(
    idUnidadNegocio: int,
    payload: UnidadNegocioUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(UnidadNegocio).filter(UnidadNegocio.idUnidadNegocio == idUnidadNegocio).first()
    if not row:
        raise HTTPException(status_code=404, detail="Unidad de negocio no encontrada")

    data = payload.model_dump(exclude_unset=True)
    if "nombre" in data:
        nombre = (data.pop("nombre") or "").strip()
        if not nombre:
            raise HTTPException(status_code=400, detail="Nombre es obligatorio")
        row.Nombre = nombre
    if "prefijo" in data:
        row.Prefijo = data.pop("prefijo")
    if "codigo_kobo" in data:
        row.codigo_kobo = data.pop("codigo_kobo")
    if "activo" in data:
        row.activo = _normalize_binary(data.pop("activo"))

    db.commit()
    db.refresh(row)
    return _to_unidad_response(row)


@router.delete("/unidades-negocio/{idUnidadNegocio}", response_model=DeleteResponse)
async def delete_unidad_negocio(
    idUnidadNegocio: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(UnidadNegocio).filter(UnidadNegocio.idUnidadNegocio == idUnidadNegocio).first()
    if not row:
        raise HTTPException(status_code=404, detail="Unidad de negocio no encontrada")

    row.activo = 0
    db.commit()
    return DeleteResponse()


@router.get("/tipos-proceso", response_model=list[TipoProcesoResponse])
async def list_tipos_proceso(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    unidad_id: int | None = None,
    activo: int | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(TipoDeProceso)
    if buscar:
        pattern = f"%{buscar.strip()}%"
        query = query.filter(TipoDeProceso.nombre.ilike(pattern))
    if activo in (0, 1):
        query = query.filter(TipoDeProceso.activo == activo)
    rows = query.order_by(TipoDeProceso.nombre).offset(skip).limit(limit).all()
    if unidad_id:
        rows = [row for row in rows if unidad_id in _tipo_proceso_unidad_ids(db, row)]
    return [_to_tipo_proceso_response(db, r) for r in rows]


@router.post("/tipos-proceso", response_model=TipoProcesoResponse, status_code=status.HTTP_201_CREATED)
async def create_tipo_proceso(
    payload: TipoProcesoCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    nombre = payload.nombre.strip()
    if not nombre:
        raise HTTPException(status_code=400, detail="Nombre es obligatorio")

    row = TipoDeProceso(
        nombre=nombre,
        campos=payload.campos,
        requiere_acta=payload.requiere_acta,
        requiere_predio=payload.requiere_predio,
        requiere_rodal=payload.requiere_rodal,
        activo=_normalize_binary(payload.activo),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    _sync_tipo_proceso_unidades(db, row, payload.unidad_ids)
    db.commit()
    db.refresh(row)
    return _to_tipo_proceso_response(db, row)


@router.put("/tipos-proceso/{tipo_proceso_id}", response_model=TipoProcesoResponse)
async def update_tipo_proceso(
    tipo_proceso_id: int,
    payload: TipoProcesoUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(TipoDeProceso).filter(TipoDeProceso.id == tipo_proceso_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Tipo de proceso no encontrado")

    data = payload.model_dump(exclude_unset=True)
    unidad_ids = data.pop("unidad_ids", None)
    if "nombre" in data:
        nombre = (data.pop("nombre") or "").strip()
        if not nombre:
            raise HTTPException(status_code=400, detail="Nombre es obligatorio")
        row.nombre = nombre
    if "campos" in data:
        row.campos = data.pop("campos")
    if "requiere_acta" in data:
        row.requiere_acta = bool(data.pop("requiere_acta"))
    if "requiere_predio" in data:
        row.requiere_predio = bool(data.pop("requiere_predio"))
    if "requiere_rodal" in data:
        row.requiere_rodal = bool(data.pop("requiere_rodal"))
    if "activo" in data:
        row.activo = _normalize_binary(data.pop("activo"))
    if unidad_ids is not None:
        _sync_tipo_proceso_unidades(db, row, unidad_ids)

    db.commit()
    db.refresh(row)
    return _to_tipo_proceso_response(db, row)


@router.delete("/tipos-proceso/{tipo_proceso_id}", response_model=DeleteResponse)
async def delete_tipo_proceso(
    tipo_proceso_id: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(TipoDeProceso).filter(TipoDeProceso.id == tipo_proceso_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Tipo de proceso no encontrado")

    row.activo = 0
    db.commit()
    return DeleteResponse()


@router.get("/tipos-movil", response_model=list[TipoMovilResponse])
async def list_tipos_movil(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    activo: int | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(TipoMovil)
    if buscar:
        pattern = f"%{buscar.strip()}%"
        query = query.filter(TipoMovil.detalle.ilike(pattern))
    if activo in (0, 1):
        query = query.filter(TipoMovil.activo == activo)
    rows = query.order_by(TipoMovil.detalle).offset(skip).limit(limit).all()
    return [_to_tipo_movil_response(r) for r in rows]


@router.get("/lugares-carga", response_model=list[LugarCargaResponse])
async def list_lugares_carga(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    unidad_id: int | None = None,
    activo: int | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(LugarCarga)
    if buscar:
        query = query.filter(LugarCarga.Detalle.ilike(f"%{buscar.strip()}%"))
    if unidad_id:
        query = query.filter(LugarCarga.unidad_negocio == unidad_id)
    if activo in (0, 1):
        query = query.filter(LugarCarga.activo == activo)
    rows = query.order_by(LugarCarga.Detalle).offset(skip).limit(limit).all()
    return [_to_lugar_carga_response(r) for r in rows]


@router.post("/lugares-carga", response_model=LugarCargaResponse, status_code=status.HTTP_201_CREATED)
async def create_lugar_carga(
    payload: LugarCargaCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    detalle = payload.detalle.strip()
    if not detalle:
        raise HTTPException(status_code=400, detail="Detalle es obligatorio")

    row = LugarCarga(
        Detalle=detalle,
        unidad_negocio=payload.unidad_negocio,
        activo=_normalize_binary(payload.activo),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_lugar_carga_response(row)


@router.put("/lugares-carga/{idLugarCarga}", response_model=LugarCargaResponse)
async def update_lugar_carga(
    idLugarCarga: int,
    payload: LugarCargaUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(LugarCarga).filter(LugarCarga.idLugarCarga == idLugarCarga).first()
    if not row:
        raise HTTPException(status_code=404, detail="Lugar de carga no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "detalle" in data:
        detalle = (data.pop("detalle") or "").strip()
        if not detalle:
            raise HTTPException(status_code=400, detail="Detalle es obligatorio")
        row.Detalle = detalle
    if "unidad_negocio" in data:
        row.unidad_negocio = data.pop("unidad_negocio")
    if "activo" in data:
        row.activo = _normalize_binary(data.pop("activo"))

    db.commit()
    db.refresh(row)
    return _to_lugar_carga_response(row)


@router.delete("/lugares-carga/{idLugarCarga}", response_model=DeleteResponse)
async def delete_lugar_carga(
    idLugarCarga: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(LugarCarga).filter(LugarCarga.idLugarCarga == idLugarCarga).first()
    if not row:
        raise HTTPException(status_code=404, detail="Lugar de carga no encontrado")

    row.activo = 0
    db.commit()
    return DeleteResponse()


@router.get("/predios", response_model=list[PredioResponse])
async def list_predios(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(Predio)
    if buscar:
        pattern = f"%{buscar.strip()}%"
        query = query.filter(or_(Predio.Nombre.ilike(pattern), Predio.empresa.ilike(pattern)))
    rows = query.order_by(Predio.Nombre).offset(skip).limit(limit).all()
    return [_to_predio_response(r) for r in rows]


@router.post("/predios", response_model=PredioResponse, status_code=status.HTTP_201_CREATED)
async def create_predio(
    payload: PredioCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    nombre = payload.nombre.strip()
    empresa = payload.empresa.strip()
    if not nombre or not empresa:
        raise HTTPException(status_code=400, detail="Nombre y empresa son obligatorios")

    next_id = payload.idPredio
    if next_id is None:
        next_id = int((db.query(func.max(Predio.idPredio)).scalar() or 0) + 1)

    row = Predio(
        idPredio=next_id,
        Nombre=nombre,
        empresa=empresa,
        codigo_kobo=payload.codigo_kobo,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_predio_response(row)


@router.put("/predios/{idPredio}", response_model=PredioResponse)
async def update_predio(
    idPredio: int,
    payload: PredioUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Predio).filter(Predio.idPredio == idPredio).first()
    if not row:
        raise HTTPException(status_code=404, detail="Predio no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "nombre" in data:
        nombre = (data.pop("nombre") or "").strip()
        if not nombre:
            raise HTTPException(status_code=400, detail="Nombre es obligatorio")
        row.Nombre = nombre
    if "empresa" in data:
        empresa = (data.pop("empresa") or "").strip()
        if not empresa:
            raise HTTPException(status_code=400, detail="Empresa es obligatoria")
        row.empresa = empresa
    if "codigo_kobo" in data:
        row.codigo_kobo = data.pop("codigo_kobo")

    db.commit()
    db.refresh(row)
    return _to_predio_response(row)


@router.delete("/predios/{idPredio}", response_model=DeleteResponse)
async def delete_predio(
    idPredio: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Predio).filter(Predio.idPredio == idPredio).first()
    if not row:
        raise HTTPException(status_code=404, detail="Predio no encontrado")

    db.delete(row)
    db.commit()
    return DeleteResponse()


@router.get("/rodales", response_model=list[RodalResponse])
async def list_rodales(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(Rodal)
    if buscar:
        query = query.filter(Rodal.Rodal.ilike(f"%{buscar.strip()}%"))
    rows = query.order_by(Rodal.Rodal).offset(skip).limit(limit).all()
    return [_to_rodal_response(r) for r in rows]


@router.post("/rodales", response_model=RodalResponse, status_code=status.HTTP_201_CREATED)
async def create_rodal(
    payload: RodalCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    rodal = payload.rodal.strip()
    if not rodal:
        raise HTTPException(status_code=400, detail="Rodal es obligatorio")

    row = Rodal(
        Rodal=rodal,
        idPredio=payload.idPredio,
        VAM=payload.vam,
        Tarifa=payload.tarifa,
        Extraccion=payload.extraccion,
        Carga=payload.carga,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_rodal_response(row)


@router.put("/rodales/{idRodal}", response_model=RodalResponse)
async def update_rodal(
    idRodal: int,
    payload: RodalUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Rodal).filter(Rodal.idRodal == idRodal).first()
    if not row:
        raise HTTPException(status_code=404, detail="Rodal no encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "rodal" in data:
        rodal = (data.pop("rodal") or "").strip()
        if not rodal:
            raise HTTPException(status_code=400, detail="Rodal es obligatorio")
        row.Rodal = rodal
    if "idPredio" in data:
        row.idPredio = data.pop("idPredio")
    if "vam" in data:
        row.VAM = data.pop("vam")
    if "tarifa" in data:
        row.Tarifa = data.pop("tarifa")
    if "extraccion" in data:
        row.Extraccion = data.pop("extraccion")
    if "carga" in data:
        row.Carga = data.pop("carga")

    db.commit()
    db.refresh(row)
    return _to_rodal_response(row)


@router.delete("/rodales/{idRodal}", response_model=DeleteResponse)
async def delete_rodal(
    idRodal: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Rodal).filter(Rodal.idRodal == idRodal).first()
    if not row:
        raise HTTPException(status_code=404, detail="Rodal no encontrado")

    db.delete(row)
    db.commit()
    return DeleteResponse()


@router.get("/actas", response_model=list[ActaAdminResponse])
async def list_actas_admin(
    skip: int = 0,
    limit: int = 50,
    buscar: str | None = None,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    query = db.query(Acta)
    if buscar:
        query = query.filter(Acta.numero.ilike(f"%{buscar.strip()}%"))
    rows = query.order_by(Acta.numero).offset(skip).limit(limit).all()
    return [_to_acta_admin_response(r) for r in rows]


@router.post("/actas", response_model=ActaAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_acta(
    payload: ActaCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    numero = payload.numero.strip()
    if not numero:
        raise HTTPException(status_code=400, detail="Numero es obligatorio")

    row = Acta(
        numero=numero,
        rodal_id=payload.rodal_id,
        vam=payload.vam,
        tarifa=payload.tarifa,
        extraccion=payload.extraccion,
        carga=payload.carga,
        periodo=payload.periodo,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_acta_admin_response(row)


@router.put("/actas/{acta_id}", response_model=ActaAdminResponse)
async def update_acta(
    acta_id: int,
    payload: ActaUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Acta).filter(Acta.id == acta_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Acta no encontrada")

    data = payload.model_dump(exclude_unset=True)
    if "numero" in data:
        numero = (data.pop("numero") or "").strip()
        if not numero:
            raise HTTPException(status_code=400, detail="Numero es obligatorio")
        row.numero = numero
    if "rodal_id" in data:
        row.rodal_id = data.pop("rodal_id")
    if "vam" in data:
        row.vam = data.pop("vam")
    if "tarifa" in data:
        row.tarifa = data.pop("tarifa")
    if "extraccion" in data:
        row.extraccion = data.pop("extraccion")
    if "carga" in data:
        row.carga = data.pop("carga")
    if "periodo" in data:
        row.periodo = data.pop("periodo")

    db.commit()
    db.refresh(row)
    return _to_acta_admin_response(row)


@router.delete("/actas/{acta_id}", response_model=DeleteResponse)
async def delete_acta(
    acta_id: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(Acta).filter(Acta.id == acta_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Acta no encontrada")

    db.delete(row)
    db.commit()
    return DeleteResponse()


@router.get("/asignaciones", response_model=list[AsignacionOperativaResponse])
async def list_asignaciones(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    rows = (
        db.query(AsignacionOperativa)
        .order_by(AsignacionOperativa.idAsignacion.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_to_asignacion_response(r) for r in rows]


@router.post("/asignaciones", response_model=AsignacionOperativaResponse, status_code=status.HTTP_201_CREATED)
async def create_asignacion(
    payload: AsignacionOperativaCreate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    _ensure_asignacion_consistente(db, payload.idMovil, payload.idChofer, payload.idProceso)
    row = AsignacionOperativa(
        idMovil=payload.idMovil,
        idChofer=payload.idChofer,
        idProceso=payload.idProceso,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_asignacion_response(row)


@router.put("/asignaciones/{idAsignacion}", response_model=AsignacionOperativaResponse)
async def update_asignacion(
    idAsignacion: int,
    payload: AsignacionOperativaUpdate,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(AsignacionOperativa).filter(AsignacionOperativa.idAsignacion == idAsignacion).first()
    if not row:
        raise HTTPException(status_code=404, detail="Asignacion no encontrada")

    data = payload.model_dump(exclude_unset=True)
    next_id_movil = data.get("idMovil", row.idMovil)
    next_id_chofer = data.get("idChofer", row.idChofer)
    next_id_proceso = data.get("idProceso", row.idProceso)
    _ensure_asignacion_consistente(db, next_id_movil, next_id_chofer, next_id_proceso)

    if "idMovil" in data:
        row.idMovil = data.pop("idMovil")
    if "idChofer" in data:
        row.idChofer = data.pop("idChofer")
    if "idProceso" in data:
        row.idProceso = data.pop("idProceso")

    db.commit()
    db.refresh(row)
    return _to_asignacion_response(row)


@router.delete("/asignaciones/{idAsignacion}", response_model=DeleteResponse)
async def delete_asignacion(
    idAsignacion: int,
    db: Session = Depends(get_db),
    _: Personal = Depends(get_current_admin),
):
    row = db.query(AsignacionOperativa).filter(AsignacionOperativa.idAsignacion == idAsignacion).first()
    if not row:
        raise HTTPException(status_code=404, detail="Asignacion no encontrada")

    db.delete(row)
    db.commit()
    return DeleteResponse()
