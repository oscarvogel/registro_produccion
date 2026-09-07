from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes.parte_caminos import _validate_location


def _tipo(nombre, *, predio=False, acta=False, rodal=False):
    return SimpleNamespace(
        nombre=nombre,
        requiere_predio=predio,
        requiere_acta=acta,
        requiere_rodal=rodal,
    )


def test_perfilado_without_location_flags_does_not_require_location():
    tipo = _tipo("PERFILADO")

    _validate_location(tipo, "", "", "")


def test_disposicion_and_remolque_respect_configured_predio_requirement():
    for nombre in ("DISPOSICION", "REMOLQUE"):
        tipo = _tipo(nombre, predio=True)

        with pytest.raises(HTTPException, match="predio"):
            _validate_location(tipo, "", "", "")

        _validate_location(tipo, "PREDIO", "", "")


@pytest.mark.parametrize(
    ("kwargs", "predio", "acta", "rodal", "message"),
    [
        ({"predio": True}, "", "", "", "predio"),
        ({"acta": True}, "", "", "", "acta"),
        ({"rodal": True}, "", "", "", "rodal"),
    ],
)
def test_location_validation_uses_tipo_de_proceso_flags(kwargs, predio, acta, rodal, message):
    tipo = _tipo("CUALQUIER PROCESO", **kwargs)

    with pytest.raises(HTTPException, match=message):
        _validate_location(tipo, predio, acta, rodal)


def test_all_configured_location_fields_are_accepted_when_present():
    tipo = _tipo("PERFILADO", predio=True, acta=True, rodal=True)

    _validate_location(tipo, "PREDIO", "ACTA", "RODAL")
