from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import date, datetime
from contextlib import contextmanager

from app.api.deps import get_db, get_current_user
from app.models.personal import Personal
from app.models.personal_unidad_negocio import PersonalUnidadNegocio
from app.models.unidad_negocio import UnidadNegocio
from app.models.tipo_proceso import TipoDeProceso, UnidadNegocioTipoProceso
from app.models.movil import Movil
from app.models.movil_operador import MovilOperador
from app.models.ubicacion import Acta, Predio, Rodal
from app.models.produccion import TableroProduccion
from app.models.carga_comb import CargaComb
from app.models.asignacion_operativa import AsignacionOperativa
from app.models.lugar_carga import LugarCarga
from app.schemas.produccion import (
    OperadorResponse,
    UnidadNegocioResponse,
    TipoProcesoResponse,
    MovilResponse,
    AsignacionOperativaResponse,
    ActaResponse,
    PredioResponse,
    RodalResponse,
    UltimaHoraFinResponse,
    LugarCargaResponse,
    TableroProduccionCreate,
    TableroProduccionResponse,
    MiRegistroItem,
    MisRegistrosResponse,
)

router = APIRouter(prefix="/produccion", tags=["produccion"])


def _acquire_form_submission_lock(db: Session, lock_name: str) -> bool:
    result = db.execute(
        text("SELECT GET_LOCK(:lock_name, 10)"),
        {"lock_name": lock_name},
    ).scalar()
    return result == 1


def _release_form_submission_lock(db: Session, lock_name: str) -> None:
    db.execute(
        text("SELECT RELEASE_LOCK(:lock_name)"),
        {"lock_name": lock_name},
    )


@contextmanager
def _form_submission_lock(db: Session, lock_name: str):
    # Named locks belong to a MySQL connection, not a transaction. Keep this
    # dedicated connection checked out until RELEASE_LOCK has completed.
    connection = db.get_bind().connect()
    try:
        if not _acquire_form_submission_lock(connection, lock_name):
            raise HTTPException(
                status_code=503,
                detail="No se pudo reservar el envío. Se reintentará automáticamente.",
            )
        yield
    finally:
        try:
            _release_form_submission_lock(connection, lock_name)
        finally:
            connection.close()


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


def _personal_unidad_ids(db: Session, personal: Personal) -> list[int]:
    if _table_exists(db, "personal_unidad_negocio"):
        ids = [
            int(value)
            for (value,) in (
                db.query(PersonalUnidadNegocio.idUnidadNegocio)
                .filter(PersonalUnidadNegocio.idPersonal == personal.idPersonal)
                .all()
            )
        ]
        return _normalize_ids(ids, personal.unidad_negocio)
    return _normalize_ids([], personal.unidad_negocio)


def _personal_unidad_ids_map(db: Session, people: list[Personal]) -> dict[int, list[int]]:
    people_by_id = {
        int(person.idPersonal): person
        for person in people
        if person.idPersonal is not None
    }
    unit_ids_by_person = {
        person_id: _normalize_ids([], person.unidad_negocio)
        for person_id, person in people_by_id.items()
    }
    if not people_by_id or not _table_exists(db, "personal_unidad_negocio"):
        return unit_ids_by_person

    relation_rows = (
        db.query(PersonalUnidadNegocio.idPersonal, PersonalUnidadNegocio.idUnidadNegocio)
        .filter(PersonalUnidadNegocio.idPersonal.in_(people_by_id.keys()))
        .all()
    )
    grouped_ids: dict[int, list[int]] = {person_id: [] for person_id in people_by_id}
    for person_id, unit_id in relation_rows:
        try:
            grouped_ids[int(person_id)].append(int(unit_id))
        except (TypeError, ValueError):
            continue

    return {
        person_id: _normalize_ids(grouped_ids.get(person_id), people_by_id[person_id].unidad_negocio)
        for person_id in people_by_id
    }


def _full_tree_unidad_ids(db: Session) -> list[int]:
    if not _table_exists(db, "unidadnegocio"):
        return []
    return [
        int(value)
        for (value,) in (
            db.query(UnidadNegocio.idUnidadNegocio)
            .filter(func.lower(func.trim(UnidadNegocio.Nombre)) == "full tree")
            .all()
        )
    ]


