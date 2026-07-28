"""Tests de regresion para los catalogos legacy del seed demo.

Issue #101: el seed no creaba tipocomb, panioles ni un lugarcarga con
id=1, y el backend de /produccion/ los usa como FKs hardcodeadas.
El seed debe crear los 3 para que cualquier parte con combustible se
pueda guardar en una instancia demo recien seeded.
"""
from datetime import date

from app.seed import demo_data


def test_demo_dataset_includes_tipocomb():
    dataset = demo_data.build_demo_dataset(record_count=5, today=date(2026, 6, 17))

    assert hasattr(dataset, "tipocomb")
    assert len(dataset.tipocomb) > 0

    for row in dataset.tipocomb:
        assert "idTipoComb" in row
        assert "Detalle" in row
        assert "Unitario" in row
        assert "idArticulo" in row
    # El backend espera idTipoComb=1 (Gasoil por defecto).
    assert any(row["idTipoComb"] == 1 for row in dataset.tipocomb)


def test_demo_dataset_includes_panioles():
    dataset = demo_data.build_demo_dataset(record_count=5, today=date(2026, 6, 17))

    assert hasattr(dataset, "panioles")
    assert len(dataset.panioles) > 0

    for row in dataset.panioles:
        assert "idPaniol" in row
        assert "Nombre" in row
        assert "un" in row
    # El backend espera idPaniol=1.
    assert any(row["idPaniol"] == 1 for row in dataset.panioles)


def test_demo_dataset_includes_lugar_carga_legacy_with_id_1():
    dataset = demo_data.build_demo_dataset(record_count=5, today=date(2026, 6, 17))

    assert hasattr(dataset, "lugares_carga_legacy")
    assert len(dataset.lugares_carga_legacy) > 0

    # El backend fallback usa idLugarCarga=1 cuando el cliente no envia lugar_carga.
    assert any(row["idLugarCarga"] == 1 for row in dataset.lugares_carga_legacy)
