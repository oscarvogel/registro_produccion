from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes import produccion
from app.schemas.produccion import TableroProduccionCreate


def _payload(*, cod_un: int = 10, codigo_tabla: int = 20) -> TableroProduccionCreate:
    return TableroProduccionCreate(
        fecha=date(2026, 8, 10),
        cod_un=cod_un,
        codigo_tabla=codigo_tabla,
    )


def test_rechaza_proceso_no_habilitado_para_la_un_para_cualquier_usuario(monkeypatch):
    data = _payload()
    user = SimpleNamespace(encargado=0)

    monkeypatch.setattr(produccion, "_tipo_proceso_habilitado", lambda db, proceso, un: False)
    monkeypatch.setattr(produccion, "_restricted_unidad_ids", lambda user, db: None)

    with pytest.raises(HTTPException) as exc:
        produccion._validate_restricted_payload(data, user, object())

    assert exc.value.status_code == 422
    assert "no esta habilitado" in exc.value.detail
    assert "unidad de negocio" in exc.value.detail


def test_acepta_proceso_habilitado_para_usuario_no_restringido(monkeypatch):
    data = _payload()
    user = SimpleNamespace(encargado=0)

    monkeypatch.setattr(produccion, "_tipo_proceso_habilitado", lambda db, proceso, un: True)
    monkeypatch.setattr(produccion, "_restricted_unidad_ids", lambda user, db: None)

    produccion._validate_restricted_payload(data, user, object())


def test_validacion_global_ocurre_antes_de_las_restricciones_full_tree(monkeypatch):
    data = _payload(cod_un=3, codigo_tabla=99)
    user = SimpleNamespace(encargado=1)
    restricted_called = False

    def _restricted(user, db):
        nonlocal restricted_called
        restricted_called = True
        return [3]

    monkeypatch.setattr(produccion, "_tipo_proceso_habilitado", lambda db, proceso, un: False)
    monkeypatch.setattr(produccion, "_restricted_unidad_ids", _restricted)

    with pytest.raises(HTTPException) as exc:
        produccion._validate_restricted_payload(data, user, object())

    assert exc.value.status_code == 422
    assert restricted_called is False
