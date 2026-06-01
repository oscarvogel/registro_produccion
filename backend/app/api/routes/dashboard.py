from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text, case
from typing import List
from datetime import date, timedelta

from app.api.deps import get_db, get_current_admin_or_encargado
from app.models.personal import Personal
from app.models.personal_unidad_negocio import PersonalUnidadNegocio
from app.models.produccion import TableroProduccion
from app.models.tipo_proceso import TipoDeProceso, UnidadNegocioTipoProceso
from app.models.movil import Movil
from app.models.dashboard import KpiDefinicion, TipoProcesoKpi
from app.schemas.dashboard import (
    KpiItem,
    KpisResponse,
    FiltrosAplicados,
    EvolucionResponse,
    DatasetItem,
    RankingMaquinaItem,
    TipoProcesoDisponible,
    MovilDisponible,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _personal_unidad_ids(db: Session, user: Personal) -> set[int]:
    ids = {int(value) for value in [user.unidad_negocio] if value}
    rows = (
        db.query(PersonalUnidadNegocio.idUnidadNegocio)
        .filter(PersonalUnidadNegocio.idPersonal == user.idPersonal)
        .all()
    )
    ids.update(int(value) for (value,) in rows if value)
    return ids


def _verify_un(user: Personal, un_id: int, db: Session):
    """Verificar que el usuario puede consultar la unidad solicitada."""
    if user.is_admin == 1:
        return

    if un_id not in _personal_unidad_ids(db, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para consultar esta unidad de negocio",
        )


# ─── Helpers ───
def _get_tipo_proceso_ids(db: Session, un_id: int, tipo_proceso_id: int | None = None) -> list[int]:
    """Retorna los tipo_proceso_id válidos para la UN (opcionalmente filtrado a uno solo)."""
    query = db.query(UnidadNegocioTipoProceso.tipo_proceso_id).filter(
        UnidadNegocioTipoProceso.un_id == un_id
    )
    ids = [r[0] for r in query.all()]
    if tipo_proceso_id is not None:
        if tipo_proceso_id not in ids:
            raise HTTPException(status_code=400, detail="Tipo de proceso no pertenece a la UN")
        return [tipo_proceso_id]
    return ids


def _resolve_process_filter(tipo_proceso_key: str | None = None, tipo_proceso_id: int | None = None) -> dict | None:
    if tipo_proceso_key:
        key = str(tipo_proceso_key).strip()
        if key.startswith("operacion:"):
            name = key.split(":", 1)[1].strip()
            return {"mode": "operacion", "name": name} if name else None
        if key.startswith("tipo:"):
            key = key.split(":", 1)[1]
        if key.isdigit():
            return {"mode": "tipo", "ids": [int(key)]}

    if tipo_proceso_id is not None:
        return {"mode": "tipo", "ids": [int(tipo_proceso_id)]}
    return None


def _apply_process_filter(base, process_filter: dict | None):
    if not process_filter:
        return base
    if process_filter["mode"] == "tipo":
        return base.filter(TableroProduccion.codigo_tabla.in_(process_filter["ids"]))
    if process_filter["mode"] == "operacion":
        return base.filter(func.upper(func.trim(TableroProduccion.operacion)) == process_filter["name"].upper())
    return base


def _base_filters(query, tp_ids: list[int], movil_id: int | None, fecha_desde: date | None, fecha_hasta: date | None):
    """Aplica los filtros comunes a un query sobre tablero_produccion usando text SQL for operacion matching."""
    # Filtrar por operación: obtener nombres de tipo_proceso
    # Usamos un subquery con los nombres reales
    query = query.filter(TableroProduccion.cod_un.isnot(None))

    if tp_ids:
        query = query.filter(TableroProduccion.tabla == "tipo_de_proceso")
        query = query.filter(TableroProduccion.codigo_tabla.in_(tp_ids))

    if movil_id is not None:
        query = query.filter(TableroProduccion.cod_equipo == movil_id)
    if fecha_desde is not None:
        query = query.filter(TableroProduccion.fecha >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(TableroProduccion.fecha <= fecha_hasta)
    return query


def _apply_data_filters(base, process_filter: dict | None, movil_id: int | None, fecha_desde: date | None, fecha_hasta: date | None):
    """Aplica filtros de datos (tipo proceso explícito, móvil, fechas) a un query base."""
    base = _apply_process_filter(base, process_filter)
    if movil_id is not None:
        base = base.filter(TableroProduccion.cod_equipo == movil_id)
    if fecha_desde is not None:
        base = base.filter(TableroProduccion.fecha >= fecha_desde)
    if fecha_hasta is not None:
        base = base.filter(TableroProduccion.fecha <= fecha_hasta)
    return base


def _compute_kpi_value(db: Session, kpi: KpiDefinicion, process_filter: dict | None, movil_id: int | None, fecha_desde: date | None, fecha_hasta: date | None, un_id: int) -> float:
    """Calcula el valor de un KPI dado los filtros.
    
    filter_tp_ids: lista con un solo ID cuando el usuario eligió un tipo de proceso
                   explícitamente, o None/[] para mostrar todos los datos de la UN.
    """
    campo = kpi.campo_origen

    base = db.query(TableroProduccion).filter(TableroProduccion.cod_un == un_id)
    base = _apply_data_filters(base, process_filter, movil_id, fecha_desde, fecha_hasta)

    if campo == "CUSTOM:horas_trabajadas":
        result = base.with_entities(func.sum(TableroProduccion.hr_fin - TableroProduccion.hr_inicio)).scalar()
        return round(float(result or 0), 2)

    if campo == "CUSTOM:eficiencia":
        hrs_trab = base.with_entities(func.sum(TableroProduccion.hr_fin - TableroProduccion.hr_inicio)).scalar()
        hrs_no_op = base.with_entities(func.sum(TableroProduccion.hrs_no_op)).scalar()
        hrs_trab = float(hrs_trab or 0)
        hrs_no_op = float(hrs_no_op or 0)
        if hrs_trab == 0:
            return 0.0
        return round((hrs_trab - hrs_no_op) / hrs_trab * 100, 2)

    if campo == "CUSTOM:registros" or kpi.agregacion == "COUNT":
        result = base.with_entities(func.count(TableroProduccion.id)).scalar()
        return float(result or 0)

    # Standard aggregation
    col = getattr(TableroProduccion, campo, None)
    if col is None:
        return 0.0

    if kpi.agregacion == "SUM":
        result = base.with_entities(func.sum(col)).scalar()
    elif kpi.agregacion == "AVG":
        result = base.with_entities(func.avg(col)).scalar()
    elif kpi.agregacion == "MAX":
        result = base.with_entities(func.max(col)).scalar()
    else:
        result = 0

    return round(float(result or 0), 2)


def _compute_variation(db: Session, kpi: KpiDefinicion, process_filter: dict | None, movil_id: int | None, fecha_desde: date | None, fecha_hasta: date | None, un_id: int) -> float | None:
    """Calcula la variación porcentual comparando con el período anterior equivalente."""
    if fecha_desde is None or fecha_hasta is None:
        return None

    delta = fecha_hasta - fecha_desde
    prev_hasta = fecha_desde - timedelta(days=1)
    prev_desde = prev_hasta - delta

    current_val = _compute_kpi_value(db, kpi, process_filter, movil_id, fecha_desde, fecha_hasta, un_id)
    prev_val = _compute_kpi_value(db, kpi, process_filter, movil_id, prev_desde, prev_hasta, un_id)

    if prev_val == 0:
        return None
    return round((current_val - prev_val) / prev_val * 100, 2)


def _metric_expr(metric: str):
    if metric == "combustible":
        return func.sum(TableroProduccion.combustible), "Combustible"
    if metric == "registros":
        return func.count(TableroProduccion.id), "Registros"
    return func.sum(TableroProduccion.produccion), "Produccion"


def _fallback_kpis(db: Session, process_filter: dict | None, movil_id: int | None, fecha_desde: date | None, fecha_hasta: date | None, un_id: int) -> list[KpiItem]:
    base = db.query(TableroProduccion).filter(TableroProduccion.cod_un == un_id)
    base = _apply_data_filters(base, process_filter, movil_id, fecha_desde, fecha_hasta)
    row = base.with_entities(
        func.count(TableroProduccion.id).label("registros"),
        func.sum(TableroProduccion.produccion).label("produccion"),
        func.sum(TableroProduccion.combustible).label("combustible"),
        func.sum(TableroProduccion.hr_fin - TableroProduccion.hr_inicio).label("horas"),
    ).first()

    registros = float(row.registros or 0)
    produccion = round(float(row.produccion or 0), 2)
    combustible = round(float(row.combustible or 0), 2)
    horas = round(float(row.horas or 0), 2)
    principal = produccion > 0

    return [
        KpiItem(id=-1, nombre="Produccion total", valor=produccion, unidad="", icono="box", es_principal=principal),
        KpiItem(id=-2, nombre="Registros", valor=registros, unidad="", icono="clipboard-list", es_principal=not principal),
        KpiItem(id=-3, nombre="Combustible", valor=combustible, unidad="L", icono="fuel", es_principal=False),
        KpiItem(id=-4, nombre="Horas", valor=horas, unidad="hs", icono="clock", es_principal=False),
    ]


def _process_label(db: Session, process_filter: dict | None) -> str | None:
    if not process_filter:
        return None
    if process_filter["mode"] == "operacion":
        return process_filter["name"]
    if process_filter["mode"] == "tipo":
        return db.query(TipoDeProceso.nombre).filter(TipoDeProceso.id == process_filter["ids"][0]).scalar()
    return None


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/tipos-proceso-disponibles", response_model=List[TipoProcesoDisponible])
async def tipos_proceso_disponibles(
    un_id: int,
    user: Personal = Depends(get_current_admin_or_encargado),
    db: Session = Depends(get_db),
):
    _verify_un(user, un_id, db)
    catalog_rows = (
        db.query(TipoDeProceso)
        .join(UnidadNegocioTipoProceso, UnidadNegocioTipoProceso.tipo_proceso_id == TipoDeProceso.id)
        .filter(UnidadNegocioTipoProceso.un_id == un_id, TipoDeProceso.activo == 1)
        .order_by(TipoDeProceso.nombre)
        .all()
    )
    options = [
        {
            "id": row.id,
            "nombre": row.nombre,
            "value": f"tipo:{row.id}",
            "source": "catalogo",
        }
        for row in catalog_rows
    ]
    seen_names = {str(row.nombre or "").strip().upper() for row in catalog_rows}

    operation_rows = (
        db.query(TableroProduccion.operacion)
        .filter(
            TableroProduccion.cod_un == un_id,
            TableroProduccion.operacion.isnot(None),
            func.trim(TableroProduccion.operacion) != "",
            func.trim(TableroProduccion.operacion) != "0",
        )
        .group_by(TableroProduccion.operacion)
        .order_by(TableroProduccion.operacion)
        .all()
    )
    next_id = -1
    for (operacion,) in operation_rows:
        name = str(operacion or "").strip()
        if not name or name.upper() in seen_names:
            continue
        options.append({
            "id": next_id,
            "nombre": name,
            "value": f"operacion:{name}",
            "source": "historico",
        })
        next_id -= 1

    return options


@router.get("/moviles-disponibles", response_model=List[MovilDisponible])
async def moviles_disponibles(
    un_id: int,
    tipo_proceso_id: int | None = None,
    tipo_proceso_key: str | None = None,
    user: Personal = Depends(get_current_admin_or_encargado),
    db: Session = Depends(get_db),
):
    _verify_un(user, un_id, db)
    process_filter = _resolve_process_filter(tipo_proceso_key, tipo_proceso_id)

    # Máquinas que tienen al menos un registro en tablero_produccion para esa UN
    query = (
        db.query(Movil.idMovil, Movil.Patente, Movil.Detalle)
        .join(TableroProduccion, TableroProduccion.cod_equipo == Movil.idMovil)
        .filter(TableroProduccion.cod_un == un_id)
    )
    query = _apply_process_filter(query, process_filter)

    query = query.group_by(Movil.idMovil, Movil.Patente, Movil.Detalle).order_by(Movil.Detalle)
    rows = query.all()
    return [MovilDisponible(idMovil=r[0], patente=r[1], detalle=r[2]) for r in rows]


@router.get("/kpis", response_model=KpisResponse)
async def get_kpis(
    un_id: int,
    tipo_proceso_id: int | None = None,
    tipo_proceso_key: str | None = None,
    movil_id: int | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    user: Personal = Depends(get_current_admin_or_encargado),
    db: Session = Depends(get_db),
):
    _verify_un(user, un_id, db)
    process_filter = _resolve_process_filter(tipo_proceso_key, tipo_proceso_id)
    # config_tp_ids: tipos de proceso para buscar configuración de KPIs
    # filter_tp_ids: para filtrar datos de tablero_produccion
    if process_filter and process_filter["mode"] == "tipo":
        config_tp_ids = process_filter["ids"]
    else:
        config_tp_ids = _get_tipo_proceso_ids(db, un_id)

    # Obtener KPIs aplicables según el tipo de proceso seleccionado
    kpi_rows = []
    if config_tp_ids:
        kpi_rows = (
            db.query(KpiDefinicion, TipoProcesoKpi.es_principal, TipoProcesoKpi.orden)
            .join(TipoProcesoKpi, TipoProcesoKpi.kpi_id == KpiDefinicion.id)
            .filter(TipoProcesoKpi.tipo_proceso_id.in_(config_tp_ids), KpiDefinicion.activo == 1)
            .order_by(TipoProcesoKpi.es_principal.desc(), TipoProcesoKpi.orden)
            .all()
        )

    # Deduplicar KPIs (un KPI puede aparecer en varios tipo_proceso)
    # Cuando hay múltiples tipos seleccionados ("Todos"), solo mostrar KPIs comunes
    # y usar Horas Trabajadas como principal del resumen general.
    is_multi = len(config_tp_ids) > 1
    seen = set()
    kpis_result: list[KpiItem] = []

    if is_multi:
        # Contar en cuántos tipos aparece cada KPI
        from collections import Counter
        kpi_tp_count = Counter()
        for kpi_def, _, _ in kpi_rows:
            kpi_tp_count[kpi_def.id] += 1
        total_tps = len(config_tp_ids)

        # Solo KPIs que aparecen en todos los tipos de proceso (comunes)
        common_kpi_ids = {kid for kid, cnt in kpi_tp_count.items() if cnt >= total_tps}

        for kpi_def, es_principal, orden in kpi_rows:
            if kpi_def.id in seen:
                continue
            if kpi_def.id not in common_kpi_ids:
                continue
            seen.add(kpi_def.id)

            # En vista "Todos", Horas Trabajadas es el KPI principal
            is_hero = (kpi_def.campo_origen == "CUSTOM:horas_trabajadas")

            valor = _compute_kpi_value(db, kpi_def, process_filter, movil_id, fecha_desde, fecha_hasta, un_id)
            variacion = _compute_variation(db, kpi_def, process_filter, movil_id, fecha_desde, fecha_hasta, un_id)

            kpis_result.append(KpiItem(
                id=kpi_def.id,
                nombre=kpi_def.nombre,
                valor=valor,
                unidad=kpi_def.unidad,
                icono=kpi_def.icono,
                es_principal=is_hero,
                variacion_porcentual=variacion,
            ))

        # Ordenar: principal primero, luego por orden
        kpis_result.sort(key=lambda k: (not k.es_principal, 0))
    else:
        for kpi_def, es_principal, orden in kpi_rows:
            if kpi_def.id in seen:
                continue
            seen.add(kpi_def.id)

            valor = _compute_kpi_value(db, kpi_def, process_filter, movil_id, fecha_desde, fecha_hasta, un_id)
            variacion = _compute_variation(db, kpi_def, process_filter, movil_id, fecha_desde, fecha_hasta, un_id)

            kpis_result.append(KpiItem(
                id=kpi_def.id,
                nombre=kpi_def.nombre,
                valor=valor,
                unidad=kpi_def.unidad,
                icono=kpi_def.icono,
                es_principal=bool(es_principal),
                variacion_porcentual=variacion,
            ))

    if not kpis_result:
        kpis_result = _fallback_kpis(db, process_filter, movil_id, fecha_desde, fecha_hasta, un_id)

    tp_nombre = _process_label(db, process_filter)

    movil_nombre = None
    if movil_id:
        m = db.query(Movil.Patente).filter(Movil.idMovil == movil_id).scalar()
        movil_nombre = m

    return KpisResponse(
        kpis=kpis_result,
        filtros_aplicados=FiltrosAplicados(
            tipo_proceso=tp_nombre,
            movil=movil_nombre,
            fecha_desde=str(fecha_desde) if fecha_desde else None,
            fecha_hasta=str(fecha_hasta) if fecha_hasta else None,
        ),
    )


@router.get("/evolucion", response_model=EvolucionResponse)
async def get_evolucion(
    un_id: int,
    tipo_proceso_id: int | None = None,
    tipo_proceso_key: str | None = None,
    metric: str = "produccion",
    movil_id: int | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    user: Personal = Depends(get_current_admin_or_encargado),
    db: Session = Depends(get_db),
):
    _verify_un(user, un_id, db)
    if tipo_proceso_id is not None:
        config_tp_ids = [tipo_proceso_id]
        filter_tp_ids = [tipo_proceso_id]
    else:
        config_tp_ids = _get_tipo_proceso_ids(db, un_id)
        filter_tp_ids = None

    process_filter = _resolve_process_filter(tipo_proceso_key, tipo_proceso_id)
    if process_filter and process_filter["mode"] == "tipo":
        config_tp_ids = process_filter["ids"]
        filter_tp_ids = process_filter
    elif process_filter:
        config_tp_ids = []
        filter_tp_ids = process_filter
    elif filter_tp_ids:
        filter_tp_ids = {"mode": "tipo", "ids": filter_tp_ids}

    # Obtener el KPI principal del tipo de proceso seleccionado
    is_multi = len(config_tp_ids) > 1
    if is_multi:
        # En vista "Todos", usar Horas Trabajadas como KPI del gráfico
        kpi_def = db.query(KpiDefinicion).filter(
            KpiDefinicion.campo_origen == "CUSTOM:horas_trabajadas",
            KpiDefinicion.activo == 1,
        ).first()
        if not kpi_def:
            kpi_def = None
    else:
        principal = (
            db.query(KpiDefinicion, TipoProcesoKpi)
            .join(TipoProcesoKpi, TipoProcesoKpi.kpi_id == KpiDefinicion.id)
            .filter(TipoProcesoKpi.tipo_proceso_id.in_(config_tp_ids), TipoProcesoKpi.es_principal == 1, KpiDefinicion.activo == 1)
            .first()
        )
        if not principal:
            kpi_def = None
        else:
            kpi_def = principal[0]
    campo = getattr(kpi_def, "campo_origen", "produccion")
    label = getattr(kpi_def, "nombre", "Produccion")
    if metric == "combustible":
        campo = "combustible"
        label = "Combustible"

    # Base query
    base = db.query(TableroProduccion).filter(TableroProduccion.cod_un == un_id)
    base = _apply_data_filters(base, filter_tp_ids, movil_id, fecha_desde, fecha_hasta)

    # Agrupar por fecha
    if campo == "CUSTOM:horas_trabajadas":
        agg_expr = func.sum(TableroProduccion.hr_fin - TableroProduccion.hr_inicio)
    elif campo == "CUSTOM:eficiencia":
        # No graficamos eficiencia como evolución; usar horas trabajadas como fallback
        agg_expr = func.sum(TableroProduccion.hr_fin - TableroProduccion.hr_inicio)
    elif campo == "CUSTOM:registros":
        agg_expr = func.count(TableroProduccion.id)
    else:
        col = getattr(TableroProduccion, campo, None)
        if col is None:
            return EvolucionResponse(labels=[], datasets=[])
        agg_expr = func.sum(col)

    rows = (
        base.with_entities(TableroProduccion.fecha, agg_expr.label("valor"))
        .group_by(TableroProduccion.fecha)
        .order_by(TableroProduccion.fecha)
        .all()
    )

    labels = [str(r[0]) if r[0] else "" for r in rows]
    valores = [round(float(r[1] or 0), 2) for r in rows]

    return EvolucionResponse(
        labels=labels,
        datasets=[DatasetItem(nombre=label, valores=valores)],
    )


@router.get("/ranking-maquinas", response_model=List[RankingMaquinaItem])
async def get_ranking_maquinas(
    un_id: int,
    tipo_proceso_id: int | None = None,
    tipo_proceso_key: str | None = None,
    metric: str = "produccion",
    movil_id: int | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    user: Personal = Depends(get_current_admin_or_encargado),
    db: Session = Depends(get_db),
):
    _verify_un(user, un_id, db)
    if tipo_proceso_id is not None:
        config_tp_ids = [tipo_proceso_id]
        filter_tp_ids = [tipo_proceso_id]
    else:
        config_tp_ids = _get_tipo_proceso_ids(db, un_id)
        filter_tp_ids = None

    process_filter = _resolve_process_filter(tipo_proceso_key, tipo_proceso_id)
    if process_filter and process_filter["mode"] == "tipo":
        config_tp_ids = process_filter["ids"]
        filter_tp_ids = process_filter
    elif process_filter:
        config_tp_ids = []
        filter_tp_ids = process_filter
    elif filter_tp_ids:
        filter_tp_ids = {"mode": "tipo", "ids": filter_tp_ids}

    # Obtener KPI principal del tipo de proceso seleccionado
    is_multi = len(config_tp_ids) > 1
    if is_multi:
        # En vista "Todos", usar Horas Trabajadas como KPI del ranking
        kpi_def = db.query(KpiDefinicion).filter(
            KpiDefinicion.campo_origen == "CUSTOM:horas_trabajadas",
            KpiDefinicion.activo == 1,
        ).first()
        if not kpi_def:
            kpi_def = None
    else:
        principal = (
            db.query(KpiDefinicion, TipoProcesoKpi)
            .join(TipoProcesoKpi, TipoProcesoKpi.kpi_id == KpiDefinicion.id)
            .filter(TipoProcesoKpi.tipo_proceso_id.in_(config_tp_ids), TipoProcesoKpi.es_principal == 1, KpiDefinicion.activo == 1)
            .first()
        )
        if not principal:
            kpi_def = None
        else:
            kpi_def = principal[0]
    campo = getattr(kpi_def, "campo_origen", "produccion")
    if metric == "combustible":
        campo = "combustible"

    # Base
    base = (
        db.query(TableroProduccion)
        .join(Movil, Movil.idMovil == TableroProduccion.cod_equipo)
        .filter(TableroProduccion.cod_un == un_id)
    )
    base = _apply_data_filters(base, filter_tp_ids, movil_id, fecha_desde, fecha_hasta)

    if campo == "CUSTOM:horas_trabajadas":
        agg_expr = func.sum(TableroProduccion.hr_fin - TableroProduccion.hr_inicio)
    elif campo == "CUSTOM:eficiencia":
        agg_expr = func.sum(TableroProduccion.hr_fin - TableroProduccion.hr_inicio)
    elif campo == "CUSTOM:registros":
        agg_expr = func.count(TableroProduccion.id)
    else:
        col = getattr(TableroProduccion, campo, None)
        if col is None:
            return []
        agg_expr = func.sum(col)

    rows = (
        base.with_entities(
            Movil.Patente,
            Movil.Detalle,
            agg_expr.label("valor"),
            func.count(TableroProduccion.id).label("registros"),
        )
        .group_by(Movil.idMovil, Movil.Patente, Movil.Detalle)
        .order_by(agg_expr.desc())
        .all()
    )

    return [
        RankingMaquinaItem(
            patente=r[0],
            detalle=r[1],
            valor=round(float(r[2] or 0), 2),
            registros=int(r[3]),
        )
        for r in rows
    ]
