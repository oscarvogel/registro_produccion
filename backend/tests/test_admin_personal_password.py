from datetime import date

import pytest
from fastapi import HTTPException

from app.api.routes import admin_legacy
from app.core.security import PASSWORD_TOO_LONG_MESSAGE
from app.schemas.admin import DashboardResumenItem, DashboardUnidadNegocioItem


def test_hash_personal_password_rejects_long_password_with_400():
    with pytest.raises(HTTPException) as exc_info:
        admin_legacy._hash_personal_password("a" * 73)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == PASSWORD_TOO_LONG_MESSAGE
    assert "bcrypt" not in exc_info.value.detail.lower()
    assert "passlib" not in exc_info.value.detail.lower()


def test_hash_personal_password_keeps_valid_password_flow(monkeypatch):
    monkeypatch.setattr(admin_legacy, "get_password_hash", lambda password: f"hashed:{password}")

    assert admin_legacy._hash_personal_password("clave-valida") == "hashed:clave-valida"


def test_dashboard_unit_sort_key_orders_by_latest_activity_first():
    def unit(name, last_activity):
        return DashboardUnidadNegocioItem(
            id=1,
            nombre=name,
            prefijo=name[:3],
            resumen=DashboardResumenItem(
                total_registros=0,
                produccion_total=0,
                tn_despachadas_total=0,
                combustible_total=0,
                operadores_activos=0,
                equipos_activos=0,
                registros_hoy=0,
                ultima_actividad_fecha=last_activity,
            ),
            tipos_proceso=[],
        )

    units = [
        unit("Sin actividad", None),
        unit("Ayer", date(2026, 6, 12)),
        unit("Mas vieja", date(2026, 6, 1)),
    ]

    ordered = sorted(units, key=admin_legacy._dashboard_unit_sort_key)

    assert [item.nombre for item in ordered] == ["Ayer", "Mas vieja", "Sin actividad"]
