"""Regresión: las filas hermanas de Caminos comparten una sola jornada."""

from datetime import date

from app.api.routes.dashboard import _aggregate_jornadas, _jornada_key


def row(fecha, registro_id, form_uuid, hr_inicio, hr_fin, hrs_no_op=0):
    return (fecha, registro_id, form_uuid, hr_inicio, hr_fin, hrs_no_op)


def test_jornada_key_usa_form_uuid_y_legacy_por_id():
    assert _jornada_key(10, " abc ") == "form:abc"
    assert _jornada_key(10, None) == "legacy:10"
    assert _jornada_key(11, "") == "legacy:11"


def test_dos_procesos_mismo_form_uuid_suman_una_sola_jornada():
    fecha = date(2026, 8, 20)
    grouped = _aggregate_jornadas(
        [
            row(fecha, 1, "FORM-A", 8351, 8359),
            row(fecha, 2, "FORM-A", 8351, 8359),
        ],
        (0,),
    )

    assert len(grouped) == 1
    assert sum(item["horas"] for item in grouped.values()) == 8


def test_dos_form_uuid_distintos_suman_dos_jornadas():
    fecha = date(2026, 8, 20)
    grouped = _aggregate_jornadas(
        [
            row(fecha, 1, "FORM-A", 8351, 8359),
            row(fecha, 2, "FORM-B", 8359, 8367),
        ],
        (0,),
    )

    assert len(grouped) == 2
    assert sum(item["horas"] for item in grouped.values()) == 16


def test_legacy_sin_form_uuid_conserva_semantica_por_fila():
    fecha = date(2026, 8, 20)
    grouped = _aggregate_jornadas(
        [
            row(fecha, 1, None, 8351, 8359),
            row(fecha, 2, None, 8351, 8359),
        ],
        (0,),
    )

    assert len(grouped) == 2
    assert sum(item["horas"] for item in grouped.values()) == 16


def test_cabecera_no_operativa_tambien_se_deduplica_en_eficiencia():
    fecha = date(2026, 8, 20)
    grouped = _aggregate_jornadas(
        [
            row(fecha, 1, "FORM-A", 8351, 8359, 2),
            row(fecha, 2, "FORM-A", 8351, 8359, 2),
        ],
        (0,),
    )

    values = list(grouped.values())
    assert values[0]["horas"] == 8
    assert values[0]["hrs_no_op"] == 2
