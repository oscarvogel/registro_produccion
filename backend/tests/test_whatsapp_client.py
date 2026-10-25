"""Tests del cliente de la gateway de WhatsApp (issue #206).

El contrato de la gateway (vogel_whatsapp_api docs/API_V1.md)::

    POST {base}/api/v1/instances/{instancia}/messages   header: x-api-key
    202 -> {"success": true, "data": {"messageId": "...", "status": "queued"}}

Lo que hay que cuidar:
- el 202 es "encolado", no entregado;
- el teléfono va solo dígitos, internacional;
- un fallo de la gateway NO puede tumbar el alta de un parte.
"""
from __future__ import annotations

import httpx
import pytest

from app.core import whatsapp
from app.core.config import settings


class _Respuesta:
    def __init__(self, status_code=202, payload=None, texto=""):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = texto or ""

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


@pytest.fixture(autouse=True)
def whatsapp_configurado(monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(settings, "WHATSAPP_INSTANCE", "instancia-de-prueba")
    monkeypatch.setattr(settings, "WHATSAPP_BASE_URL", "https://gateway.example")
    monkeypatch.setattr(settings, "WHATSAPP_SOURCE_APP", "registro-produccion")


def test_normaliza_un_telefono_con_formato_local():
    assert whatsapp.normalizar_telefono("+54 9 3743 51-2000") == "5493743512000"
    assert whatsapp.normalizar_telefono("(03743) 51-2000") == "03743512000"
    assert whatsapp.normalizar_telefono("5493743512000") == "5493743512000"


def test_un_telefono_invalido_no_se_normaliza():
    assert whatsapp.normalizar_telefono("") is None
    assert whatsapp.normalizar_telefono(None) is None
    assert whatsapp.normalizar_telefono("123") is None
    # 17 dígitos: fuera del rango internacional que acepta la gateway.
    assert whatsapp.normalizar_telefono("12345678901234567") is None


def test_envia_el_texto_y_devuelve_el_message_id(monkeypatch):
    capturados = {}

    def fake_post(url, json=None, headers=None, timeout=None):
        capturados["url"] = url
        capturados["json"] = json
        capturados["headers"] = headers
        capturados["timeout"] = timeout
        return _Respuesta(
            202,
            {"success": True, "data": {"messageId": "msg-1", "status": "queued"}},
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    resultado = whatsapp.enviar_mensaje(
        telefono="5493743512000",
        mensaje="Hay una foto para validar.",
        external_ref="registro:42",
        actor_name="Registro Produccion",
    )

    assert resultado.ok is True
    assert resultado.encolado is True
    assert resultado.message_id == "msg-1"
    assert capturados["url"] == (
        "https://gateway.example/api/v1/instances/instancia-de-prueba/messages"
    )
    assert capturados["headers"]["x-api-key"] == "clave-de-prueba"
    assert capturados["json"]["phone"] == "5493743512000"
    assert capturados["json"]["message"] == "Hay una foto para validar."
    assert capturados["json"]["externalRef"] == "registro:42"
    assert capturados["json"]["sourceApp"] == "registro-produccion"


def test_sin_api_key_no_manda_nada(monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_API_KEY", "")
    called = {"ok": False}

    def fake_post(*_args, **_kwargs):
        called["ok"] = True
        return _Respuesta()

    monkeypatch.setattr(httpx, "post", fake_post)

    resultado = whatsapp.enviar_mensaje(telefono="5493743512000", mensaje="hola")

    assert resultado.ok is False
    assert "WHATSAPP_API_KEY" in resultado.error
    assert called["ok"] is False


def test_sin_instancia_no_manda_nada(monkeypatch):
    monkeypatch.setattr(settings, "WHATSAPP_INSTANCE", "")
    resultado = whatsapp.enviar_mensaje(telefono="5493743512000", mensaje="hola")
    assert resultado.ok is False
    assert "WHATSAPP_INSTANCE" in resultado.error


def test_un_telefono_invalido_no_manda_nada(monkeypatch):
    called = {"ok": False}

    def fake_post(*_args, **_kwargs):
        called["ok"] = True
        return _Respuesta()

    monkeypatch.setattr(httpx, "post", fake_post)

    resultado = whatsapp.enviar_mensaje(telefono="123", mensaje="hola")

    assert resultado.ok is False
    assert called["ok"] is False


def test_un_error_de_red_no_propaga_la_excepcion(monkeypatch):
    def fake_post(*_args, **_kwargs):
        raise httpx.ConnectError("no hay red")

    monkeypatch.setattr(httpx, "post", fake_post)

    resultado = whatsapp.enviar_mensaje(telefono="5493743512000", mensaje="hola")

    assert resultado.ok is False
    assert "ConnectError" in resultado.error


def test_un_error_de_la_gateway_no_propaga_la_excepcion(monkeypatch):
    def fake_post(*_args, **_kwargs):
        return _Respuesta(403, texto="forbidden: la instancia es de otra empresa")

    monkeypatch.setattr(httpx, "post", fake_post)

    resultado = whatsapp.enviar_mensaje(telefono="5493743512000", mensaje="hola")

    assert resultado.ok is False
    assert "403" in resultado.error


def test_una_respuesta_sin_json_no_rompe(monkeypatch):
    def fake_post(*_args, **_kwargs):
        return _Respuesta(202, payload=ValueError("no es json"))

    monkeypatch.setattr(httpx, "post", fake_post)

    resultado = whatsapp.enviar_mensaje(telefono="5493743512000", mensaje="hola")

    assert resultado.ok is True
    assert resultado.message_id is None