def _restricted_unidad_ids(user: Personal, db: Session) -> list[int] | None:
    if int(user.encargado or 0) != 1:
        return None
    full_tree_ids = _full_tree_unidad_ids(db)
    if not full_tree_ids:
        return None
    user_unit_ids = _personal_unidad_ids(db, user)
    restricted = [unit_id for unit_id in full_tree_ids if unit_id in user_unit_ids]
    return restricted or None


def _allowed_unidad_ids(user: Personal, db: Session, requested_un_id: int | None = None) -> list[int] | None:
    restricted = _restricted_unidad_ids(user, db)
    if restricted is None:
        return [requested_un_id] if requested_un_id else None
    if requested_un_id:
        return [requested_un_id] if requested_un_id in restricted else []
    return restricted


def _personal_belongs_to_any_unidad(db: Session, personal_id: int, unidad_ids: list[int]) -> bool:
    personal = db.query(Personal).filter(Personal.idPersonal == personal_id).first()
    if not personal:
        return False
    return any(unit_id in _personal_unidad_ids(db, personal) for unit_id in unidad_ids)


def _tipo_proceso_habilitado(db: Session, tipo_proceso_id: int, unidad_id: int) -> bool:
    if not _table_exists(db, "unidadnegocio_tipo_proceso"):
        return True
    return (
        db.query(UnidadNegocioTipoProceso)
        .filter(
            UnidadNegocioTipoProceso.un_id == unidad_id,
            UnidadNegocioTipoProceso.tipo_proceso_id == tipo_proceso_id,
        )
        .first()
        is not None
    )


def _validate_restricted_payload(data: TableroProduccionCreate, user: Personal, db: Session) -> None:
    restricted = _restricted_unidad_ids(user, db)
    if restricted is None:
        return

    if not data.cod_un or int(data.cod_un) not in restricted:
        raise HTTPException(status_code=403, detail="La unidad de negocio no esta habilitada para este usuario")

    if not _personal_belongs_to_any_unidad(db, data.cod_operador, restricted):
        raise HTTPException(status_code=403, detail="El operador no esta habilitado para Full Tree")

    movil = db.query(Movil).filter(Movil.idMovil == data.cod_equipo, Movil.activo == 1).first()
    if not movil or int(movil.idUnidadNegocio or 0) not in restricted:
        raise HTTPException(status_code=403, detail="El movil no esta habilitado para Full Tree")

    if data.codigo_tabla and not _tipo_proceso_habilitado(db, data.codigo_tabla, int(data.cod_un)):
        raise HTTPException(status_code=403, detail="El tipo de proceso no esta habilitado para Full Tree")


