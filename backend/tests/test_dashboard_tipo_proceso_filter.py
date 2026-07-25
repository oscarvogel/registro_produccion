"""Tests para el fix del filtro tipo_proceso en el dashboard.

Bug original: ``_apply_process_filter`` con ``mode="tipo"`` filtraba por
``TableroProduccion.codigo_tabla``, pero el importador de Kobo deja los
registros con ``codigo_tabla`` igual al id de submission de Kobo (no al id
de tipo_de_proceso). Resultado: cualquier selección de tipo de proceso en la
UI del dashboard mostraba 0 producción.

Fix: usar ``TableroProduccion.tipo_proceso_id`` (columna FK agregada via
migración SQL).
"""
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base

from app.api.routes.dashboard import _apply_process_filter
from app.models.produccion import TableroProduccion


def test_tablero_produccion_tiene_columna_tipo_proceso_id():
    """El modelo debe declarar la columna ``tipo_proceso_id`` para que el ORM
    la conozca y no rompa al correr queries que la referencien."""
    assert hasattr(TableroProduccion, "tipo_proceso_id"), (
        "TableroProduccion debe tener el atributo tipo_proceso_id"
    )
    col = TableroProduccion.__table__.columns.get("tipo_proceso_id")
    assert col is not None, "La columna tipo_proceso_id no existe en la tabla"
    assert col.nullable is True, "tipo_proceso_id debe ser nullable"


def _make_filter_capture():
    """Devuelve (fake_base, captured_filters) donde ``fake_base.filter`` guarda
    cada filter que se le pasa y devuelve el mismo fake_base, para poder
    inspeccionar los filtros que _apply_process_filter aplicó.
    """
    captured = []

    class FakeBase:
        def filter(self, *args, **kwargs):
            captured.append(("filter", args, kwargs))
            return self

    return FakeBase(), captured


def test_apply_process_filter_tipo_filtra_por_tipo_proceso_id():
    """El modo ``tipo`` debe usar ``tipo_proceso_id``, no ``codigo_tabla``."""
    base, captured = _make_filter_capture()

    _apply_process_filter(base, {"mode": "tipo", "ids": [3, 4]})

    assert len(captured) == 1, "Debería aplicarse exactamente un filtro"
    arg = captured[0][1][0]
    rendered = str(arg)
    assert "tipo_proceso_id" in rendered, (
        f"El filtro debe mencionar tipo_proceso_id. Render: {rendered!r}"
    )
    assert "codigo_tabla" not in rendered, (
        f"El filtro NO debe mencionar codigo_tabla. Render: {rendered!r}"
    )
    assert "IN" in rendered.upper() or "in_(" in rendered, (
        f"El filtro debe ser un IN con los ids [3, 4]. Render: {rendered!r}"
    )


def test_apply_process_filter_operacion_no_cambia():
    """El modo ``operacion`` debe seguir funcionando como antes (no se toca)."""
    base, captured = _make_filter_capture()

    _apply_process_filter(base, {"mode": "operacion", "name": "PROCESO"})

    assert len(captured) == 1
    arg = captured[0][1][0]
    rendered = str(arg)
    assert "tipo_proceso_id" not in rendered, (
        f"El modo operacion no debe usar tipo_proceso_id. Render: {rendered!r}"
    )
    assert "operacion" in rendered, (
        f"El modo operacion debe seguir usando operacion. Render: {rendered!r}"
    )


def test_apply_process_filter_sin_filter_no_aplica_nada():
    """Sin process_filter no se debe aplicar ningún filtro."""
    base, captured = _make_filter_capture()

    _apply_process_filter(base, None)

    assert captured == [], (
        "Sin process_filter no se debe llamar a .filter() en el base"
    )
