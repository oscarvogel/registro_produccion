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


def test_perfilado_caminos_requires_predio_acta_and_rodal_even_if_global_flags_are_false():
    tipo = _tipo("PERFILADO")

    with pytest.raises(HTTPException, match="predio"):
        _validate_location(tipo, "", "", "")

    with pytest.raises(HTTPException, match="acta"):
        _validate_location(tipo, "PREDIO", "", "")

    with pytest.raises(HTTPException, match="rodal"):
        _validate_location(tipo, "PREDIO", "ACTA", "")

    _validate_location(tipo, "PREDIO", "ACTA", "RODAL")


def test_disposicion_and_remolque_only_add_caminos_predio_requirement():
    for nombre in ("DISPOSICION", "REMOLQUE"):
        tipo = _tipo(nombre)
        with pytest.raises(HTTPException, match="predio"):
            _validate_location(tipo, "", "", "")
        _validate_location(tipo, "PREDIO", "", "")


def test_unknown_process_falls_back_to_global_location_flags():
    tipo = _tipo("OTRO", acta=True)

    with pytest.raises(HTTPException, match="acta"):
        _validate_location(tipo, "", "", "")

    _validate_location(tipo, "", "ACTA", "")
