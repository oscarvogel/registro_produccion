"""Endpoints de la evidencia fotografica de produccion (issue #198).

La foto se sube **antes** que el parte (modo offline, D3): el vinculo estable
es el `form_uuid` del formulario y el `registro_id` se completa cuando el
backend crea el registro.

Reglas que aplica este modulo:

- **R2** la evidencia exigida por el tipo de proceso es obligatoria al crear
  el registro (la validacion vive en `routes/produccion.py`).
- **R5** solo `encargado` o `admin` verifica o rechaza.
- **R7** la cobertura se calcula por roles: una foto de la pantalla del
  procesador cubre tambien el horometro si el operador declaro que se ve en
  esa pantalla (D7).
- **R8** la declaracion del operador viaja con la evidencia
  (`incluye_horometro`) y se muestra al encargado junto a la foto.

Las fotos viven en el volumen del servidor (D2), no en la base: este modulo
es el unico que las escribe y el unico que las sirve.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_or_encargado, get_current_user, get_db
from app.core.config import settings
from app.core.evidencia import (
    ESTADO_PENDIENTE,
    ESTADO_RECHAZADA,
    ESTADO_REEMPLAZADA,
    ESTADO_VERIFICADA,
    ESTADOS_VIVOS,
    ROL_HOROMETRO,
    ROLES,
    EvidenciaError,
    directorio_evidencia,
    extension_para_mime,
    guardar_archivo,
    hash_archivo,
    ruta_absoluta,
    ruta_relativa,
    sanear_form_uuid,
    tope_upload_bytes,
)
from app.core.locks import form_submission_lock
from app.models.evidencia import ProduccionEvidencia
from app.models.personal import Personal
from app.models.produccion import TableroProduccion
from app.schemas.evidencia import EvidenciaResponse, EvidenciaVerificacion

router = APIRouter(prefix="/produccion", tags=["evidencia"])

# MySQL limita el nombre de un lock a 64 caracteres: el prefijo tiene que
# ser corto para que entre el `form_uuid` completo.
LOCK_EVIDENCIA = "prod_evid:{form_uuid}"


# ─── Helpers ───────────────────────────────────────────────────────
def _base_almacenamiento() -> Path:
    """Directorio de evidencia, creado si no existe."""
    base = directorio_evidencia()
    base.mkdir(parents=True, exist_ok=True)
    return base


def _nombre_usuario(user) -> str:
    return str(getattr(user, "Nombre", "") or "")[:80]


def _es_encargado(user) -> bool:
    return (
        int(getattr(user, "is_admin", 0) or 0) == 1
        or int(getattr(user, "encargado", 0) or 0) == 1
    )


def _id_usuario(user) -> int:
    return int(getattr(user, "idPersonal", 0) or 0)


def _a_response(fila: ProduccionEvidencia) -> EvidenciaResponse:
    return EvidenciaResponse(
        id=fila.id,
        registro_id=fila.registro_id,
        form_uuid=fila.form_uuid or "",
        tipo=fila.tipo or "",
        incluye_horometro=bool(fila.incluye_horometro),
        estado=int(fila.estado or 0),
        mime=fila.mime or "",
        tamano=int(fila.tamano or 0),
        hash_sha256=fila.hash_sha256 or "",
        cargado_por=fila.cargado_por or "",
        verificado_por=fila.verificado_por or "",
        verificado_at=fila.verificado_at,
        comentario=fila.comentario or "",
        created_at=fila.created_at,
        url=f"/api/produccion/evidencias/{fila.id}/archivo",
    )


def _evidencia_por_id(db: Session, evidencia_id: int) -> ProduccionEvidencia:
    fila = (
        db.query(ProduccionEvidencia)
        .filter(ProduccionEvidencia.id == int(evidencia_id))
        .first()
    )
    if fila is None:
        raise HTTPException(status_code=404, detail="La evidencia no existe")
    return fila


def _registro_por_id(db: Session, registro_id: int) -> TableroProduccion:
    registro = (
        db.query(TableroProduccion)
        .filter(TableroProduccion.id == int(registro_id))
        .first()
    )
    if registro is None:
        raise HTTPException(status_code=404, detail="El registro no existe")
    return registro


def _puede_ver_registro(user, registro) -> bool:
    """El encargado ve todo; el operador, solo sus propios partes."""
    if _es_encargado(user):
        return True
    return int(getattr(registro, "cod_operador", 0) or 0) == _id_usuario(user)


def _puede_ver_evidencia(user, fila, db: Session) -> bool:
    """El encargado ve todo; el operador, la evidencia que subio o la de su parte."""
    if _es_encargado(user):
        return True
    if fila.cargado_por_id and int(fila.cargado_por_id) == _id_usuario(user):
        return True
    if fila.registro_id:
        registro = (
            db.query(TableroProduccion)
            .filter(TableroProduccion.id == int(fila.registro_id))
            .first()
        )
        if registro is not None and int(getattr(registro, "cod_operador", 0) or 0) == _id_usuario(user):
            return True
    return False


async def _leer_foto(archivo: UploadFile) -> tuple[bytes, str]:
    """Lee el archivo subido y valida mime y tamano."""
    contenido = await archivo.read()
    if not contenido:
        raise HTTPException(status_code=422, detail="La foto viene vacia.")
    if len(contenido) > tope_upload_bytes():
        raise HTTPException(
            status_code=422,
            detail=f"La foto supera el tamano maximo permitido ({settings.EVIDENCIA_MAX_UPLOAD_MB} MB).",
        )
    mime = (archivo.content_type or "").split(";")[0].strip().lower()
    try:
        extension_para_mime(mime)
    except EvidenciaError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return contenido, mime


def _guardar_evidencia(
    db: Session,
    user,
    form_uuid: str,
    tipo: str,
    incluye_horometro: bool,
    contenido: bytes,
    mime: str,
    registro_id: int | None = None,
) -> tuple[ProduccionEvidencia, bool]:
    """Guarda la foto y devuelve (fila, creada).

    La unicidad la garantiza la aplicacion: hay **una sola evidencia viva**
    por `(form_uuid, tipo)`. Si ya hay una:

    - con el mismo hash es un reintento de subida: se devuelve la misma fila;
    - verificada, no se puede reemplazar (409);
    - pendiente, la anterior queda como historial (`reemplazada`) y sube la
      nueva;
    - rechazada, queda como historial del rechazo y sube la nueva (D-F).
    """
    hash_hex = hash_archivo(contenido)
    extension = extension_para_mime(mime)
    ahora = datetime.now()
    base = _base_almacenamiento()
    relativo = ruta_relativa(form_uuid, tipo, hash_hex, extension, ahora)

    previas = (
        db.query(ProduccionEvidencia)
        .filter(
            ProduccionEvidencia.form_uuid == form_uuid,
            ProduccionEvidencia.tipo == tipo,
        )
        .order_by(ProduccionEvidencia.id.desc())
        .all()
    )
    viva = next((f for f in previas if int(f.estado or 0) in ESTADOS_VIVOS), None)

    if viva is not None and (viva.hash_sha256 or "") == hash_hex:
        # Reintento de la misma foto (sync offline): no se duplica nada.
        # Si el archivo no esta (barrido manual), se vuelve a escribir.
        try:
            if not ruta_absoluta(base, viva.archivo).is_file():
                guardar_archivo(base, viva.archivo, contenido)
        except EvidenciaError:
            pass
        return viva, False

    if viva is not None and int(viva.estado or 0) == ESTADO_VERIFICADA:
        raise HTTPException(
            status_code=409,
            detail=(
                "La foto ya fue verificada por un encargado y no se puede "
                "reemplazar. Pedi que la rechacen si hay que subir otra."
            ),
        )

    # El archivo se escribe antes que la fila: una fila nunca apunta a un
    # archivo que no este en disco.
    guardar_archivo(base, relativo, contenido)

    if viva is not None:
        # La foto anterior queda como historial. No se marca como "rechazada"
        # porque ningun encargado la evaluo.
        viva.estado = ESTADO_REEMPLAZADA
        viva.comentario = "Reemplazada por una foto posterior."

    fila = ProduccionEvidencia(
        registro_id=registro_id,
        form_uuid=form_uuid,
        tipo=tipo,
        incluye_horometro=1 if incluye_horometro else 0,
        archivo=relativo,
        mime=mime,
        tamano=len(contenido),
        hash_sha256=hash_hex,
        estado=ESTADO_PENDIENTE,
        cargado_por=_nombre_usuario(user),
        cargado_por_id=_id_usuario(user) or None,
        comentario="",
        created_at=ahora,
    )
    db.add(fila)
    db.flush()
    return fila, True


def _validar_tipo(tipo: str) -> str:
    limpio = (tipo or "").strip().lower()
    if limpio not in ROLES:
        raise HTTPException(
            status_code=422,
            detail="El tipo de evidencia tiene que ser 'procesador' u 'horometro'.",
        )
    return limpio


def _validar_form_uuid(form_uuid: str) -> str:
    limpio = (form_uuid or "").strip()
    if not limpio:
        raise HTTPException(
            status_code=422,
            detail="Falta el identificador del formulario (form_uuid).",
        )
    return limpio


# ─── Subida de la foto ─────────────────────────────────────────────
@router.post("/evidencias", response_model=EvidenciaResponse, status_code=201)
async def crear_evidencia(
    response: Response,
    form_uuid: str = Form(..., max_length=36),
    tipo: str = Form(...),
    archivo: UploadFile = File(...),
    incluye_horometro: bool = Form(False),
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    """Sube una foto de evidencia.

    Idempotente por `(form_uuid, tipo)`: volver a subir la misma foto no
    duplica nada (pasa con los reintentos del sync offline).
    """
    form_uuid = _validar_form_uuid(form_uuid)
    tipo = _validar_tipo(tipo)
    # La foto del horometro ES el horometro: la declaracion solo tiene
    # sentido en la foto de la pantalla del procesador (D7).
    if tipo == ROL_HOROMETRO:
        incluye_horometro = False

    contenido, mime = await _leer_foto(archivo)

    with form_submission_lock(db, LOCK_EVIDENCIA.format(form_uuid=sanear_form_uuid(form_uuid))):
        fila, creada = _guardar_evidencia(
            db, user, form_uuid, tipo, incluye_horometro, contenido, mime
        )
        db.commit()
        db.refresh(fila)

    if not creada:
        response.status_code = 200
    return _a_response(fila)


# ─── Adjuntar foto a un registro ya creado (D-F) ───────────────────
@router.post("/registros/{registro_id}/evidencias", response_model=EvidenciaResponse, status_code=201)
async def adjuntar_evidencia_a_registro(
    registro_id: int,
    response: Response,
    tipo: str = Form(...),
    archivo: UploadFile = File(...),
    incluye_horometro: bool = Form(False),
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    """Sube una foto para un parte ya creado.

    Es el camino de correccion (D-F): si el encargado rechaza la foto, el
    operador sube otra sin tener que rehacer el parte entero.
    """
    registro = _registro_por_id(db, registro_id)
    if not _puede_ver_registro(user, registro):
        raise HTTPException(
            status_code=403,
            detail="No tenes acceso a este registro.",
        )

    tipo = _validar_tipo(tipo)
    if tipo == ROL_HOROMETRO:
        incluye_horometro = False

    contenido, mime = await _leer_foto(archivo)
    form_uuid = (registro.form_uuid or "").strip() or f"registro-{registro.id}"

    with form_submission_lock(db, LOCK_EVIDENCIA.format(form_uuid=sanear_form_uuid(form_uuid))):
        fila, creada = _guardar_evidencia(
            db,
            user,
            form_uuid,
            tipo,
            incluye_horometro,
            contenido,
            mime,
            registro_id=registro.id,
        )
        db.commit()
        db.refresh(fila)

    if not creada:
        response.status_code = 200
    return _a_response(fila)


# ─── Bytes de la foto ──────────────────────────────────────────────
@router.get("/evidencias/{evidencia_id}/archivo")
async def descargar_evidencia(
    evidencia_id: int,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    """Devuelve los bytes de la foto, con su mime real."""
    fila = _evidencia_por_id(db, evidencia_id)
    if not _puede_ver_evidencia(user, fila, db):
        raise HTTPException(
            status_code=403,
            detail="No tenes acceso a esta evidencia.",
        )

    base = directorio_evidencia()
    try:
        destino = ruta_absoluta(base, fila.archivo)
    except EvidenciaError as exc:
        raise HTTPException(
            status_code=404,
            detail="No se encontro el archivo de la evidencia.",
        ) from exc
    if not destino.is_file():
        raise HTTPException(
            status_code=404,
            detail="No se encontro el archivo de la evidencia.",
        )
    return FileResponse(destino, media_type=fila.mime or "application/octet-stream")


# ─── Evidencia de un registro ──────────────────────────────────────
@router.get("/registros/{registro_id}/evidencias", response_model=list[EvidenciaResponse])
async def listar_evidencias_de_registro(
    registro_id: int,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_user),
):
    """Lista la evidencia del registro, con estado y metadatos."""
    registro = _registro_por_id(db, registro_id)
    if not _puede_ver_registro(user, registro):
        raise HTTPException(
            status_code=403,
            detail="No tenes acceso a este registro.",
        )

    filas = (
        db.query(ProduccionEvidencia)
        .filter(ProduccionEvidencia.registro_id == int(registro_id))
        .order_by(ProduccionEvidencia.id)
        .all()
    )
    return [_a_response(fila) for fila in filas]


# ─── Verificacion por el encargado (R5) ─────────────────────────────
@router.patch("/evidencias/{evidencia_id}", response_model=EvidenciaResponse)
async def verificar_evidencia(
    evidencia_id: int,
    data: EvidenciaVerificacion,
    db: Session = Depends(get_db),
    user: Personal = Depends(get_current_admin_or_encargado),
):
    """Marca la evidencia como verificada o rechazada.

    Un rechazo NO borra la foto: queda el registro del intento y el parte
    queda observado.
    """
    if data.estado not in (ESTADO_VERIFICADA, ESTADO_RECHAZADA):
        raise HTTPException(
            status_code=422,
            detail="La evidencia solo puede quedar 'verificada' o 'rechazada'.",
        )

    fila = _evidencia_por_id(db, evidencia_id)
    fila.estado = data.estado
    fila.comentario = (data.comentario or "").strip()[:255]
    fila.verificado_por = _nombre_usuario(user)
    fila.verificado_at = datetime.now()
    db.commit()
    db.refresh(fila)
    return _a_response(fila)
