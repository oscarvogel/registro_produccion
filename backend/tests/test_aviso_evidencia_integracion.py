"""Disparo del aviso por WhatsApp (issue #206).

El aviso tiene que salir en los dos momentos en que una foto queda esperando
validacion:

1. cuando se crea el parte con evidencia,
2. cuando el operador sube una foto de correccion a un parte ya creado (D-F).

Y en ningun caso puede tumbar el alta: si el aviso falla, el parte se guarda.
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
from app.api.deps import get_current_user, get_db
from app.api.routes import evidencia as evidencia_routes
from app.api.routes import produccion as produccion_routes
from app.core.config import settings
from app.core.database import Base
from app.main import app
from app.models.personal import Personal
from app.models.produccion import TableroProduccion
from app.models.tipo_proceso import TipoDeProceso

JPEG_BINARIO = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"


@pytest.fixture()
def entorno(tmp_path, monkeypatch):
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'aviso.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(settings, "EVIDENCIA_STORAGE_DIR", str(tmp_path / "media"))
    monkeypatch.setattr(settings, "EVIDENCIA_MAX_UPLOAD_MB", 10)

    @contextmanager
    def no_lock(*_args, **_kwargs):
        yield

    monkeypatch.setattr(evidencia_routes, "form_submission_lock", no_lock)
    monkeypatch.setattr(produccion_routes, "_form_submission_lock", no_lock)

    usuarios = {
        "actual": SimpleNamespace(
            idPersonal=7, Nombre="OPERADOR UNO", is_admin=0, encargado=0
        )
    }

    def override_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: usuarios["actual"]
    try:
        yield SimpleNamespace(
            sessionmaker=Session,
            usuarios=usuarios,
            cliente=TestClient(app),
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


@pytest.fixture()
def avisos(entorno, monkeypatch):
    """Captura los avisos disparados por los endpoints."""
    llamadas = []

    def fake_avisar(db, registro, evidencias):
        # Se copian los ids en el momento del aviso: al terminar el request la
        # sesion se cierra y el objeto queda desconectado.
        llamadas.append(
            {
                "registro_id": registro.id,
                "evidencias": [fila.id for fila in (evidencias or [])],
            }
        )
        return []

    monkeypatch.setattr(produccion_routes, "avisar_evidencia_pendiente", fake_avisar)
    monkeypatch.setattr(evidencia_routes, "avisar_evidencia_pendiente", fake_avisar)
    return llamadas


def _tipo_proceso(sessionmaker, nombre="PROCESO", foto_procesador=True):
    with sessionmaker() as db:
        fila = TipoDeProceso(
            nombre=nombre,
            campos="m3,plantas",
            requiere_acta=False,
            requiere_predio=False,
            requiere_rodal=False,
            requiere_horometro=True,
            requiere_foto_horometro=False,
            requiere_foto_procesador=foto_procesador,
            activo=1,
        )
        db.add(fila)
        db.commit()
        db.refresh(fila)
        return fila.id


def _encargado(sessionmaker, id_personal=900002, telefono="5493743512000"):
    with sessionmaker() as db:
        db.add(
            Personal(
                idPersonal=id_personal,
                Nombre="ENCARGADO UNO",
                telefono=telefono,
                encargado=1,
                activo=1,
                unidad_negocio=1,
            )
        )
        db.commit()


def _subir(cliente, form_uuid="uuid-1", tipo="procesador"):
    return cliente.post(
        "/api/produccion/evidencias",
        data={
            "form_uuid": form_uuid,
            "tipo": tipo,
            "incluye_horometro": "true",
        },
        files={"archivo": ("foto.jpg", JPEG_BINARIO, "image/jpeg")},
    )


def _payload(codigo_tabla, form_uuid="uuid-1", evidencias=None, **extra):
    datos = {
        "fecha": "2026-10-24",
        "form_uuid": form_uuid,
        "tabla": "tipo_de_proceso",
        "codigo_tabla": codigo_tabla,
        "operacion": "PROCESO",
        "cod_operador": 7,
    }
    if evidencias is not None:
        datos["evidencias"] = evidencias
    datos.update(extra)
    return datos


def test_al_crear_el_parte_con_evidencia_se_avisa(entorno, avisos):
    _encargado(entorno.sessionmaker)
    tipo_id = _tipo_proceso(entorno.sessionmaker)
    subida = _subir(entorno.cliente).json()

    respuesta = entorno.cliente.post(
        "/api/produccion/",
        json=_payload(tipo_id, evidencias=[subida["id"]]),
    )

    assert respuesta.status_code == 201, respuesta.text
    assert len(avisos) == 1
    aviso = avisos[0]
    assert aviso["registro_id"] == respuesta.json()["id"]
    assert aviso["evidencias"] == [subida["id"]]


def test_al_crear_el_parte_sin_evidencia_no_se_avisa(entorno, avisos):
    tipo_id = _tipo_proceso(entorno.sessionmaker, foto_procesador=False)

    respuesta = entorno.cliente.post("/api/produccion/", json=_payload(tipo_id))

    assert respuesta.status_code == 201, respuesta.text
    assert avisos == []


def test_al_subir_la_foto_de_correccion_a_un_parte_existente_se_avisa(entorno, avisos):
    with entorno.sessionmaker() as db:
        db.add(
            TableroProduccion(
                id=900,
                form_uuid="uuid-9",
                cod_operador=7,
                cod_un=1,
                fecha=date(2026, 10, 24),
                hr_inicio=0,
                hr_fin=0,
            )
        )
        db.commit()

    respuesta = entorno.cliente.post(
        "/api/produccion/registros/900/evidencias",
        data={"tipo": "procesador", "incluye_horometro": "true"},
        files={"archivo": ("foto.jpg", JPEG_BINARIO, "image/jpeg")},
    )

    assert respuesta.status_code == 201, respuesta.text
    assert len(avisos) == 1
    assert avisos[0]["registro_id"] == 900


def test_un_aviso_que_falla_no_rompe_el_alta(entorno, monkeypatch):
    tipo_id = _tipo_proceso(entorno.sessionmaker)
    subida = _subir(entorno.cliente).json()

    def avisar_que_falla(*_args, **_kwargs):
        raise RuntimeError("la gateway exploto")

    monkeypatch.setattr(
        produccion_routes, "avisar_evidencia_pendiente", avisar_que_falla
    )

    respuesta = entorno.cliente.post(
        "/api/produccion/",
        json=_payload(tipo_id, evidencias=[subida["id"]]),
    )

    assert respuesta.status_code == 201, respuesta.text
