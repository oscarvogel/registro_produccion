"""Aviso al encargado cuando hay evidencia fotográfica para validar (issue #206).

El aviso es por WhatsApp, vía la gateway de Vogel (``vogel_whatsapp_api``).

Reglas de la casa:

* **El aviso nunca bloquea el alta del parte.** Si no hay WhatsApp configurado,
  no hay teléfono, no hay encargado o la gateway falla, el parte se guarda
  igual y el motivo queda en el log.
* Se avisa a los **encargados de la unidad** del registro (los que tienen
  ``encargado = 1``), con el teléfono que tiene cargado en ``personal``.
* La foto se sube **antes** de que exista el parte, así que el aviso se manda
  cuando el parte ya está creado y la evidencia quedó vinculada a él: es el
  único momento en que se sabe a qué unidad y a qué registro pertenece.
"""
from __future__ import annotations

import logging

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.whatsapp import (
    ResultadoEnvio,
    enviar_mensaje,
    normalizar_telefono,
    whatsapp_configurado,
)
from app.models.personal import Personal
from app.models.personal_unidad_negocio import PersonalUnidadNegocio

logger = logging.getLogger(__name__)

# Rol de la foto -> como se nombra en el mensaje.
_ROLES = {
    "procesador": "pantalla del procesador",
    "horometro": "horómetro",
}


def encargados_de_la_unidad(db: Session, un_id: int | None) -> list[Personal]:
    """Los personal activos con ``encargado = 1`` de esa unidad de negocio.

    La unidad puede venir por la columna ``personal.unidad_negocio`` o por la
    pivot ``personal_unidad_negocio``: se acepta cualquiera de las dos, como
    en el resto de la app.
    """
    if not un_id:
        return []
    try:
        return (
            db.query(Personal)
            .outerjoin(
                PersonalUnidadNegocio,
                PersonalUnidadNegocio.idPersonal == Personal.idPersonal,
            )
            .filter(
                Personal.encargado == 1,
                Personal.activo == 1,
                or_(
                    Personal.unidad_negocio == int(un_id),
                    PersonalUnidadNegocio.idUnidadNegocio == int(un_id),
                ),
            )
            .distinct()
            .all()
        )
    except SQLAlchemyError:
        # La pivot puede no existir en una base vieja: se cae al filtro por
        # columna en vez de romper el alta del parte.
        db.rollback()
        return (
            db.query(Personal)
            .filter(
                Personal.encargado == 1,
                Personal.activo == 1,
                Personal.unidad_negocio == int(un_id),
            )
            .all()
        )


def _roles_de(evidencias) -> str:
    roles = []
    for fila in evidencias or []:
        tipo = getattr(fila, "tipo", "") or ""
        nombre = _ROLES.get(tipo, tipo or "evidencia")
        if nombre not in roles:
            roles.append(nombre)
    return ", ".join(roles)


def mensaje_evidencia_pendiente(registro, evidencias) -> str:
    """El texto del aviso: qué parte es y qué tiene que revisar."""
    cantidad = len(evidencias or [])
    roles = _roles_de(evidencias)
    unidad = (getattr(registro, "UN", "") or "").strip()
    operador = (getattr(registro, "operador", "") or "").strip()
    operacion = (getattr(registro, "operacion", "") or "").strip()
    fecha = getattr(registro, "fecha", None)

    lineas = [
        "Registro de Producción: hay evidencia para validar.",
        "",
        f"Registro #{getattr(registro, 'id', '?')} — {operacion or 'Producción'}",
    ]
    if fecha:
        lineas.append(f"Fecha: {fecha}")
    if unidad:
        lineas.append(f"Unidad: {unidad}")
    if operador:
        lineas.append(f"Operador: {operador}")
    lineas.append(f"Fotos: {cantidad}" + (f" ({roles})" if roles else ""))
    lineas.append("")
    lineas.append(
        "Quedó cargada y espera tu validación. Entrá a Seguimiento → Detalle de "
        'registros y filtrá por "Esperando verificación".'
    )
    return "\n".join(lineas)


def avisar_evidencia_pendiente(db: Session, registro, evidencias) -> list[ResultadoEnvio]:
    """Avisa a los encargados de la unidad que hay fotos para validar.

    Devuelve los resultados (uno por destinatario). **No levanta excepciones**:
    un aviso que falla no puede impedir que el parte quede guardado.
    """
    try:
        return _avisar(db, registro, evidencias)
    except Exception as exc:  # noqa: BLE001 - el aviso es cortesía, nunca bloqueante
        logger.warning(
            "No se pudo avisar del registro %s: %s: %s",
            getattr(registro, "id", "?"),
            type(exc).__name__,
            exc,
        )
        return []


def _avisar(db: Session, registro, evidencias) -> list[ResultadoEnvio]:
    resultados: list[ResultadoEnvio] = []
    if not evidencias:
        return resultados

    if not whatsapp_configurado():
        logger.info(
            "WhatsApp no configurado: no se avisa del registro %s",
            getattr(registro, "id", "?"),
        )
        return resultados

    un_id = getattr(registro, "cod_un", None)
    responsables = encargados_de_la_unidad(db, un_id)
    if not responsables:
        logger.info(
            "No hay encargados en la unidad %s: no se avisa del registro %s",
            un_id,
            getattr(registro, "id", "?"),
        )
        return resultados

    mensaje = mensaje_evidencia_pendiente(registro, evidencias)
    external_ref = f"registro-produccion:registro:{getattr(registro, 'id', '?')}"

    # El actor de la auditoría de la gateway es quien ORIGINA el aviso (el
    # operador que cargó el parte), no el encargado que lo recibe: en el
    # portal de la gateway se filtra por actorId para ver qué avisos generó
    # cada operador.
    actor_id = getattr(registro, "cod_operador", None)
    actor_name = (getattr(registro, "operador", "") or "").strip()

    for persona in responsables:
        telefono = normalizar_telefono(getattr(persona, "telefono", None))
        if not telefono:
            logger.info(
                "El encargado %s no tiene un teléfono válido cargado: no se le "
                "avisa del registro %s",
                getattr(persona, "idPersonal", "?"),
                getattr(registro, "id", "?"),
            )
            continue
        resultado = enviar_mensaje(
            telefono=telefono,
            mensaje=mensaje,
            external_ref=external_ref,
            actor_id=str(actor_id) if actor_id else None,
            actor_name=actor_name or None,
        )
        if not resultado.ok:
            logger.warning(
                "No se pudo avisar al encargado %s del registro %s: %s",
                getattr(persona, "idPersonal", "?"),
                getattr(registro, "id", "?"),
                resultado.error,
            )
        resultados.append(resultado)

    return resultados
