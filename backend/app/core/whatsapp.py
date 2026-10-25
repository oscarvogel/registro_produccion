"""Cliente de la gateway de WhatsApp de Vogel (``vogel_whatsapp_api``).

Contrato (``vogel_whatsapp_api`` docs/API_V1.md)::

    POST {base}/api/v1/instances/{instancia}/messages
    header: x-api-key
    body:   { phone, message, externalRef, actorId, actorName, sourceApp }
    202 ->  {"success": true, "data": {"messageId": "...", "status": "queued"}}

Dos cosas del contrato que conviene no olvidar:

* **El 202 es "encolado", NO entregado.** La gateway acepta el mensaje y lo
  deja en su cola; para saber si salió hay que consultar
  ``GET /api/v1/instances/{instancia}/messages/{messageId}``. Por eso el
  resultado dice ``queued`` y no ``sent``.
* **El teléfono va solo dígitos, internacional** (10 a 16). La gateway no
  normaliza: un número con ``+``, espacios o guiones se pierde.

Este módulo no hace nada por sí solo: ``enviar_mensaje`` devuelve el resultado
y es el que llama decide si el aviso era obligatorio o un detalle.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)

# La gateway pide solo dígitos: 10 a 16 para un internacional con country code.
_LONGITUD_MINIMA = 10
_LONGITUD_MAXIMA = 16
_NO_DIGITOS = re.compile(r"\D")


@dataclass(frozen=True)
class ResultadoEnvio:
    """Resultado de pedir un envío a la gateway."""

    ok: bool
    estado: str = ""  # "queued" cuando la gateway lo aceptó; "" si no salió
    message_id: str | None = None
    error: str | None = None

    @property
    def encolado(self) -> bool:
        return self.ok and self.estado == "queued"


def normalizar_telefono(valor: str | None) -> str | None:
    """Deja el teléfono como dígitos internacionales, o ``None`` si no sirve.

    Acepta lo que la gente escribe en el campo (``+54 9 3743 51-2000``) y
    devuelve ``5493743512000``. Si el número no tiene una longitud de
    internacional razonable, devuelve ``None``: es mejor no avisar que
    mandarle un mensaje a un número inválido.
    """
    if valor is None:
        return None
    digitos = _NO_DIGITOS.sub("", str(valor))
    if not (_LONGITUD_MINIMA <= len(digitos) <= _LONGITUD_MAXIMA):
        return None
    return digitos


def whatsapp_configurado() -> bool:
    """¿Hay API key e instancia para poder avisar?"""
    return bool(settings.WHATSAPP_API_KEY and settings.WHATSAPP_INSTANCE)


def enviar_mensaje(
    *,
    telefono: str | None,
    mensaje: str,
    external_ref: str | None = None,
    actor_id: str | None = None,
    actor_name: str | None = None,
) -> ResultadoEnvio:
    """Pide a la gateway que envíe un texto.

    Nunca levanta una excepción: un aviso que falla no puede tumbar el alta de
    un parte. Devuelve el resultado y el que llama decide.
    """
    if not settings.WHATSAPP_API_KEY:
        return ResultadoEnvio(ok=False, error="WhatsApp no configurado (falta WHATSAPP_API_KEY)")
    if not settings.WHATSAPP_INSTANCE:
        return ResultadoEnvio(ok=False, error="WhatsApp no configurado (falta WHATSAPP_INSTANCE)")

    destino = normalizar_telefono(telefono)
    if not destino:
        return ResultadoEnvio(ok=False, error=f"Telefono invalido: {telefono!r}")

    texto = (mensaje or "").strip()
    if not texto:
        return ResultadoEnvio(ok=False, error="Mensaje vacio")

    url = (
        f"{settings.WHATSAPP_BASE_URL.rstrip('/')}"
        f"/api/v1/instances/{settings.WHATSAPP_INSTANCE}/messages"
    )
    payload = {
        "phone": destino,
        "message": texto,
        "sourceApp": settings.WHATSAPP_SOURCE_APP,
    }
    if external_ref:
        payload["externalRef"] = external_ref
    if actor_id:
        payload["actorId"] = str(actor_id)
    if actor_name:
        payload["actorName"] = actor_name

    # Import perezoso: si no se usa WhatsApp, la app no carga httpx al entrar.
    import httpx

    try:
        response = httpx.post(
            url,
            json=payload,
            headers={"x-api-key": settings.WHATSAPP_API_KEY},
            timeout=settings.WHATSAPP_TIMEOUT_SECONDS,
        )
    except Exception as exc:  # noqa: BLE001 - la red puede fallar de mil maneras
        logger.warning("No se pudo avisar por WhatsApp: %s: %s", type(exc).__name__, exc)
        return ResultadoEnvio(ok=False, error=f"{type(exc).__name__}: {exc}"[:300])

    if response.status_code not in (200, 202):
        detalle = (response.text or "")[:300]
        logger.warning(
            "La gateway de WhatsApp respondio %s: %s", response.status_code, detalle
        )
        return ResultadoEnvio(
            ok=False, error=f"HTTP {response.status_code}: {detalle}"
        )

    try:
        datos = response.json().get("data") or {}
    except Exception:  # noqa: BLE001
        datos = {}
    message_id = datos.get("messageId")
    estado = str(datos.get("status") or "queued")
    logger.info(
        "Aviso de WhatsApp encolado para %s (messageId=%s, externalRef=%s)",
        destino[-4:],
        message_id,
        payload.get("externalRef"),
    )
    return ResultadoEnvio(ok=True, estado=estado, message_id=message_id)
