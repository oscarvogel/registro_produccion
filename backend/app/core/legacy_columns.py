"""Normalizacion de los valores que se guardan en ``tablero_produccion``.

``tablero_produccion`` replica la tabla del sistema legacy (VFP) y sus
columnas son MAS angostas que los catalogos de origen:

======================  ==========  ======  ====================  =====
columna legacy          ancho       catalogo de origen       ancho
======================  ==========  ======  ====================  =====
``rodal``               10          ``rodales.Rodal``        50
``acta``                10          ``actas.numero``         30
``predio``              50          ``predios.Nombre``       100
``equipo``              100         ``moviles.Detalle``      200
``operador``            50          ``personal.nombre``      100
======================  ==========  ======  ====================  =====

Si el valor no entra en la columna, MySQL corta el INSERT con el error 1406
("Data too long for column"). Ese error lo reportaba el backend como un 503
generico ("No se pudieron cargar los datos necesarios..."), asi que el
operador veia un error de carga cuando en realidad estaba guardando, sin
poder saber que corregir, y el parte no se guardaba.

Este modulo deja los valores listos para la columna legacy antes del INSERT:

* :func:`normalize_rodal`: el rodal es un CODIGO. Si llega una etiqueta
  larga (ej. ``PIRAY MEDIO - RODAL 90``) se extrae el codigo (``90``); si no
  se puede reducir a un codigo valido se rechaza con un mensaje claro.
* :func:`normalize_acta`: el numero de acta es una referencia, no se recorta:
  si no entra se rechaza con un mensaje claro.
* :func:`fit_legacy_text`: recorta al ancho de la columna. Se usa para
  nombres descriptivos (equipo, operador, predio), donde perder la cola del
  texto es preferible a bloquear el guardado en el campo.

Las funciones son puras (no tocan la base) y lanzan ``ValueError`` con un
mensaje apto para el usuario final (la API lo devuelve como 422).
"""
from __future__ import annotations

import re

# Anchos de las columnas de `tablero_produccion` (ver `fg_structure.sql`).
RODAL_MAX_LENGTH = 10
ACTA_MAX_LENGTH = 10
PREDIO_MAX_LENGTH = 50
EQUIPO_MAX_LENGTH = 100
OPERADOR_MAX_LENGTH = 50

# "PIRAY MEDIO - RODAL 90" -> "90"
# Se busca la palabra "RODAL" seguida del codigo, en cualquier posicion.
_RODAL_CODE_RE = re.compile(
    r"RODAL[\s\-_]+(?P<code>[0-9A-Za-z][0-9A-Za-z._\-]*)",
    re.IGNORECASE,
)


def normalize_rodal(value: str | None) -> str:
    """Devuelve el codigo del rodal, listo para ``tablero_produccion.rodal``.

    * Codigo corto (caso normal, ``"90"``): se devuelve tal cual.
    * Etiqueta larga (``"PIRAY MEDIO - RODAL 90"``): se extrae el codigo.
    * Valor largo sin codigo reconocible: ``ValueError`` con un mensaje
      que dice que hay que cargar solo el codigo.
    """
    stripped = (value or "").strip()
    if not stripped:
        return ""

    if len(stripped) <= RODAL_MAX_LENGTH:
        return stripped

    match = _RODAL_CODE_RE.search(stripped)
    if match:
        code = match.group("code").strip()
        if code and len(code) <= RODAL_MAX_LENGTH:
            return code

    raise ValueError(
        f"El rodal no puede superar los {RODAL_MAX_LENGTH} caracteres. "
        f"Ingresa solo el codigo del rodal (por ejemplo, 90)."
    )


def normalize_acta(value: str | None) -> str:
    """Devuelve el numero de acta listo para ``tablero_produccion.acta``.

    A diferencia del nombre de un equipo, el numero de acta es una
    referencia: recortarla apuntaria a un acta que no existe, asi que un
    valor que no entra se rechaza con un mensaje claro.
    """
    stripped = (value or "").strip()
    if len(stripped) > ACTA_MAX_LENGTH:
        raise ValueError(
            f"El numero de acta no puede superar los {ACTA_MAX_LENGTH} caracteres."
        )
    return stripped


def fit_legacy_text(value: str | None, max_length: int) -> str:
    """Recorta un texto descriptivo al ancho de la columna legacy.

    Quita los espacios de los bordes (los catalogos vienen con padding) y
    recorta la cola si todavia no entra.
    """
    stripped = (value or "").strip()
    if len(stripped) <= max_length:
        return stripped
    return stripped[:max_length]
