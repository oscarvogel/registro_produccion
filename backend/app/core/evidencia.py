"""Reglas de la evidencia fotografica de produccion (issues #194 y #198).

La evidencia cubre **roles**, no tipos:

  - ``procesador``: la foto de la pantalla del procesador (plantas y/o m3).
  - ``horometro``: la foto del horometro (lectura final).

Una sola foto puede cubrir LOS DOS roles: cuando el operador declara que el
horometro se ve en esa misma pantalla del procesador (decision D7), esa foto
documenta el horometro tambien. Por eso la cobertura se calcula por roles y
no por el ``tipo`` de la fila.

Las reglas viven aca y no en la pantalla: el frontend las muestra, pero quien
manda es el backend.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

from app.core.config import settings

ROL_PROCESADOR = "procesador"
ROL_HOROMETRO = "horometro"
ROLES = (ROL_PROCESADOR, ROL_HOROMETRO)

ESTADO_PENDIENTE = 0
ESTADO_VERIFICADA = 1
ESTADO_RECHAZADA = 2
# La foto fue reemplazada por una posterior (D-F). Queda como historial: no
# cuenta para la cobertura y NO se muestra como "rechazada", porque ningun
# encargado la evaluo.
ESTADO_REEMPLAZADA = 3
ESTADOS = (ESTADO_PENDIENTE, ESTADO_VERIFICADA, ESTADO_RECHAZADA, ESTADO_REEMPLAZADA)
# Solo la evidencia VIVA cubre un rol (R2/R7): una foto rechazada queda como
# historial del intento, y una reemplazada fue superada por otra.
ESTADOS_VIVOS = (ESTADO_PENDIENTE, ESTADO_VERIFICADA)

# El mime decide la extension: nunca se usa el nombre que manda el cliente
# (evita path traversal y falsificacion de tipo).
MIMES_PERMITIDOS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/heic": ".heic",
    "image/heif": ".heif",
}

# El `form_uuid` lo manda el cliente y entra al nombre del archivo: sin este
# filtro un "../" colado en el nombre permitiria escribir fuera del volumen.
_CARACTERES_SEGUROS = re.compile(r"[^A-Za-z0-9_-]+")


class EvidenciaError(ValueError):
    """Error de validacion de la evidencia, con mensaje para el operador."""


def directorio_evidencia() -> Path:
    """Directorio (raiz) donde viven los archivos de evidencia."""
    return Path(settings.EVIDENCIA_STORAGE_DIR).expanduser()


def tope_upload_bytes() -> int:
    """Tope de tamaño del archivo, en bytes."""
    return int(settings.EVIDENCIA_MAX_UPLOAD_MB) * 1024 * 1024


def sanear_form_uuid(valor: str | None) -> str:
    """Deja solo caracteres seguros para armar un nombre de archivo."""
    limpio = _CARACTERES_SEGUROS.sub("_", (valor or "").strip())
    return limpio[:36] or "desconocido"


def roles_de(tipo: str, incluye_horometro: bool = False) -> set[str]:
    """Roles que cubre una foto."""
    if tipo not in ROLES:
        raise EvidenciaError(f"Tipo de evidencia desconocido: {tipo}")
    roles = {tipo}
    if tipo == ROL_PROCESADOR and incluye_horometro:
        roles.add(ROL_HOROMETRO)
    return roles


def roles_exigidos(requiere_foto_horometro: bool, requiere_foto_procesador: bool) -> set[str]:
    """Roles que exige un tipo de proceso, segun sus flags de configuracion."""
    roles: set[str] = set()
    if requiere_foto_horometro:
        roles.add(ROL_HOROMETRO)
    if requiere_foto_procesador:
        roles.add(ROL_PROCESADOR)
    return roles


def roles_faltantes(exigidos: set[str], evidencias) -> set[str]:
    """Roles exigidos que ninguna evidencia VIVA cubre.

    Una evidencia rechazada no cuenta: el registro queda observado y hay que
    volver a subir la foto.
    """
    cubiertos: set[str] = set()
    for fila in evidencias:
        if int(getattr(fila, "estado", 0) or 0) not in ESTADOS_VIVOS:
            continue
        cubiertos |= roles_de(fila.tipo, bool(fila.incluye_horometro))
    return exigidos - cubiertos


def mensaje_faltante(faltantes: set[str], nombre_proceso: str = "") -> str:
    """Mensaje para el operador, nombrando la foto que falta."""
    partes = []
    if ROL_HOROMETRO in faltantes:
        partes.append(
            "la foto del horometro (o marcar que el horometro se ve en la "
            "pantalla del procesador)"
        )
    if ROL_PROCESADOR in faltantes:
        partes.append("la foto de la pantalla del procesador")
    lista = " y ".join(partes)
    donde = f" para {nombre_proceso}" if nombre_proceso else ""
    return f"Falta {lista}{donde}."


def mensaje_faltante_horometro() -> str:
    """Mensaje de R3: falta la lectura final del horometro."""
    return "Falta la lectura final del horometro."


def proceso_usa_horometro(campos: str | None) -> bool:
    """True si el tipo de proceso reporta horas de horometro.

    El marcador es el CSV `campos` del tipo de proceso: es lo que dice que el
    parte pide lecturas de horometro (hoy: HORAS MAQUINAS, con
    `hora_inicio,hora_fin`).
    """
    lista = {campo.strip().lower() for campo in (campos or "").split(",") if campo.strip()}
    return "hora_inicio" in lista or "hora_fin" in lista


def extension_para_mime(mime: str | None) -> str:
    mime = (mime or "").split(";")[0].strip().lower()
    if mime not in MIMES_PERMITIDOS:
        raise EvidenciaError(
            "Formato de foto no permitido. Se aceptan JPEG, PNG, WebP y HEIC."
        )
    return MIMES_PERMITIDOS[mime]


def hash_archivo(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def ruta_relativa(form_uuid: str, tipo: str, hash_hex: str, extension: str, ahora) -> str:
    """``<YYYY>/<MM>/<form_uuid>_<tipo>_<hash8>.<ext>``.

    Shardeado por mes para no crear un directorio con cientos de miles de
    archivos.
    """
    return (
        f"{ahora.year:04d}/{ahora.month:02d}/"
        f"{sanear_form_uuid(form_uuid)}_{tipo}_{hash_hex[:8]}{extension}"
    )


def ruta_absoluta(base: Path, relativo: str) -> Path:
    """Resuelve la ruta dentro del directorio de evidencia.

    Nunca devuelve algo fuera de ``base``: la ruta viene de la base, pero un
    ``..`` colado ahi no debe poder leer el disco entero.
    """
    base = base.resolve()
    destino = (base / relativo).resolve()
    if not destino.is_relative_to(base):
        raise EvidenciaError("Ruta de archivo invalida")
    return destino


def guardar_archivo(base: Path, relativo: str, contenido: bytes) -> Path:
    """Escribe el archivo de forma atomica (nada de archivos a medias)."""
    destino = ruta_absoluta(base, relativo)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + ".tmp")
    with open(temporal, "wb") as archivo:
        archivo.write(contenido)
    os.replace(temporal, destino)
    return destino


def borrar_archivo(base: Path, relativo: str) -> bool:
    """Borra el archivo si existe. Nunca toca nada fuera del directorio."""
    try:
        destino = ruta_absoluta(base, relativo)
    except EvidenciaError:
        return False
    if destino.is_file():
        destino.unlink()
        return True
    return False
