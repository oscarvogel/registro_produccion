"""Normalizacion canonica del numero de remito de combustible.

Issue #124: en produccion conviven tres formatos para el mismo remito
y eso hace que el reporte "Control de combustible" muestre la misma
carga dos veces:

* Numerico con padding variable: ``011278`` vs ``000000011278``,
  ``1`` vs ``000000000001``.
* Hifenado numerico: ``02-1335`` vs ``0000002-1335`` vs
  ``000200001335``.
* Alfanumerico con prefijo: ``R-0001``, ``D000001``.

Reglas de normalizacion (aplicadas al recibir el POST):

* Se eliminan espacios al principio y al final.
* Si el valor es puramente numerico (``isdigit()``), se completa con
  ceros a la izquierda hasta 12 caracteres.
* Si el valor tiene un guion y ambas partes son numericas
  (formato ``PPPPP-DDDDDDDD``), se reemplaza por la concatenacion
  con la primera parte paddeada a 4 digitos y la segunda a 8
  digitos (total 12).
* Si el valor es alfanumerico (ej. ``R-0001``, ``D000001``), se
  conserva tal cual, en mayusculas, sin padding.
* Solo se permiten letras ASCII (A-Z), digitos (0-9) y guion (-).
  Cualquier otro caracter (puntos, espacios internos, simbolos)
  produce un rechazo claro.
* La longitud final no puede superar los 12 caracteres.

El modulo expone una sola funcion publica ``normalize_remito`` que
devuelve el valor canonico o lanza ``ValueError`` con un mensaje
apto para el usuario final (es devuelto por la API como 400).
"""
from __future__ import annotations

import re

# Coincide con el ancho de las columnas ``cargacomb.remito`` y
# ``tablero_produccion.remito`` (``VARCHAR(12)``).
REMITO_MAX_LENGTH = 12

# Anchos del formato con guion: prefijo de 4 digitos + sufijo de 8.
# El guion se elimina y se reemplaza por padding a izquierda en cada
# parte para obtener un total de 12 caracteres canonicos.
_HYPHEN_PREFIX_WIDTH = 4
_HYPHEN_SUFFIX_WIDTH = 8

# Solo letras ASCII, digitos y guion. Esto rechaza espacios internos,
# puntos, barras, simbolos, letras con tilde, etc.
_ALLOWED_CHARS = re.compile(r"^[A-Z0-9-]+$")
_DIGITS_ONLY = re.compile(r"^[0-9]+$")
_HYPHEN_TWO_NUMERIC = re.compile(r"^([0-9]+)-([0-9]+)$")


def normalize_remito(value: str | None) -> str:
    """Devuelve el remito en formato canonico o lanza ``ValueError``.

    La funcion es pura (no toca la base) y se usa tanto en los schemas
    de entrada como en scripts de migracion / tests.
    """
    if value is None:
        raise ValueError("El remito no puede ser vacio")

    stripped = value.strip()
    if not stripped:
        raise ValueError("El remito no puede ser vacio")

    upper = stripped.upper()

    if not _ALLOWED_CHARS.match(upper):
        raise ValueError(
            "El remito solo puede contener letras, numeros y guion (-)"
        )

    # Formato hifenado numerico: "PPPPP-DDDDDDDD" -> "PPPP" + "DDDDDDDD".
    # Antes de validar el ancho limpiamos ceros a la izquierda en cada
    # parte: en la base conviven "02-1335" y "0000002-1335" y ambos
    # representan el mismo comprobante.
    hyphen_match = _HYPHEN_TWO_NUMERIC.match(upper)
    if hyphen_match:
        prefix = hyphen_match.group(1).lstrip("0") or "0"
        suffix = hyphen_match.group(2).lstrip("0") or "0"
        if len(prefix) > _HYPHEN_PREFIX_WIDTH:
            raise ValueError(
                f"La parte anterior al guion no puede superar los "
                f"{_HYPHEN_PREFIX_WIDTH} digitos"
            )
        if len(suffix) > _HYPHEN_SUFFIX_WIDTH:
            raise ValueError(
                f"La parte posterior al guion no puede superar los "
                f"{_HYPHEN_SUFFIX_WIDTH} digitos"
            )
        return prefix.zfill(_HYPHEN_PREFIX_WIDTH) + suffix.zfill(
            _HYPHEN_SUFFIX_WIDTH
        )

    if _DIGITS_ONLY.match(upper):
        padded = upper.zfill(REMITO_MAX_LENGTH)
        if len(padded) > REMITO_MAX_LENGTH:
            raise ValueError(
                f"El remito numerico no puede superar los "
                f"{REMITO_MAX_LENGTH} digitos"
            )
        return padded

    if len(upper) > REMITO_MAX_LENGTH:
        raise ValueError(
            f"El remito no puede superar los {REMITO_MAX_LENGTH} caracteres"
        )

    return upper


def is_canonical(value: str | None) -> bool:
    """True si ``value`` ya esta en formato canonico (util para tests)."""
    if not value:
        return False
    try:
        return normalize_remito(value) == value
    except ValueError:
        return False
