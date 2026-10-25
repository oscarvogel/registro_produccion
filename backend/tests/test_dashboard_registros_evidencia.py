"""Evidencia fotografica en el listado del dashboard (issue #204).

Cubre:
- el filtro por estado de evidencia (``pendiente`` / ``verificada`` /
  ``rechazada`` / ``sin_evidencia``) en ``/api/dashboard/registros``,
- el resumen por fila (total, pendientes, rechazadas) que usa el frontend para
  marcar los registros observados,
- el detalle del registro con el mismo resumen,
- que un filtro desconocido se rechaza con 422.

Las pruebas corren contra SQLite (no MySQL).
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  (registra todas las tablas en Base.metadata)
from app.api.deps import get_current_admin_or_encargado, get_current_user, get_db
from app.core.database import Base
from app.core.evidencia import (
    ESTADO_PENDIENTE,
    ESTADO_RECHAZADA,
    ESTADO_REEMPLAZADA,
    ESTADO_VERIFICADA,
)
from app.main import app
from app.models.evidencia import ProduccionEvidencia
from app.models.produccion import TableroProduccion

RUTA_LISTADO = "/api/dashboard/registros"


@pytest.fixture()
def entorno(tmp_path):
    """Base SQLite con registros y evidencia, y un usuario admin."""
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'dashboard.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    admin = SimpleNamespace(idPersonal=1, Nombre="ADMIN UNO", is_admin=1, encargado=0)

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_admin_or_encargado] = lambda: admin
    app.dependency_overrides[get_current_user] = lambda: admin
    try:
        yield SimpleNamespace(sessionmaker=Session, cliente=TestClient(app))
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _registro(sessionmaker, registro_id, fecha="2026-10-20"):
    db = sessionmaker()
    try:
        db.add(
            TableroProduccion(
                id=registro_id,
                UN="UNIDAD DEMO",
                operacion="PROCESO",
                fecha=date.fromisoformat(fecha),
                cod_un=900001,
                cod_operador=7,
                form_uuid=f"uuid-{registro_id}",
                # Columnas que en MySQL son NOT NULL con default y en SQLite
                # quedan en NULL: el detalle las expone como int/str.
                espada=0,
                puntera=0,
                cadena=0,
                pinon=0,
                origen="",
                tabla="",
            )
        )
        db.commit()
    finally:
        db.close()


def _evidencia(sessionmaker, registro_id, estado, tipo="procesador", evidencia_id=None):
    db = sessionmaker()
    try:
        fila = ProduccionEvidencia(
            id=evidencia_id,
            registro_id=registro_id,
            form_uuid=f"uuid-{registro_id}",
            tipo=tipo,
            incluye_horometro=0,
            archivo="2026/10/foto.jpg",
            mime="image/jpeg",
            tamano=100,
            hash_sha256=f"hash-{registro_id}-{estado}-{tipo}",
            estado=estado,
        )
        db.add(fila)
        db.commit()
        return fila.id
    finally:
        db.close()


def test_el_listado_trae_el_resumen_de_evidencia(entorno):
    _registro(entorno.sessionmaker, 1)
    _registro(entorno.sessionmaker, 2)
    _evidencia(entorno.sessionmaker, 1, ESTADO_PENDIENTE)
    _evidencia(entorno.sessionmaker, 1, ESTADO_RECHAZADA, tipo="horometro")
    _evidencia(entorno.sessionmaker, 2, ESTADO_VERIFICADA)

    respuesta = entorno.cliente.get(RUTA_LISTADO, params={"un_id": 900001})
    assert respuesta.status_code == 200
    filas = {item["id"]: item for item in respuesta.json()["items"]}

    assert filas[1]["evidencias_total"] == 2
    assert filas[1]["evidencias_pendientes"] == 1
    assert filas[1]["evidencias_rechazadas"] == 1
    assert filas[2]["evidencias_total"] == 1
    assert filas[2]["evidencias_pendientes"] == 0
    assert filas[2]["evidencias_rechazadas"] == 0


def test_filtra_por_evidencia_pendiente(entorno):
    _registro(entorno.sessionmaker, 1)
    _registro(entorno.sessionmaker, 2)
    _evidencia(entorno.sessionmaker, 1, ESTADO_PENDIENTE)
    _evidencia(entorno.sessionmaker, 2, ESTADO_VERIFICADA)

    respuesta = entorno.cliente.get(
        RUTA_LISTADO, params={"un_id": 900001, "evidencia": "pendiente"}
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert [item["id"] for item in datos["items"]] == [1]
    assert datos["total"] == 1


def test_filtra_por_evidencia_rechazada(entorno):
    _registro(entorno.sessionmaker, 1)
    _registro(entorno.sessionmaker, 2)
    _evidencia(entorno.sessionmaker, 1, ESTADO_RECHAZADA)
    _evidencia(entorno.sessionmaker, 2, ESTADO_PENDIENTE)

    respuesta = entorno.cliente.get(
        RUTA_LISTADO, params={"un_id": 900001, "evidencia": "rechazada"}
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert [item["id"] for item in datos["items"]] == [1]
    assert datos["total"] == 1


def test_filtra_por_evidencia_sin_evidencia(entorno):
    _registro(entorno.sessionmaker, 1)
    _registro(entorno.sessionmaker, 2)
    _evidencia(entorno.sessionmaker, 1, ESTADO_PENDIENTE)

    respuesta = entorno.cliente.get(
        RUTA_LISTADO, params={"un_id": 900001, "evidencia": "sin_evidencia"}
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert [item["id"] for item in datos["items"]] == [2]
    assert datos["total"] == 1


def test_la_evidencia_reemplazada_no_cuenta_como_pendiente(entorno):
    """Una foto reemplazada es historial: no es pendiente ni rechazada (D-F)."""
    _registro(entorno.sessionmaker, 1)
    _evidencia(entorno.sessionmaker, 1, ESTADO_REEMPLAZADA)

    pendiente = entorno.cliente.get(
        RUTA_LISTADO, params={"un_id": 900001, "evidencia": "pendiente"}
    )
    assert pendiente.json()["items"] == []

    rechazada = entorno.cliente.get(
        RUTA_LISTADO, params={"un_id": 900001, "evidencia": "rechazada"}
    )
    assert rechazada.json()["items"] == []


def test_un_filtro_desconocido_se_rechaza(entorno):
    _registro(entorno.sessionmaker, 1)

    respuesta = entorno.cliente.get(
        RUTA_LISTADO, params={"un_id": 900001, "evidencia": "inventado"}
    )
    assert respuesta.status_code == 422


def test_el_detalle_del_registro_trae_el_resumen(entorno):
    _registro(entorno.sessionmaker, 1)
    _evidencia(entorno.sessionmaker, 1, ESTADO_RECHAZADA)

    respuesta = entorno.cliente.get(f"{RUTA_LISTADO}/1")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["evidencias_total"] == 1
    assert datos["evidencias_rechazadas"] == 1
    assert datos["evidencias_pendientes"] == 0


@contextmanager
def _noop(*_args, **_kwargs):
    yield
