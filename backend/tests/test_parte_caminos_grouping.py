from datetime import date
from types import SimpleNamespace

from app.api.routes.parte_caminos import _group_operator_rows


def _row(row_id, form_uuid, operacion, *, km=0, disposicion=0, remolque=0, combustible=80):
    return SimpleNamespace(
        id=row_id,
        form_uuid=form_uuid,
        fecha=date(2026, 8, 14),
        operacion=operacion,
        equipo="Motoniveladora 1",
        combustible=combustible,
        tn_despachadas=0,
        m3=0,
        has=0,
        carros=0,
        plantas=0,
        km_carreteo=0,
        km_perfilado=km,
        hr_disposicion=disposicion,
        hr_remolque=remolque,
        mtrs_recorridos=0,
        hr_inicio=1200,
        hr_fin=1210,
    )


def test_group_operator_rows_collapses_siblings_and_sums_process_metrics_once():
    rows = [
        _row(10, "parte-1", "PERFILADO", km=12.5),
        _row(11, "parte-1", "DISPOSICION", disposicion=2),
        _row(12, "parte-1", "REMOLQUE", remolque=1.5),
    ]

    result = _group_operator_rows(rows)

    assert result.child_ids == [10, 11, 12]
    assert len(result.registros) == 1
    item = result.registros[0]
    assert item.id == 10
    assert item.procesos_count == 3
    assert item.operacion == "Caminos — 3 procesos"
    assert item.km_perfilado == 12.5
    assert item.hr_disposicion == 2
    assert item.hr_remolque == 1.5
    assert item.combustible == 80


def test_group_operator_rows_keeps_legacy_caminos_row_as_single_record():
    result = _group_operator_rows([
        _row(20, "", "PERFILADO", km=3, combustible=0),
    ])

    assert result.child_ids == [20]
    assert len(result.registros) == 1
    assert result.registros[0].procesos_count == 1
    assert result.registros[0].form_uuid == ""
    assert result.registros[0].operacion == "PERFILADO"
