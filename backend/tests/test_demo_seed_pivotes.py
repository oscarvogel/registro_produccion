"""Tests de regresion para las pivotes que popular el seed demo.

Issue #97: el seed no estaba creando las filas en
``personal_unidad_negocio`` ni en ``unidadnegocio_tipo_proceso``,
y los endpoints de catalogo filtran por esas pivotes, asi que
devolvian listas vacias en una instancia demo recien seeded.

Con el fix, el dataset debe incluir esas dos listas con las filas
que esperan los endpoints ``/operadores`` y ``/tipo-proceso``.
"""
from datetime import date

from app.seed import demo_data


def test_demo_dataset_includes_personal_unidad_negocio():
    dataset = demo_data.build_demo_dataset(record_count=5, today=date(2026, 6, 17))

    assert hasattr(dataset, "personal_unidad_negocio")
    assert len(dataset.personal_unidad_negocio) > 0

    # Cada fila mapea un personal demo al UN demo.
    for row in dataset.personal_unidad_negocio:
        assert "idPersonal" in row
        assert "idUnidadNegocio" in row
        assert row["idUnidadNegocio"] == dataset.unidades_negocio[0]["idUnidadNegocio"]


def test_demo_dataset_includes_unidadnegocio_tipo_proceso():
    dataset = demo_data.build_demo_dataset(record_count=5, today=date(2026, 6, 17))

    assert hasattr(dataset, "unidadnegocio_tipo_proceso")
    assert len(dataset.unidadnegocio_tipo_proceso) > 0

    un_demo = dataset.unidades_negocio[0]["idUnidadNegocio"]
    tipo_proceso_ids = {row["id"] for row in dataset.tipos_proceso}

    for row in dataset.unidadnegocio_tipo_proceso:
        assert row["un_id"] == un_demo
        assert row["tipo_proceso_id"] in tipo_proceso_ids


def test_pivotes_cover_all_personal_and_tipo_proceso():
    """Las pivotes deben cubrir todos los personales y tipos demo del seed."""
    dataset = demo_data.build_demo_dataset(record_count=5, today=date(2026, 6, 17))

    un_demo = dataset.unidades_negocio[0]["idUnidadNegocio"]
    personal_un_ids = {row["unidad_negocio"] for row in dataset.personal}
    personal_pivot_ids = {row["idPersonal"] for row in dataset.personal_unidad_negocio}
    personal_with_un = {row["idPersonal"] for row in dataset.personal if row.get("unidad_negocio") == un_demo}

    # La pivot incluye al menos a todos los personales con el UN demo.
    assert personal_with_un <= personal_pivot_ids

    # Y la pivot de tipos cubre todos los tipos activos.
    tipo_activo_ids = {row["id"] for row in dataset.tipos_proceso if row.get("activo") == 1}
    pivot_tipo_ids = {row["tipo_proceso_id"] for row in dataset.unidadnegocio_tipo_proceso}
    assert tipo_activo_ids <= pivot_tipo_ids
