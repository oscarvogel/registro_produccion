from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.produccion import TableroProduccionCreate


def build_payload(**overrides):
    data = {
        "fecha": date(2026, 8, 18),
        "operacion": "HORAS MAQUINAS",
        "hr_inicio": 2192.70,
        "hr_fin": 2197.40,
        "produccion": 999,
        "unidad_produccion": "OTRA",
    }
    data.update(overrides)
    return TableroProduccionCreate(**data)


def test_horas_maquinas_calcula_produccion_desde_horometro():
    payload = build_payload()

    assert payload.produccion == 4.70
    assert payload.unidad_produccion == "HS"


def test_horas_maquinas_ignora_produccion_enviada_por_cliente():
    payload = build_payload(produccion=123.45)

    assert payload.produccion == 4.70


def test_horas_maquinas_requiere_fin_mayor_a_inicio():
    with pytest.raises(ValidationError, match="hora final debe ser mayor"):
        build_payload(hr_inicio=2200, hr_fin=2199)


def test_horas_maquinas_no_permite_horometros_en_cero():
    with pytest.raises(ValidationError, match="hora de inicio y hora de fin mayores a cero"):
        build_payload(hr_inicio=0, hr_fin=2199)


def test_otro_proceso_no_reescribe_produccion():
    payload = build_payload(
        operacion="CARGA",
        produccion=15.25,
        unidad_produccion="TN",
    )

    assert payload.produccion == 15.25
    assert payload.unidad_produccion == "TN"
