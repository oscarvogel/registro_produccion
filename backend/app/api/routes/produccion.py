from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List
from datetime import date, datetime

from app.api.deps import get_db
from app.models.personal import Personal
from app.models.unidad_negocio import UnidadNegocio
from app.models.tipo_proceso import TipoDeProceso, UnidadNegocioTipoProceso
from app.models.movil import Movil
from app.models.movil_operador import MovilOperador
from app.models.ubicacion import Acta, Predio, Rodal
from app.models.produccion import TableroProduccion
from app.models.asignacion_operativa import AsignacionOperativa
from app.schemas.produccion import (
    OperadorResponse,
    UnidadNegocioResponse,
    TipoProcesoResponse,
    MovilResponse,
    AsignacionOperativaResponse,
    ActaResponse,
    PredioResponse,
    RodalResponse,
    TableroProduccionCreate,
    TableroProduccionResponse,
)

router = APIRouter(prefix="/produccion", tags=["produccion"])


# ─── Operadores activos (filtrados por unidad de negocio) ───
@router.get("/operadores", response_model=List[OperadorResponse])
async def list_operadores(un_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Personal).filter(Personal.activo == 1)
    if un_id:
        query = query.filter(Personal.unidad_negocio == un_id)
    rows = query.order_by(Personal.Nombre).all()
    return [
        OperadorResponse(
            idPersonal=r.idPersonal,
            nombre=r.Nombre,
            dni=r.dni,
            encargado=r.encargado,
            tipo_de_proceso_id=r.tipo_de_proceso_id,
        )
        for r in rows
    ]


# ─── Unidades de negocio activas ───
@router.get("/unidades-negocio", response_model=List[UnidadNegocioResponse])
async def list_unidades_negocio(db: Session = Depends(get_db)):
    rows = (
        db.query(UnidadNegocio)
        .filter(UnidadNegocio.activo == 1)
        .order_by(UnidadNegocio.Nombre)
        .all()
    )
    return [
        UnidadNegocioResponse(
            idUnidadNegocio=r.idUnidadNegocio,
            nombre=r.Nombre,
        )
        for r in rows
    ]


# ─── Tipos de proceso filtrados por UN (via pivot table) ───
@router.get("/tipo-proceso", response_model=List[TipoProcesoResponse])
async def list_tipo_proceso(un_id: int, db: Session = Depends(get_db)):
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
async def list_all_tipos_proceso(db: Session = Depends(get_db)):
    return db.query(TipoDeProceso).filter(TipoDeProceso.activo == 1).order_by(TipoDeProceso.nombre).all()


# ─── Asignaciones operativas de un operador ───
@router.get("/asignaciones/{operador_id}", response_model=List[AsignacionOperativaResponse])
async def list_asignaciones(operador_id: int, db: Session = Depends(get_db)):
    """Devuelve todas las asignaciones (movil + proceso) del operador."""
    rows = (
        db.query(AsignacionOperativa, Movil)
        .join(Movil, Movil.idMovil == AsignacionOperativa.idMovil)
        .filter(
            AsignacionOperativa.idChofer == operador_id,
            Movil.activo == 1,
        )
        .all()
    )
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
async def get_movil_by_operador(operador_id: int, db: Session = Depends(get_db)):
    today = date.today()

    # 1. Buscar en asignaciones_operativas primero
    asig = (
        db.query(AsignacionOperativa)
        .filter(AsignacionOperativa.idChofer == operador_id)
        .first()
    )
    if asig:
        movil = db.query(Movil).filter(Movil.idMovil == asig.idMovil, Movil.activo == 1).first()
        if movil:
            return MovilResponse(
                idMovil=movil.idMovil,
                patente=movil.Patente,
                detalle=movil.Detalle,
                idChofer=movil.idChofer,
            )

    # 2. Buscar en moviles_operadores (asignación con rango de fechas)
    asignacion = (
        db.query(MovilOperador)
        .filter(
            MovilOperador.operador_id == operador_id,
            MovilOperador.desde <= today,
            or_(MovilOperador.hasta >= today, MovilOperador.hasta == "0000-00-00"),
        )
        .first()
    )

    if asignacion:
        movil = (
            db.query(Movil)
            .filter(
                or_(
                    Movil.Patente == asignacion.movil_id,
                    Movil.idMovil == int(asignacion.movil_id)
                    if asignacion.movil_id.isdigit()
                    else False,
                ),
                Movil.activo == 1,
            )
            .first()
        )
        if movil:
            return MovilResponse(
                idMovil=movil.idMovil,
                patente=movil.Patente,
                detalle=movil.Detalle,
                idChofer=movil.idChofer,
            )

    # 3. Fallback: buscar en moviles.idChofer
    movil = (
        db.query(Movil)
        .filter(Movil.idChofer == operador_id, Movil.activo == 1)
        .first()
    )
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
async def list_moviles(un_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Movil).filter(Movil.activo == 1)
    if un_id:
        query = query.filter(Movil.idUnidadNegocio == un_id)
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
    return db.query(Acta).order_by(Acta.numero).all()


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


# ─── Crear registro en tablero_produccion ───
@router.post("/", response_model=TableroProduccionResponse, status_code=201)
async def create_produccion(data: TableroProduccionCreate, db: Session = Depends(get_db)):
    # Get next ID (tablero_produccion doesn't have auto_increment)
    max_id = db.query(func.max(TableroProduccion.id)).scalar() or 0
    new_id = max_id + 1

    registro = TableroProduccion(
        id=new_id,
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
        tabla=data.tabla,
        codigo_tabla=data.codigo_tabla,
        fecha_hora=datetime.now(),
        origen="web",
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro
