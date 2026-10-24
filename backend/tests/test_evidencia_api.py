"""API de evidencia fotografica (issue #198).

Cubre:
- la subida de la foto (multipart): mime, tamano, idempotencia y escritura
  atomica en disco,
- el servicio de los bytes y los permisos de quien puede verlos,
- el listado de la evidencia de un registro,
- la verificacion por el encargado (R5),
- R2 en el alta del parte: la cobertura se calcula por ROLES (R7) y una foto
  rechazada no cuenta,
- D-F: adjuntar una foto nueva a un registro ya creado.

Las pruebas corren contra SQLite (no MySQL) y con el lock nombrado de MySQL
reemplazado por un no-op: el lock se valida aparte, en la base real.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date
from pathlib import Path
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
from app.core.evidencia import (
    ESTADO_PENDIENTE,
    ESTADO_RECHAZADA,
    ESTADO_REEMPLAZADA,
    ESTADO_VERIFICADA,
    ROL_HOROMETRO,
    ROL_PROCESADOR,
    extension_para_mime,
    guardar_archivo,
    mensaje_faltante,
    roles_de,
    roles_exigidos,
    roles_faltantes,
    ruta_absoluta,
    ruta_relativa,
)
from app.main import app
from app.models.evidencia import ProduccionEvidencia
from app.models.produccion import TableroProduccion
from app.models.tipo_proceso import TipoDeProceso

JPEG_BINARIO = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
PNG_BINARIO = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32

RUTA_UPLOAD = "/api/produccion/evidencias"


@pytest.fixture()
def entorno(tmp_path, monkeypatch):
    """Base SQLite, directorio de evidencia temporal y usuario autenticado."""
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'api.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(settings, "EVIDENCIA_STORAGE_DIR", str(tmp_path / "media"))
    monkeypatch.setattr(settings, "EVIDENCIA_MAX_UPLOAD_MB", 10)

    @contextmanager
    def no_lock(*_args, **_kwargs):
        yield

    # El lock con nombre de MySQL no existe en SQLite.
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
            media=tmp_path / "media",
            cliente=TestClient(app),
        )
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def _subir(cliente, form_uuid="uuid-1", tipo=ROL_PROCESADOR, contenido=JPEG_BINARIO,
           mime="image/jpeg", incluye_horometro=None, nombre="foto.jpg"):
    datos = {"form_uuid": form_uuid, "tipo": tipo}
    if incluye_horometro is not None:
        datos["incluye_horometro"] = "true" if incluye_horometro else "false"
    return cliente.post(
        RUTA_UPLOAD,
        data=datos,
        files={"archivo": (nombre, contenido, mime)},
    )


def _crear_tipo_proceso(sessionmaker, nombre, campos, foto_horometro, foto_procesador):
    with sessionmaker() as db:
        fila = TipoDeProceso(
            nombre=nombre,
            campos=campos,
            requiere_acta=False,
            requiere_predio=False,
            requiere_rodal=False,
            requiere_horometro=True,
            requiere_foto_horometro=foto_horometro,
            requiere_foto_procesador=foto_procesador,
            activo=1,
        )
        db.add(fila)
        db.commit()
        db.refresh(fila)
        return fila.id


def _crear_registro(sessionmaker, form_uuid="uuid-1", cod_operador=7):
    with sessionmaker() as db:
        fila = TableroProduccion(
            id=900,
            form_uuid=form_uuid,
            cod_operador=cod_operador,
            fecha=date(2026, 10, 24),
            hr_inicio=0,
            hr_fin=0,
        )
        db.add(fila)
        db.commit()
        return fila.id


def _payload_produccion(codigo_tabla, form_uuid="uuid-1", evidencias=None, **extra):
    datos = {
        "fecha": "2026-10-24",
        "form_uuid": form_uuid,
        "tabla": "tipo_de_proceso",
        "codigo_tabla": codigo_tabla,
        "operacion": extra.pop("operacion", "PROCESO"),
        "cod_operador": 7,
    }
    if evidencias is not None:
        datos["evidencias"] = evidencias
    datos.update(extra)
    return datos


# ─── Subida de la foto ─────────────────────────────────────────────
def test_upload_creates_the_row_and_writes_the_file(entorno):
    response = _subir(entorno.cliente)

    assert response.status_code == 201
    cuerpo = response.json()
    assert cuerpo["tipo"] == ROL_PROCESADOR
    assert cuerpo["estado"] == ESTADO_PENDIENTE
    assert cuerpo["incluye_horometro"] is False
    assert cuerpo["url"] == f"/api/produccion/evidencias/{cuerpo['id']}/archivo"

    with entorno.sessionmaker() as db:
        fila = db.query(ProduccionEvidencia).filter(
            ProduccionEvidencia.id == cuerpo["id"]
        ).one()
        assert fila.form_uuid == "uuid-1"
        assert fila.hash_sha256
        assert fila.cargado_por == "OPERADOR UNO"
        assert fila.cargado_por_id == 7

    assert (entorno.media / fila.archivo).is_file()


def test_upload_is_idempotent_for_the_same_photo(entorno):
    primera = _subir(entorno.cliente)
    segunda = _subir(entorno.cliente)

    assert primera.status_code == 201
    # Reintento de red: la misma foto no se duplica.
    assert segunda.status_code == 200
    assert segunda.json()["id"] == primera.json()["id"]

    with entorno.sessionmaker() as db:
        assert db.query(ProduccionEvidencia).count() == 1


def test_upload_rejects_a_mime_that_is_not_a_photo(entorno):
    response = _subir(entorno.cliente, mime="application/pdf", contenido=b"%PDF-1.4")

    assert response.status_code == 422
    assert "Formato de foto no permitido" in response.json()["detail"]


def test_upload_rejects_an_empty_file(entorno):
    response = _subir(entorno.cliente, contenido=b"")

    assert response.status_code == 422
    assert "vacia" in response.json()["detail"]


def test_upload_rejects_a_file_over_the_size_limit(entorno, monkeypatch):
    monkeypatch.setattr(settings, "EVIDENCIA_MAX_UPLOAD_MB", 0)

    response = _subir(entorno.cliente)

    assert response.status_code == 422
    assert "tamano maximo" in response.json()["detail"]


def test_upload_rejects_an_unknown_type(entorno):
    response = _subir(entorno.cliente, tipo="perro")

    assert response.status_code == 422
    assert "'procesador' u 'horometro'" in response.json()["detail"]


def test_upload_requires_the_form_uuid(entorno):
    response = _subir(entorno.cliente, form_uuid="   ")

    assert response.status_code == 422
    assert "form_uuid" in response.json()["detail"]


def test_extension_comes_from_the_mime_not_from_the_file_name(entorno):
    # El nombre que manda el cliente no decide nada: un ".exe" con mime de
    # foto se guarda como .jpg.
    response = _subir(entorno.cliente, nombre="../../evil.exe")

    assert response.status_code == 201
    with entorno.sessionmaker() as db:
        fila = db.query(ProduccionEvidencia).one()
        assert fila.archivo.endswith(".jpg")
        assert "evil" not in fila.archivo


def test_form_uuid_cannot_escape_the_evidence_directory(entorno):
    response = _subir(entorno.cliente, form_uuid="../../secreto")

    assert response.status_code == 201
    with entorno.sessionmaker() as db:
        fila = db.query(ProduccionEvidencia).one()
    destino = (entorno.media / fila.archivo).resolve()
    assert destino.is_relative_to(entorno.media.resolve())
    assert destino.is_file()


def test_horometro_photo_ignores_the_declaration_flag(entorno):
    # La declaracion "el horometro se ve en la pantalla" solo tiene sentido
    # en la foto del procesador (D7).
    response = _subir(
        entorno.cliente,
        tipo=ROL_HOROMETRO,
        incluye_horometro=True,
    )

    assert response.status_code == 201
    assert response.json()["incluye_horometro"] is False


# ─── Servir los bytes ──────────────────────────────────────────────
def test_archive_returns_the_bytes_with_the_real_mime(entorno):
    subida = _subir(entorno.cliente).json()

    response = entorno.cliente.get(subida["url"])

    assert response.status_code == 200
    assert response.content == JPEG_BINARIO
    assert response.headers["content-type"].startswith("image/jpeg")


def test_archive_of_a_missing_evidence_is_404(entorno):
    response = entorno.cliente.get("/api/produccion/evidencias/999999/archivo")

    assert response.status_code == 404


def test_archive_of_a_missing_file_is_404(entorno):
    subida = _subir(entorno.cliente).json()
    with entorno.sessionmaker() as db:
        fila = db.query(ProduccionEvidencia).one()
        fila.archivo = "2026/10/no-existe.jpg"
        db.commit()

    response = entorno.cliente.get(subida["url"])

    assert response.status_code == 404


def test_another_operator_cannot_download_the_photo(entorno):
    subida = _subir(entorno.cliente).json()
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=99, Nombre="OTRO OPERADOR", is_admin=0, encargado=0
    )

    response = entorno.cliente.get(subida["url"])

    assert response.status_code == 403


def test_the_encargado_can_download_any_photo(entorno):
    subida = _subir(entorno.cliente).json()
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=99, Nombre="ENCARGADO", is_admin=0, encargado=1
    )

    response = entorno.cliente.get(subida["url"])

    assert response.status_code == 200


# ─── Listado de la evidencia de un registro ────────────────────────
def test_list_returns_the_evidence_of_the_record(entorno):
    registro_id = _crear_registro(entorno.sessionmaker)
    subida = _subir(entorno.cliente).json()
    with entorno.sessionmaker() as db:
        fila = db.query(ProduccionEvidencia).one()
        fila.registro_id = registro_id
        db.commit()

    response = entorno.cliente.get(f"/api/produccion/registros/{registro_id}/evidencias")

    assert response.status_code == 200
    cuerpo = response.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["id"] == subida["id"]
    assert cuerpo[0]["registro_id"] == registro_id


def test_list_of_a_record_of_another_operator_is_403(entorno):
    registro_id = _crear_registro(entorno.sessionmaker, cod_operador=42)
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=99, Nombre="OTRO OPERADOR", is_admin=0, encargado=0
    )

    response = entorno.cliente.get(f"/api/produccion/registros/{registro_id}/evidencias")

    assert response.status_code == 403


# ─── Verificacion (R5) ─────────────────────────────────────────────
def test_an_operator_can_not_verify(entorno):
    subida = _subir(entorno.cliente).json()

    response = entorno.cliente.patch(
        f"/api/produccion/evidencias/{subida['id']}",
        json={"estado": ESTADO_VERIFICADA},
    )

    assert response.status_code == 403


def test_the_encargado_can_verify(entorno):
    subida = _subir(entorno.cliente).json()
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=99, Nombre="ENCARGADO", is_admin=0, encargado=1
    )

    response = entorno.cliente.patch(
        f"/api/produccion/evidencias/{subida['id']}",
        json={"estado": ESTADO_VERIFICADA, "comentario": "Se ve el horometro"},
    )

    assert response.status_code == 200
    cuerpo = response.json()
    assert cuerpo["estado"] == ESTADO_VERIFICADA
    assert cuerpo["verificado_por"] == "ENCARGADO"
    assert cuerpo["verificado_at"]
    assert cuerpo["comentario"] == "Se ve el horometro"


def test_verification_rejects_an_invalid_state(entorno):
    subida = _subir(entorno.cliente).json()
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=99, Nombre="ENCARGADO", is_admin=0, encargado=1
    )

    response = entorno.cliente.patch(
        f"/api/produccion/evidencias/{subida['id']}",
        json={"estado": ESTADO_PENDIENTE},
    )

    assert response.status_code == 422


def test_a_rejection_keeps_the_file(entorno):
    # R5: un rechazo NO borra la foto: queda el registro del intento.
    subida = _subir(entorno.cliente).json()
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=99, Nombre="ENCARGADO", is_admin=0, encargado=1
    )

    entorno.cliente.patch(
        f"/api/produccion/evidencias/{subida['id']}",
        json={"estado": ESTADO_RECHAZADA, "comentario": "No se ve el horometro"},
    )

    with entorno.sessionmaker() as db:
        fila = db.query(ProduccionEvidencia).one()
        assert fila.estado == ESTADO_RECHAZADA
        assert fila.comentario == "No se ve el horometro"
    assert (entorno.media / fila.archivo).is_file()


# ─── R2 en el alta del parte ───────────────────────────────────────
def test_create_without_the_required_evidence_is_422(entorno):
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "PROCESO", "m3,plantas", True, True
    )

    response = entorno.cliente.post(
        "/api/produccion/", json=_payload_produccion(tipo_id)
    )

    assert response.status_code == 422
    detalle = response.json()["detail"]
    assert "horometro" in detalle
    assert "pantalla del procesador" in detalle
    assert "PROCESO" in detalle


def test_create_with_one_screen_photo_declaring_the_horometro_is_201(entorno):
    # R7 + D7: una sola foto cubre los dos roles si el operador declara que
    # el horometro se ve en esa pantalla.
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "PROCESO", "m3,plantas", True, True
    )
    evidencia_id = _subir(
        entorno.cliente, incluye_horometro=True
    ).json()["id"]

    response = entorno.cliente.post(
        "/api/produccion/",
        json=_payload_produccion(tipo_id, evidencias=[evidencia_id]),
    )

    assert response.status_code == 201
    with entorno.sessionmaker() as db:
        fila = db.query(ProduccionEvidencia).one()
        assert fila.registro_id is not None


def test_create_with_one_screen_photo_without_the_declaration_is_422(entorno):
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "PROCESO", "m3,plantas", True, True
    )
    evidencia_id = _subir(entorno.cliente, incluye_horometro=False).json()["id"]

    response = entorno.cliente.post(
        "/api/produccion/",
        json=_payload_produccion(tipo_id, evidencias=[evidencia_id]),
    )

    assert response.status_code == 422
    assert "horometro" in response.json()["detail"]


def test_create_with_the_two_photos_is_201(entorno):
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "PROCESO", "m3,plantas", True, True
    )
    pantalla = _subir(entorno.cliente, tipo=ROL_PROCESADOR).json()["id"]
    horometro = _subir(
        entorno.cliente, tipo=ROL_HOROMETRO, contenido=PNG_BINARIO, mime="image/png"
    ).json()["id"]

    response = entorno.cliente.post(
        "/api/produccion/",
        json=_payload_produccion(tipo_id, evidencias=[pantalla, horometro]),
    )

    assert response.status_code == 201


def test_a_rejected_photo_does_not_cover_the_role(entorno):
    # R2: una evidencia rechazada no cuenta como cobertura.
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "PROCESO", "m3,plantas", True, True
    )
    evidencia_id = _subir(entorno.cliente, incluye_horometro=True).json()["id"]
    with entorno.sessionmaker() as db:
        fila = db.query(ProduccionEvidencia).one()
        fila.estado = ESTADO_RECHAZADA
        db.commit()

    response = entorno.cliente.post(
        "/api/produccion/",
        json=_payload_produccion(tipo_id, evidencias=[evidencia_id]),
    )

    assert response.status_code == 422


def test_a_process_without_flags_does_not_require_evidence(entorno):
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "CARGA", "tn_despachadas", None, None
    )

    response = entorno.cliente.post(
        "/api/produccion/", json=_payload_produccion(tipo_id, operacion="CARGA")
    )

    assert response.status_code == 201


def test_create_with_an_evidence_of_another_form_is_422(entorno):
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "PROCESO", "m3,plantas", True, True
    )
    evidencia_id = _subir(entorno.cliente, form_uuid="otro-uuid").json()["id"]

    response = entorno.cliente.post(
        "/api/produccion/",
        json=_payload_produccion(tipo_id, evidencias=[evidencia_id]),
    )

    assert response.status_code == 422
    assert "no corresponde a este formulario" in response.json()["detail"]


def test_create_with_an_unknown_evidence_id_is_422(entorno):
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "PROCESO", "m3,plantas", True, True
    )

    response = entorno.cliente.post(
        "/api/produccion/",
        json=_payload_produccion(tipo_id, evidencias=[987654]),
    )

    assert response.status_code == 422
    assert "no existe" in response.json()["detail"]


def test_horas_maquinas_without_final_reading_is_422(entorno):
    # R3: la hora final es obligatoria en los procesos que usan horometro.
    tipo_id = _crear_tipo_proceso(
        entorno.sessionmaker, "HORAS MAQUINAS", "hora_inicio,hora_fin", True, None
    )

    response = entorno.cliente.post(
        "/api/produccion/",
        json=_payload_produccion(
            tipo_id,
            operacion="HORAS MAQUINAS",
            hr_inicio=100,
            hr_fin=0,
        ),
    )

    assert response.status_code == 422


# ─── D-F: adjuntar foto a un registro ya creado ────────────────────
def test_attach_a_photo_to_an_existing_record(entorno):
    registro_id = _crear_registro(entorno.sessionmaker)

    response = entorno.cliente.post(
        f"/api/produccion/registros/{registro_id}/evidencias",
        data={"tipo": ROL_PROCESADOR, "incluye_horometro": "true"},
        files={"archivo": ("foto.jpg", JPEG_BINARIO, "image/jpeg")},
    )

    assert response.status_code == 201
    cuerpo = response.json()
    assert cuerpo["registro_id"] == registro_id
    assert cuerpo["estado"] == ESTADO_PENDIENTE


def test_a_new_photo_does_not_erase_the_rejected_one(entorno):
    registro_id = _crear_registro(entorno.sessionmaker)
    primera = entorno.cliente.post(
        f"/api/produccion/registros/{registro_id}/evidencias",
        data={"tipo": ROL_PROCESADOR},
        files={"archivo": ("foto.jpg", JPEG_BINARIO, "image/jpeg")},
    ).json()
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=99, Nombre="ENCARGADO", is_admin=0, encargado=1
    )
    entorno.cliente.patch(
        f"/api/produccion/evidencias/{primera['id']}",
        json={"estado": ESTADO_RECHAZADA, "comentario": "Foto borrosa"},
    )
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=7, Nombre="OPERADOR UNO", is_admin=0, encargado=0
    )

    segunda = entorno.cliente.post(
        f"/api/produccion/registros/{registro_id}/evidencias",
        data={"tipo": ROL_PROCESADOR},
        files={"archivo": ("foto2.jpg", PNG_BINARIO, "image/png")},
    )

    assert segunda.status_code == 201
    assert segunda.json()["id"] != primera["id"]
    with entorno.sessionmaker() as db:
        filas = db.query(ProduccionEvidencia).order_by(ProduccionEvidencia.id).all()
        assert len(filas) == 2
        assert filas[0].estado == ESTADO_RECHAZADA
        assert filas[0].comentario == "Foto borrosa"
        assert filas[1].estado == ESTADO_PENDIENTE


def test_a_verified_photo_can_not_be_replaced(entorno):
    registro_id = _crear_registro(entorno.sessionmaker)
    primera = entorno.cliente.post(
        f"/api/produccion/registros/{registro_id}/evidencias",
        data={"tipo": ROL_PROCESADOR},
        files={"archivo": ("foto.jpg", JPEG_BINARIO, "image/jpeg")},
    ).json()
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=99, Nombre="ENCARGADO", is_admin=0, encargado=1
    )
    entorno.cliente.patch(
        f"/api/produccion/evidencias/{primera['id']}",
        json={"estado": ESTADO_VERIFICADA},
    )
    entorno.usuarios["actual"] = SimpleNamespace(
        idPersonal=7, Nombre="OPERADOR UNO", is_admin=0, encargado=0
    )

    segunda = entorno.cliente.post(
        f"/api/produccion/registros/{registro_id}/evidencias",
        data={"tipo": ROL_PROCESADOR},
        files={"archivo": ("foto2.jpg", PNG_BINARIO, "image/png")},
    )

    assert segunda.status_code == 409


def test_a_pending_photo_is_kept_as_history_when_replaced(entorno):
    registro_id = _crear_registro(entorno.sessionmaker)
    primera = entorno.cliente.post(
        f"/api/produccion/registros/{registro_id}/evidencias",
        data={"tipo": ROL_PROCESADOR},
        files={"archivo": ("foto.jpg", JPEG_BINARIO, "image/jpeg")},
    ).json()

    segunda = entorno.cliente.post(
        f"/api/produccion/registros/{registro_id}/evidencias",
        data={"tipo": ROL_PROCESADOR},
        files={"archivo": ("foto2.jpg", PNG_BINARIO, "image/png")},
    )

    assert segunda.status_code == 201
    with entorno.sessionmaker() as db:
        filas = db.query(ProduccionEvidencia).order_by(ProduccionEvidencia.id).all()
        assert len(filas) == 2
        assert filas[0].estado == ESTADO_REEMPLAZADA
        assert filas[1].estado == ESTADO_PENDIENTE


def test_attach_to_a_record_of_another_operator_is_403(entorno):
    registro_id = _crear_registro(entorno.sessionmaker, cod_operador=42)

    response = entorno.cliente.post(
        f"/api/produccion/registros/{registro_id}/evidencias",
        data={"tipo": ROL_PROCESADOR},
        files={"archivo": ("foto.jpg", JPEG_BINARIO, "image/jpeg")},
    )

    assert response.status_code == 403


# ─── Reglas puras (core/evidencia.py) ──────────────────────────────
def test_roles_of_a_photo_depend_on_the_declaration():
    assert roles_de(ROL_PROCESADOR, False) == {ROL_PROCESADOR}
    assert roles_de(ROL_PROCESADOR, True) == {ROL_PROCESADOR, ROL_HOROMETRO}
    assert roles_de(ROL_HOROMETRO, False) == {ROL_HOROMETRO}


def test_required_roles_come_from_the_flags():
    assert roles_exigidos(True, True) == {ROL_HOROMETRO, ROL_PROCESADOR}
    assert roles_exigidos(False, False) == set()
    assert roles_exigidos(True, False) == {ROL_HOROMETRO}


def test_only_a_live_photo_covers_a_role():
    class Fila:
        def __init__(self, tipo, incluye, estado):
            self.tipo = tipo
            self.incluye_horometro = incluye
            self.estado = estado

    exigidos = {ROL_HOROMETRO}
    assert roles_faltantes(exigidos, [Fila(ROL_HOROMETRO, 0, ESTADO_PENDIENTE)]) == set()
    assert roles_faltantes(exigidos, [Fila(ROL_HOROMETRO, 0, ESTADO_RECHAZADA)]) == exigidos
    assert roles_faltantes(exigidos, [Fila(ROL_HOROMETRO, 0, ESTADO_REEMPLAZADA)]) == exigidos
    # La foto de la pantalla con la declaracion cubre el horometro (D7).
    assert roles_faltantes(exigidos, [Fila(ROL_PROCESADOR, 1, ESTADO_PENDIENTE)]) == set()


def test_missing_evidence_message_names_the_photo():
    mensaje = mensaje_faltante({ROL_HOROMETRO, ROL_PROCESADOR}, "PROCESO")

    assert "horometro" in mensaje
    assert "pantalla del procesador" in mensaje
    assert "PROCESO" in mensaje


def test_mime_maps_to_the_extension():
    assert extension_para_mime("image/jpeg") == ".jpg"
    assert extension_para_mime("image/png") == ".png"
    assert extension_para_mime("image/webp") == ".webp"
    assert extension_para_mime("image/heic") == ".heic"


def test_the_relative_path_is_sharded_by_month():
    desde = datetime_fijo(2026, 10, 24)

    relativo = ruta_relativa("uuid-1", ROL_PROCESADOR, "a" * 64, ".jpg", desde)

    assert relativo.startswith("2026/10/")
    assert relativo.endswith(".jpg")
    assert "uuid-1" in relativo


def test_the_relative_path_sanitizes_the_form_uuid():
    desde = datetime_fijo(2026, 10, 24)

    relativo = ruta_relativa("../../etc/passwd", ROL_PROCESADOR, "b" * 64, ".jpg", desde)

    assert ".." not in relativo
    assert "/" not in relativo.replace("2026/10/", "")


def test_the_absolute_path_cannot_leave_the_directory(tmp_path):
    with pytest.raises(Exception):
        ruta_absoluta(tmp_path, "../fuera.jpg")


def test_the_file_is_written_atomically(tmp_path):
    base = tmp_path / "media"

    guardar_archivo(base, "2026/10/foto.jpg", b"contenido")

    assert (base / "2026" / "10" / "foto.jpg").read_bytes() == b"contenido"
    assert not list(base.rglob("*.tmp"))


def datetime_fijo(anio, mes, dia):
    from datetime import datetime

    return datetime(anio, mes, dia)


# ─── Migracion del historial (20261025) ────────────────────────────
MIGRATION_HISTORIAL = (
    Path(__file__).resolve().parents[2]
    / "db_migrations"
    / "20261025_evidencia_historial.sql"
)


def _sql_historial() -> str:
    return MIGRATION_HISTORIAL.read_text(encoding="utf-8")


def test_migration_historial_exists():
    assert MIGRATION_HISTORIAL.is_file()


def test_migration_historial_is_idempotent():
    # El runner aplica TODOS los .sql en cada deploy: cada ALTER tiene que
    # comprobar information_schema antes de ejecutarse.
    sql = _sql_historial()

    assert "information_schema.COLUMNS" in sql
    assert "information_schema.STATISTICS" in sql


def test_migration_historial_relaxes_the_unique_index():
    sql = _sql_historial()

    assert "DROP INDEX uq_evidencia_form_tipo" in sql
    assert "ADD INDEX idx_evidencia_form_tipo (form_uuid, tipo)" in sql


def test_migration_historial_adds_the_author_column():
    sql = _sql_historial()

    assert "ADD COLUMN cargado_por_id" in sql
