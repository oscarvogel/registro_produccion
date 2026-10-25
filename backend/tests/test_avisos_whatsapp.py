"""Aviso por WhatsApp al encargado (issue #206).

Cubre:
- quién recibe el aviso: los ``encargado = 1`` de la unidad del registro,
- qué dice el mensaje,
- que el aviso NUNCA bloquea el alta del parte (sin WhatsApp, sin teléfono,
  sin encargados o con la gateway caída),
- que el aviso sale cuando se crea el parte con evidencia y también cuando el
  operador sube una foto de corrección a un parte ya creado (D-F).
"""
from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  (registra todas las tablas en Base.metadata)
from app.core import avisos
from app.core.config import settings
from app.core.database import Base
from app.models.personal import Personal
from app.models.personal_unidad_negocio import PersonalUnidadNegocio

UN_DEMO = 900001


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    sesion = Session()
    try:
        yield sesion
    finally:
        sesion.close()
        engine.dispose()


def _personal(sesion, id_personal, nombre, telefono, encargado=0, un_id=UN_DEMO, activo=1):
    fila = Personal(
        idPersonal=id_personal,
        Nombre=nombre,
        telefono=telefono,
        encargado=encargado,
        activo=activo,
        unidad_negocio=un_id,
    )
    sesion.add(fila)
    sesion.flush()
    sesion.add(PersonalUnidadNegocio(idPersonal=id_personal, idUnidadNegocio=un_id))
    sesion.commit()
    return fila


def _registro(id_registro=900201, un_id=UN_DEMO):
    return SimpleNamespace(
        id=id_registro,
        UN="Unidad Negocio Demo Forestal",
        operacion="PROCESO",
        fecha=date(2026, 10, 20),
        operador="Operador Demo 01",
        cod_operador=99000011,
        cod_un=un_id,
    )


def _evidencia(tipo="procesador"):
    return SimpleNamespace(id=77, tipo=tipo, estado=0, incluye_horometro=1)


@pytest.fixture()
def whatsapp_lista(monkeypatch):
    """Activa WhatsApp y captura los envíos."""
    monkeypatch.setattr(settings, "WHATSAPP_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "WHATSAPP_INSTANCE", "instancia-de-prueba")
    enviados = []

    def fake_enviar(**kwargs):
        enviados.append(kwargs)
        return SimpleNamespace(ok=True, estado="queued", message_id="msg-1", error=None)

    monkeypatch.setattr(avisos, "enviar_mensaje", fake_enviar)
    return enviados


# ─── Quién recibe el aviso ────────────────────────────────────────────────
def test_encargados_de_la_unidad_son_los_de_la_pivot(db):
    _personal(db, 1, "ENCARGADO UNO", "5493743512000", encargado=1)
    _personal(db, 2, "OPERADOR", "5493743512001", encargado=0)
    _personal(db, 3, "ENCARGADO DE OTRA UNIDAD", "5493743512002", encargado=1, un_id=900002)
    _personal(db, 4, "ENCARGADO INACTIVO", "5493743512003", encargado=1, activo=0)

    encontrados = avisos.encargados_de_la_unidad(db, UN_DEMO)

    assert [p.idPersonal for p in encontrados] == [1]


def test_sin_unidad_no_hay_encargados(db):
    _personal(db, 1, "ENCARGADO UNO", "5493743512000", encargado=1)
    assert avisos.encargados_de_la_unidad(db, None) == []


# ─── El mensaje ───────────────────────────────────────────────────────────
def test_el_mensaje_dice_que_registro_es_y_que_hay_que_validar():
    texto = avisos.mensaje_evidencia_pendiente(_registro(), [_evidencia()])

    assert "hay evidencia para validar" in texto
    assert "#900201" in texto
    assert "PROCESO" in texto
    assert "Unidad Negocio Demo Forestal" in texto
    assert "Operador Demo 01" in texto
    assert "pantalla del procesador" in texto
    assert "Esperando verificación" in texto


def test_el_mensaje_no_inventa_datos_que_no_estan():
    registro = SimpleNamespace(id=1, UN="", operacion="", fecha=None, operador="", cod_un=1)
    texto = avisos.mensaje_evidencia_pendiente(registro, [_evidencia("horometro")])
    assert "horómetro" in texto
    assert "Unidad:" not in texto
    assert "Operador:" not in texto


# ─── El aviso ─────────────────────────────────────────────────────────────
def test_avisa_a_los_encargados_con_telefono(db, whatsapp_lista):
    _personal(db, 1, "ENCARGADO UNO", "+54 9 3743 51-2000", encargado=1)
    _personal(db, 2, "OPERADOR", "5493743512001", encargado=0)

    resultados = avisos.avisar_evidencia_pendiente(db, _registro(), [_evidencia()])

    assert len(resultados) == 1
    assert len(whatsapp_lista) == 1
    enviado = whatsapp_lista[0]
    assert enviado["telefono"] == "5493743512000"
    assert enviado["external_ref"] == "registro-produccion:registro:900201"
    assert "hay evidencia para validar" in enviado["mensaje"]


def test_el_actor_del_aviso_es_el_operador_que_cargo(db, whatsapp_lista):
    """El actor de la auditoría es quien origina el aviso, no el destinatario."""
    _personal(db, 1, "ENCARGADO UNO", "5493743512000", encargado=1)

    avisos.avisar_evidencia_pendiente(db, _registro(), [_evidencia()])

    enviado = whatsapp_lista[0]
    assert enviado["actor_id"] == "99000011"
    assert enviado["actor_name"] == "Operador Demo 01"


def test_el_encargado_sin_telefono_no_recibe_nada(db, whatsapp_lista):
    _personal(db, 1, "ENCARGADO SIN TELEFONO", "", encargado=1)

    resultados = avisos.avisar_evidencia_pendiente(db, _registro(), [_evidencia()])

    assert resultados == []
    assert whatsapp_lista == []


def test_sin_evidencia_no_se_avisa(db, whatsapp_lista):
    _personal(db, 1, "ENCARGADO UNO", "5493743512000", encargado=1)
    assert avisos.avisar_evidencia_pendiente(db, _registro(), []) == []
    assert whatsapp_lista == []


def test_sin_encargados_no_se_avisa(db, whatsapp_lista):
    _personal(db, 2, "OPERADOR", "5493743512001", encargado=0)
    assert avisos.avisar_evidencia_pendiente(db, _registro(), [_evidencia()]) == []
    assert whatsapp_lista == []


def test_sin_whatsapp_configurado_no_se_avisa(db, monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_API_KEY", "")
    _personal(db, 1, "ENCARGADO UNO", "5493743512000", encargado=1)

    assert avisos.avisar_evidencia_pendiente(db, _registro(), [_evidencia()]) == []


def test_un_fallo_de_la_gateway_no_propaga_la_excepcion(db, monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_API_KEY", "clave")
    monkeypatch.setattr(settings, "WHATSAPP_INSTANCE", "instancia")
    _personal(db, 1, "ENCARGADO UNO", "5493743512000", encargado=1)

    def fake_enviar(**_kwargs):
        return SimpleNamespace(ok=False, estado="", message_id=None, error="HTTP 403: forbidden")

    monkeypatch.setattr(avisos, "enviar_mensaje", fake_enviar)

    resultados = avisos.avisar_evidencia_pendiente(db, _registro(), [_evidencia()])

    assert len(resultados) == 1
    assert resultados[0].ok is False