# ─── Operadores activos (filtrados por unidad de negocio) ───
@router.get("/operadores", response_model=List[OperadorResponse])
async def list_operadores(
    un_id: int | None = None,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    query = db.query(Personal).filter(Personal.activo == 1)
    allowed_ids = _allowed_unidad_ids(user, db, un_id)
    if allowed_ids == []:
        return []
    if allowed_ids:
        if _table_exists(db, "personal_unidad_negocio"):
            query = (
                query.join(PersonalUnidadNegocio, PersonalUnidadNegocio.idPersonal == Personal.idPersonal)
                .filter(PersonalUnidadNegocio.idUnidadNegocio.in_(allowed_ids))
            )
        else:
            query = query.filter(Personal.unidad_negocio.in_(allowed_ids))
    rows = query.distinct().order_by(Personal.Nombre).all()
    unit_ids_by_person = _personal_unidad_ids_map(db, rows)
    return [
        OperadorResponse(
            idPersonal=r.idPersonal,
            nombre=r.Nombre,
            dni=r.dni,
            encargado=r.encargado,
            tipo_de_proceso_id=r.tipo_de_proceso_id,
            unidad_ids=unit_ids_by_person.get(int(r.idPersonal), []),
        )
        for r in rows
    ]


# ─── Unidades de negocio activas ───
@router.get("/unidades-negocio", response_model=List[UnidadNegocioResponse])
async def list_unidades_negocio(
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    if not _table_exists(db, "unidadnegocio"):
        return []

    query = db.query(UnidadNegocio).filter(UnidadNegocio.activo == 1)
    allowed_ids = _allowed_unidad_ids(user, db)
    if allowed_ids:
        query = query.filter(UnidadNegocio.idUnidadNegocio.in_(allowed_ids))

    rows = query.order_by(UnidadNegocio.Nombre).all()

    if not rows and not allowed_ids:
        rows = db.query(UnidadNegocio).order_by(UnidadNegocio.Nombre).all()

    return [
        UnidadNegocioResponse(
            idUnidadNegocio=r.idUnidadNegocio,
            nombre=r.Nombre,
        )
        for r in rows
    ]


# ─── Tipos de proceso filtrados por UN (via pivot table) ───
@router.get("/tipo-proceso", response_model=List[TipoProcesoResponse])
async def list_tipo_proceso(
    un_id: int,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    allowed_ids = _allowed_unidad_ids(user, db, un_id)
    if allowed_ids == []:
        return []

    rows = (
        db.query(TipoDeProceso)
        .join(UnidadNegocioTipoProceso, UnidadNegocioTipoProceso.tipo_proceso_id == TipoDeProceso.id)
        .filter(
            UnidadNegocioTipoProceso.un_id == un_id,
            TipoDeProceso.activo == 1,
        )
        .order_by(TipoDeProceso.nombre)
        .all()
    )
    return rows


# ─── Todos los tipos de proceso ───
@router.get("/tipos-proceso-all", response_model=List[TipoProcesoResponse])
async def list_all_tipos_proceso(
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    query = db.query(TipoDeProceso).filter(TipoDeProceso.activo == 1)
    allowed_ids = _allowed_unidad_ids(user, db)
    if allowed_ids and _table_exists(db, "unidadnegocio_tipo_proceso"):
        query = (
            query.join(UnidadNegocioTipoProceso, UnidadNegocioTipoProceso.tipo_proceso_id == TipoDeProceso.id)
            .filter(UnidadNegocioTipoProceso.un_id.in_(allowed_ids))
        )
    return query.order_by(TipoDeProceso.nombre).all()


# ─── Asignaciones operativas de un operador ───
@router.get("/asignaciones/{operador_id}", response_model=List[AsignacionOperativaResponse])
async def list_asignaciones(
    operador_id: int,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    """Devuelve todas las asignaciones (movil + proceso) del operador."""
    if not _table_exists(db, "asignaciones_operativas") or not _table_exists(db, "moviles"):
        return []

    allowed_ids = _allowed_unidad_ids(user, db)
    if allowed_ids and not _personal_belongs_to_any_unidad(db, operador_id, allowed_ids):
        return []

    query = (
        db.query(AsignacionOperativa, Movil)
        .join(Movil, Movil.idMovil == AsignacionOperativa.idMovil)
        .filter(
            AsignacionOperativa.idChofer == operador_id,
            Movil.activo == 1,
        )
    )
    if allowed_ids:
        query = query.filter(Movil.idUnidadNegocio.in_(allowed_ids))
        if _table_exists(db, "unidadnegocio_tipo_proceso"):
            allowed_process_ids = [
                int(value)
                for (value,) in (
                    db.query(UnidadNegocioTipoProceso.tipo_proceso_id)
                    .filter(UnidadNegocioTipoProceso.un_id.in_(allowed_ids))
                    .all()
                )
            ]
            query = query.filter(AsignacionOperativa.idProceso.in_(allowed_process_ids or [-1]))

    rows = query.all()
    return [
        AsignacionOperativaResponse(
            idAsignacion=asig.idAsignacion,
            idMovil=asig.idMovil,
            idChofer=asig.idChofer,
            idProceso=asig.idProceso,
            patente=movil.Patente,
            detalle=movil.Detalle,
        )
        for asig, movil in rows
    ]


# ─── Buscar movil/maquina por operador (legacy fallback) ───
@router.get("/movil-by-operador/{operador_id}", response_model=MovilResponse | None)
async def get_movil_by_operador(
    operador_id: int,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    today = date.today()
    allowed_ids = _allowed_unidad_ids(user, db)
    if allowed_ids and not _personal_belongs_to_any_unidad(db, operador_id, allowed_ids):
        return None

    # 1. Buscar en asignaciones_operativas primero
    if _table_exists(db, "asignaciones_operativas") and _table_exists(db, "moviles"):
        asig = (
            db.query(AsignacionOperativa)
            .filter(AsignacionOperativa.idChofer == operador_id)
            .first()
        )
        if asig:
            movil_query = db.query(Movil).filter(Movil.idMovil == asig.idMovil, Movil.activo == 1)
            if allowed_ids:
                movil_query = movil_query.filter(Movil.idUnidadNegocio.in_(allowed_ids))
            movil = movil_query.first()
            if movil:
                return MovilResponse(
                    idMovil=movil.idMovil,
                    patente=movil.Patente,
                    detalle=movil.Detalle,
                    idChofer=movil.idChofer,
                )

    # 2. Buscar en moviles_operadores (asignación con rango de fechas)
    if _table_exists(db, "moviles_operadores") and _table_exists(db, "moviles"):
        asignacion = (
            db.query(MovilOperador)
            .filter(
                MovilOperador.operador_id == operador_id,
                MovilOperador.desde <= today,
                or_(MovilOperador.hasta >= today, MovilOperador.hasta.is_(None)),
            )
            .first()
        )

        if asignacion:
            movil_id_texto = str(asignacion.movil_id or "")
            movil_query = db.query(Movil).filter(
                or_(
                    Movil.Patente == movil_id_texto,
                    Movil.idMovil == int(movil_id_texto)
                    if movil_id_texto.isdigit()
                    else False,
                ),
                Movil.activo == 1,
            )
            if allowed_ids:
                movil_query = movil_query.filter(Movil.idUnidadNegocio.in_(allowed_ids))
            movil = movil_query.first()
            if movil:
                return MovilResponse(
                    idMovil=movil.idMovil,
                    patente=movil.Patente,
                    detalle=movil.Detalle,
                    idChofer=movil.idChofer,
                )

    # 3. Fallback: buscar en moviles.idChofer
    if _table_exists(db, "moviles"):
        movil_query = db.query(Movil).filter(Movil.idChofer == operador_id, Movil.activo == 1)
        if allowed_ids:
            movil_query = movil_query.filter(Movil.idUnidadNegocio.in_(allowed_ids))
        movil = movil_query.first()
        if movil:
            return MovilResponse(
                idMovil=movil.idMovil,
                patente=movil.Patente,
                detalle=movil.Detalle,
                idChofer=movil.idChofer,
            )

    return None


# ─── Catálogo de máquinas (con filtro opcional por UN) ───
@router.get("/moviles", response_model=List[MovilResponse])
async def list_moviles(
    un_id: int | None = None,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    query = db.query(Movil).filter(Movil.activo == 1)
    allowed_ids = _allowed_unidad_ids(user, db, un_id)
    if allowed_ids == []:
        return []
    if allowed_ids:
        query = query.filter(Movil.idUnidadNegocio.in_(allowed_ids))
    rows = query.order_by(Movil.Detalle, Movil.Patente).all()
    return [
        MovilResponse(
            idMovil=r.idMovil,
            patente=r.Patente,
            detalle=r.Detalle,
            idChofer=r.idChofer,
        )
        for r in rows
    ]


# ─── Actas ───
@router.get("/actas", response_model=List[ActaResponse])
async def list_actas(db: Session = Depends(get_db)):
    if not _table_exists(db, "actas"):
        return []
    rows = db.query(Acta).order_by(Acta.numero).all()
    seen_numeros: set[str] = set()
    unique_rows = []
    for row in rows:
        numero = str(row.numero or "").strip()
        if numero in seen_numeros:
            continue
        seen_numeros.add(numero)
        unique_rows.append(row)
    return unique_rows


# ─── Predios ───
@router.get("/predios", response_model=List[PredioResponse])
async def list_predios(db: Session = Depends(get_db)):
    rows = db.query(Predio).order_by(Predio.Nombre).all()
    return [
        PredioResponse(idPredio=r.idPredio, nombre=r.Nombre)
        for r in rows
    ]


# ─── Rodales (filtrados por predio) ───
@router.get("/rodales", response_model=List[RodalResponse])
async def list_rodales(predio_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Rodal)
    if predio_id:
        query = query.filter(Rodal.idPredio == predio_id)
    rows = query.order_by(Rodal.Rodal).all()
    return [
        RodalResponse(idRodal=r.idRodal, rodal=r.Rodal, idPredio=r.idPredio)
        for r in rows
    ]


# ─── Lugares de Carga ───
@router.get("/lugares-carga", response_model=List[LugarCargaResponse])
async def list_lugares_carga(un_id: int | None = None, db: Session = Depends(get_db)):
    if not _table_exists(db, "lugarcarga"):
        return []
    query = db.query(LugarCarga).filter(LugarCarga.activo == 1)
    if un_id:
        query = query.filter(LugarCarga.unidad_negocio == un_id)
    rows = query.order_by(LugarCarga.Detalle).all()
    return [LugarCargaResponse(idLugarCarga=r.idLugarCarga, detalle=r.Detalle) for r in rows]


@router.get("/ultima-hora-fin", response_model=UltimaHoraFinResponse)
async def get_ultima_hora_fin(
    cod_operador: int | None = None,
    cod_un: int | None = None,
    codigo_tabla: int | None = None,
    cod_equipo: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(TableroProduccion).filter(
        TableroProduccion.hr_fin.isnot(None),
    )

    # When a machine is specified, use it as the primary filter (across all operators)
    # so the new hr_inicio is never below the last hr_fin of that machine.
    if cod_equipo:
        query = query.filter(TableroProduccion.cod_equipo == cod_equipo)
    elif cod_operador:
        query = query.filter(TableroProduccion.cod_operador == cod_operador)
    else:
        return UltimaHoraFinResponse(hr_fin=None)

    if cod_un:
        query = query.filter(TableroProduccion.cod_un == cod_un)
    if codigo_tabla:
        query = query.filter(TableroProduccion.codigo_tabla == codigo_tabla)

    row = (
        query
        .order_by(
            TableroProduccion.fecha.desc(),
            TableroProduccion.fecha_hora.desc(),
            TableroProduccion.id.desc(),
        )
        .first()
    )

    if not row or row.hr_fin is None:
        return UltimaHoraFinResponse(hr_fin=None)

    return UltimaHoraFinResponse(hr_fin=float(row.hr_fin))


# ─── Crear registro en tablero_produccion ───
@router.post("/", response_model=TableroProduccionResponse, status_code=201)
async def create_produccion(
    data: TableroProduccionCreate,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    _validate_restricted_payload(data, user, db)

    # This table assigns IDs with MAX(id)+1, so serialize all creations. The
    # same lock also makes the idempotency lookup + insert atomic.
    with _form_submission_lock(db, "registro_produccion:create"):
        # The named MySQL lock makes the lookup + insert atomic across workers.
        if data.form_uuid:
            existing = (
                db.query(TableroProduccion)
                .filter(
                    TableroProduccion.form_uuid == data.form_uuid,
                    TableroProduccion.cod_operador == data.cod_operador,
                )
                .first()
            )
            if existing:
                return existing

        # Get next ID (tablero_produccion doesn't have auto_increment)
        max_id = db.query(func.max(TableroProduccion.id)).scalar() or 0
        new_id = max_id + 1

        registro = TableroProduccion(
            id=new_id,
            form_uuid=data.form_uuid,
            UN=data.UN,
            operacion=data.operacion,
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
            acta=data.acta,
            rodal=data.rodal,
            predio=data.predio,
            m3=data.m3,
            carros=data.carros,
            tn_despachadas=data.tn_despachadas,
            has=data.has,
            produccion=data.produccion,
            plantas=data.plantas,
            mtrs_recorridos=data.mtrs_recorridos,
            km_carreteo=data.km_carreteo,
            km_perfilado=data.km_perfilado,
            hr_disposicion=data.hr_disposicion,
            hrs_no_op=data.hrs_no_op,
            motivo_no_op=data.motivo_no_op,
            observaciones=data.observaciones,
            unidad_produccion=data.unidad_produccion,
            espada=data.espada,
            puntera=data.puntera,
            cadena=data.cadena,
            pinon=data.pinon,
            cantidad_cadenas=data.cantidad_cadenas,
            pies_16=data.pies_16,
            pies_14=data.pies_14,
            pies_12=data.pies_12,
            pies_10=data.pies_10,
            pulpable=data.pulpable,
            lugar_carga=data.lugar_carga,
            tabla=data.tabla,
            codigo_tabla=data.codigo_tabla,
            fecha_hora=datetime.now(),
            origen="web",
        )
        db.add(registro)
        db.flush()

        # Si se cargó combustible, crear registro en cargacomb
        if data.combustible and data.combustible > 0:
            now = datetime.now()
            carga = CargaComb(
                idMovil=data.cod_equipo or 0,
                idTipoComb=1,  # Gasoil por defecto
                Fecha=data.fecha,
                KM=0,
                Litros=data.combustible,
                UnidadNegocio=data.cod_un or 1,
                personal=data.cod_operador or 1,
                idtabla=str(new_id),
                tabla="tablero_produccion",
                _usuario="web",
                _fecha=now.date(),
                _hora=now.strftime("%H:%M:%S"),
            )
            db.add(carga)

        db.commit()
        db.refresh(registro)
        return registro


@router.get("/mis-registros", response_model=MisRegistrosResponse)
async def get_mis_registros(
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    user: Personal = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(TableroProduccion).filter(
        TableroProduccion.cod_operador == user.idPersonal
    )
    if fecha_desde:
        query = query.filter(TableroProduccion.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(TableroProduccion.fecha <= fecha_hasta)

    rows = query.order_by(TableroProduccion.fecha.desc(), TableroProduccion.id.desc()).all()

    registros = [
        MiRegistroItem(
            id=r.id,
            fecha=r.fecha,
            operacion=r.operacion or "",
            equipo=r.equipo or "",
            combustible=int(r.combustible or 0),
            tn_despachadas=float(r.tn_despachadas or 0),
            m3=int(r.m3 or 0),
            has=float(r.has or 0),
            carros=int(r.carros or 0),
            plantas=int(r.plantas or 0),
            km_carreteo=float(r.km_carreteo or 0),
            km_perfilado=float(r.km_perfilado or 0),
            mtrs_recorridos=int(r.mtrs_recorridos or 0),
            hr_inicio=float(r.hr_inicio or 0),
            hr_fin=float(r.hr_fin or 0),
        )
        for r in rows
    ]

    total_tn = round(sum(r.tn_despachadas for r in registros), 2)
    total_m3 = sum(r.m3 for r in registros)
    total_has = round(sum(r.has for r in registros), 2)
    total_carros = sum(r.carros for r in registros)
    total_plantas = sum(r.plantas for r in registros)
    total_km_carreteo = round(sum(r.km_carreteo for r in registros), 2)
    total_km_perfilado = round(sum(r.km_perfilado for r in registros), 2)
    total_combustible = sum(r.combustible for r in registros)
    total_horas = round(sum(max(r.hr_fin - r.hr_inicio, 0) for r in registros), 2)

    def _por_hora(val: float) -> float | None:
        if total_horas == 0 or val == 0:
            return None
        return round(val / total_horas, 2)

    return MisRegistrosResponse(
        registros=registros,
        total=len(registros),
        total_horas=total_horas,
        total_combustible=total_combustible,
        total_tn=total_tn,
        total_m3=total_m3,
        total_has=total_has,
        total_carros=total_carros,
        total_plantas=total_plantas,
        total_km_carreteo=total_km_carreteo,
        total_km_perfilado=total_km_perfilado,
        combustible_por_hora=_por_hora(total_combustible),
        tn_por_hora=_por_hora(total_tn),
        m3_por_hora=_por_hora(total_m3),
        has_por_hora=_por_hora(total_has),
        carros_por_hora=_por_hora(total_carros),
        plantas_por_hora=_por_hora(total_plantas),
        km_carreteo_por_hora=_por_hora(total_km_carreteo),
        km_perfilado_por_hora=_por_hora(total_km_perfilado),
    )
