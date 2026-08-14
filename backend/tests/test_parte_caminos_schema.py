from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.parte_caminos import ParteCaminosCreate


def _base_payload(**overrides):
    payload = {
        "form_uuid": "11111111-2222-3333-4444-555555555555",
        "fecha": date(2026, 8, 14),
        "cod_equipo": 10,
        "equipo": "Motoniveladora 10",
        "cod_operador": 20,
        "operador": "Operador Caminos",
        "cod_un": 30,
        "UN": "Caminos",
        "hr_inicio": 100,
        "hr_fin": 108,
        "procesos": [
            {
                "tipo_proceso_id": 9,
                "predio": "PREDIO 1",
                "acta": "A-1",
                "rodal": "R-1",
                "km_perfilado": 12.5,
            }
        ],
    }
    payload.update(overrides)
    return payload


def test_accepts_multi_process_payload():
    data = ParteCaminosCreate.model_validate(
        _base_payload(
            procesos=[
                {
                    "tipo_proceso_id": 9,
                    "predio": "PREDIO 1",
                    "acta": "A-1",
                    "rodal": "R-1",
                    "km_perfilado": 12.5,
                },
                {
                    "tipo_proceso_id": 20,
                    "predio": "PREDIO 1",
                    "hr_disposicion": 2.25,
                },
                {
                    "tipo_proceso_id": 21,
                    "predio": "PREDIO 2",
                    "hr_remolque": 1.5,
                },
            ]
        )
    )

    assert len(data.procesos) == 3
    assert data.procesos[0].km_perfilado == 12.5
    assert data.procesos[1].hr_disposicion == 2.25
    assert data.procesos[2].hr_remolque == 1.5


def test_rejects_process_without_metric():
    with pytest.raises(ValidationError, match="al menos una metrica"):
        ParteCaminosCreate.model_validate(
            _base_payload(
                procesos=[
                    {
                        "tipo_proceso_id": 9,
                        "predio": "PREDIO 1",
                        "acta": "A-1",
                        "rodal": "R-1",
                    }
                ]
            )
        )


def test_rejects_invalid_hour_range():
    with pytest.raises(ValidationError, match="hora final"):
        ParteCaminosCreate.model_validate(_base_payload(hr_inicio=108, hr_fin=108))


def test_requires_reason_when_non_operational_hours_are_positive():
    with pytest.raises(ValidationError, match="requieren un motivo"):
        ParteCaminosCreate.model_validate(
            _base_payload(hrs_no_op=2, motivo_no_op="0")
        )


def test_rejects_process_hours_over_available_shift_hours():
    with pytest.raises(ValidationError, match="no puede superar las horas operativas"):
        ParteCaminosCreate.model_validate(
            _base_payload(
                hr_inicio=1,
                hr_fin=15,
                procesos=[
                    {
                        "tipo_proceso_id": 20,
                        "predio": "PREDIO 1",
                        "hr_disposicion": 12,
                    },
                    {
                        "tipo_proceso_id": 21,
                        "predio": "PREDIO 1",
                        "hr_remolque": 5,
                    },
                ],
            )
        )


def test_non_operational_hours_reduce_available_process_hours():
    with pytest.raises(ValidationError, match="10 h"):
        ParteCaminosCreate.model_validate(
            _base_payload(
                hr_inicio=1,
                hr_fin=15,
                hrs_no_op=4,
                motivo_no_op="Reparacion",
                procesos=[
                    {
                        "tipo_proceso_id": 20,
                        "predio": "PREDIO 1",
                        "hr_disposicion": 8,
                    },
                    {
                        "tipo_proceso_id": 21,
                        "predio": "PREDIO 1",
                        "hr_remolque": 3,
                    },
                ],
            )
        )


def test_fuel_requires_meter_load_place_and_remito():
    with pytest.raises(ValidationError, match="kilometraje u horometro"):
        ParteCaminosCreate.model_validate(_base_payload(combustible=50))

    with pytest.raises(ValidationError, match="lugar de carga"):
        ParteCaminosCreate.model_validate(
            _base_payload(combustible=50, km_combustible=1234)
        )

    with pytest.raises(ValidationError, match="Remito 1"):
        ParteCaminosCreate.model_validate(
            _base_payload(combustible=50, km_combustible=1234, lugar_carga=1)
        )


def test_remito_is_normalized():
    data = ParteCaminosCreate.model_validate(
        _base_payload(
            combustible=50,
            km_combustible=1234,
            lugar_carga=1,
            remito="123",
        )
    )

    assert data.remito == "000000000123"
