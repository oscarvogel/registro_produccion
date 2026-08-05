"""Tests del helper compartido y los nuevos endpoints de registros (issue #104).

Cubre:
- ``_resolve_records_query`` aplica los filtros correctos para cada rol.
- ``list_registros`` pagina, ordena y filtra segun los params.
- ``get_registro_detalle`` valida 404 para id fuera de alcance y 200 para
  registros que SI pertenecen al usuario.
- El refactor de ``/mis-registros`` sigue aislando por ``cod_operador``.
"""
from contextlib import contextmanager
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes import dashboard, produccion


# ─── Fakes ─────────────────────────────────────────────────────────────────


class CapturingQuery:
    """Query que captura cada llamada a .filter() y devuelve self.

    Permite inspeccionar los filtros aplicados contando las llamadas
    (``.filter_calls``) o comparando las representaciones de los args.
    """

    def __init__(self, rows=None, count_value=0):
        self.rows = rows or []
        self.count_value = count_value
        self.filter_calls = []
        self.order_by_calls = []
        self.offset_value = None
        self.limit_value = None
        self._with_entities = False
        self._count_query = False

    def filter(self, *args, **kwargs):
        self.filter_calls.append((args, kwargs))
        return self

    def with_entities(self, *args, **kwargs):
        self._with_entities = True
        # Si piden un COUNT devolvemos un subquery fake con scalar()
        if args and "count" in str(args[0]).lower():
            self._count_query = True
        return self

    def order_by(self, *args, **kwargs):
        self.order_by_calls.append((args, kwargs))
        return self

    def offset(self, value):
        self.offset_value = value
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def all(self):
        return self.rows

    def scalar(self):
        return self.count_value if self._count_query else None

    def first(self):
        return self.rows[0] if self.rows else None


class FakeDb:
    def __init__(self, rows=None, count_value=0):
        self.query_obj = CapturingQuery(rows=rows, count_value=count_value)
        # Diferentes .query() pueden querer distintos sub-queries; con uno solo alcanza
        # para los tests de helper. El endpoint detail hace su propio .query().
        self._next_first_value = None

    def query(self, *_args, **_kwargs):
        return self.query_obj


# ─── _resolve_records_query ────────────────────────────────────────────────


def test_resolve_records_only_self_requiere_cod_operador():
    db = FakeDb()
    user = SimpleNamespace(idPersonal=42, is_admin=0, encargado=0)

    with pytest.raises(HTTPException) as exc:
        dashboard._resolve_records_query(db, user, only_self=True, self_cod_operador=None)
    assert exc.value.status_code == 400


def _has_filter_attr(query, attr_name: str) -> bool:
    """Helper: chequea si algun .filter() aplicado menciona un atributo del modelo.

    El str() de un SQLAlchemy BinaryExpression incluye el nombre del lado
    izquierdo (ej: 'tablero_produccion.cod_un')."""
    for args, _ in query.filter_calls:
        for arg in args:
            if attr_name in str(arg):
                return True
    return False


def _filter_count(query) -> int:
    return len(query.filter_calls)


def test_resolve_records_only_self_filtra_por_cod_operador():
    db = FakeDb()
    user = SimpleNamespace(idPersonal=42, is_admin=0, encargado=0)

    dashboard._resolve_records_query(
        db, user,
        only_self=True,
        self_cod_operador=42,
        fecha_desde=date(2026, 7, 1),
        fecha_hasta=date(2026, 7, 31),
    )

    # cod_operador + 2 fechas = 3 filtros
    assert _filter_count(db.query_obj) == 3
    assert _has_filter_attr(db.query_obj, "cod_operador")
    assert _has_filter_attr(db.query_obj, "fecha")  # aplicado 2 veces
    # NO debe filtrar por cod_un (el operador no tiene UN, solo su persona)
    assert not _has_filter_attr(db.query_obj, "cod_un")


def test_resolve_records_encargado_con_un_id_usa_verify_un(monkeypatch):
    """Si el encargado pide un un_id, _verify_un debe llamarse y filtrar por esa UN."""
    db = FakeDb()
    user = SimpleNamespace(idPersonal=1, is_admin=0, encargado=1)
    verify_called = []

    def fake_verify(_user, _un_id, _db):
        verify_called.append(_un_id)

    monkeypatch.setattr(dashboard, "_verify_un", fake_verify)

    dashboard._resolve_records_query(
        db, user, un_id=7, movil_id=3,
        fecha_desde=date(2026, 7, 1), fecha_hasta=date(2026, 7, 31),
    )

    assert verify_called == [7]
    # 4 filtros: cod_un, cod_equipo, fecha>=, fecha<=
    assert _filter_count(db.query_obj) == 4
    assert _has_filter_attr(db.query_obj, "cod_un")
    assert _has_filter_attr(db.query_obj, "cod_equipo")
    assert _has_filter_attr(db.query_obj, "fecha")


def test_resolve_records_encargado_sin_un_id_ve_multi_un(monkeypatch):
    """Encargado SIN un_id: filtra por todas sus unidades autorizadas."""
    db = FakeDb()
    user = SimpleNamespace(idPersonal=1, is_admin=0, encargado=1, unidad_negocio=2)

    monkeypatch.setattr(
        dashboard, "_personal_unidad_ids", lambda _db, _user: {2, 5, 9},
    )

    dashboard._resolve_records_query(db, user, movil_id=11)

    # 2 filtros: cod_un IN (multi-UN), cod_equipo
    assert _filter_count(db.query_obj) == 2
    assert _has_filter_attr(db.query_obj, "cod_un")
    assert _has_filter_attr(db.query_obj, "cod_equipo")


def test_resolve_records_encargado_sin_unidades_ve_nada(monkeypatch):
    """Si el encargado no tiene unidades asignadas, no debe ver registros."""
    db = FakeDb()
    user = SimpleNamespace(idPersonal=1, is_admin=0, encargado=1, unidad_negocio=None)

    monkeypatch.setattr(dashboard, "_personal_unidad_ids", lambda _db, _user: set())

    dashboard._resolve_records_query(db, user, fecha_desde=date(2026, 7, 1))

    # 2 filtros: id == -1, fecha >=
    assert _filter_count(db.query_obj) == 2
    assert _has_filter_attr(db.query_obj, "id")  # sentinela


def test_resolve_records_admin_sin_un_id_ve_todo(monkeypatch):
    """Admin sin un_id: no debe filtrar por UN, solo por los filtros de datos."""
    db = FakeDb()
    user = SimpleNamespace(idPersonal=1, is_admin=1, encargado=0)

    dashboard._resolve_records_query(
        db, user, fecha_desde=date(2026, 7, 1), fecha_hasta=date(2026, 7, 31),
    )

    # Solo los 2 filtros de fechas
    assert _filter_count(db.query_obj) == 2
    assert not _has_filter_attr(db.query_obj, "cod_un")
    assert _has_filter_attr(db.query_obj, "fecha")


def test_resolve_records_tipo_proceso_usa_helper_existente(monkeypatch):
    """El filtro de tipo_proceso debe reutilizar _apply_process_filter."""
    db = FakeDb()
    user = SimpleNamespace(idPersonal=1, is_admin=1, encargado=0)
    captured = []

    monkeypatch.setattr(
        dashboard, "_apply_process_filter",
        lambda base, pf: captured.append(pf) or base,
    )

    dashboard._resolve_records_query(db, user, tipo_proceso_id=3)

    assert captured == [{"mode": "tipo", "ids": [3]}]


# ─── Paginación ────────────────────────────────────────────────────────────


def test_normalize_pagination_clamp_basico():
    assert dashboard._normalize_pagination(0, 50) == (1, 50)
    assert dashboard._normalize_pagination(-3, 0) == (1, 20)
    assert dashboard._normalize_pagination(5, 250) == (5, 100)
    assert dashboard._normalize_pagination(2, 30) == (2, 30)


# ─── get_registro_detalle (auth) ───────────────────────────────────────────


def test_get_registro_detalle_404_si_no_existe(monkeypatch):
    db = FakeDb(rows=[])

    with pytest.raises(HTTPException) as exc:
        # La función async, la corremos via asyncio.run para test simple
        import asyncio
        asyncio.run(dashboard.get_registro_detalle(999, user=SimpleNamespace(is_admin=1, idPersonal=1, encargado=0), db=db))
    assert exc.value.status_code == 404


def test_get_registro_detalle_404_si_un_no_autorizada(monkeypatch):
    """Encargado pide un registro de una UN que no le pertenece -> 404."""
    row = SimpleNamespace(id=1, cod_un=99)
    db = FakeDb(rows=[row])
    user = SimpleNamespace(idPersonal=1, is_admin=0, encargado=1, unidad_negocio=2)

    def fake_verify(_u, _un, _db):
        raise HTTPException(status_code=403, detail="forbidden")

    monkeypatch.setattr(dashboard, "_verify_un", fake_verify)

    import asyncio
    with pytest.raises(HTTPException) as exc:
        asyncio.run(dashboard.get_registro_detalle(1, user=user, db=db))
    assert exc.value.status_code == 404
    assert "no encontrado" in str(exc.value.detail).lower()


def test_get_registro_detalle_admin_no_filtra_por_un(monkeypatch):
    """Admin puede ver registros de cualquier UN (incluso sin cod_un asignada)."""
    row = SimpleNamespace(id=1, cod_un=None)
    db = FakeDb(rows=[row])
    user = SimpleNamespace(idPersonal=1, is_admin=1, encargado=0)
    verify_called = []

    monkeypatch.setattr(dashboard, "_verify_un", lambda *a, **k: verify_called.append(a))

    import asyncio
    result = asyncio.run(dashboard.get_registro_detalle(1, user=user, db=db))
    # Si el row tiene cod_un None, admin igual lo ve (sin invocar _verify_un)
    assert verify_called == []


def test_get_registro_detalle_acepta_nulls_en_campos_opcionales(monkeypatch):
    """Issue #127: si la fila tiene NULLs en los 11 campos opcionales que
    el schema ``RegistroDetail`` declara con default, el endpoint debe
    responder 200 con el detalle (Pydantic aplica el default) en lugar de
    devolver 500 por ValidationError.
    """
    # Fila con todos los campos opcionales en None (caso real en prod).
    row = SimpleNamespace(
        id=45302,
        cod_un=106,
        # los 11 campos del bug:
        parcela=None,
        giro_pinon=None,
        remito_proveedor=None,
        remito_fgpy=None,
        nombre_chofer=None,
        cliente_camion=None,
        origen_camion=None,
        destino_camion=None,
        usuario=None,
        hora_inicio_viaje=None,
        hora_fin_viaje=None,
    )
    db = FakeDb(rows=[row])
    user = SimpleNamespace(idPersonal=1, is_admin=1, encargado=0)
    verify_called = []

    monkeypatch.setattr(dashboard, "_verify_un", lambda *a, **k: verify_called.append(a))

    import asyncio
    # Antes del fix: pydantic_core._pydantic_core.ValidationError -> 500.
    # Despues del fix: RegistroDetail con los NULLs preservados (los 11
    # campos quedaron Optional[...] = None). El frontend ya renderiza
    # None como "-" via formatCampo.
    result = asyncio.run(dashboard.get_registro_detalle(45302, user=user, db=db))
    assert result is not None
    assert result.id == 45302
    assert result.parcela is None
    assert result.giro_pinon is None
    assert result.remito_proveedor is None
    assert result.remito_fgpy is None
    assert result.nombre_chofer is None
    assert result.cliente_camion is None
    assert result.origen_camion is None
    assert result.destino_camion is None
    assert result.usuario is None
    assert result.hora_inicio_viaje is None
    assert result.hora_fin_viaje is None


# ─── list_registros (estructura) ──────────────────────────────────────────


def test_list_registros_calcula_total_y_pagina(monkeypatch):
    rows = [
        SimpleNamespace(
            id=10, fecha=date(2026, 7, 15), operacion="Cosecha", equipo="MQ-1",
            operador="Juan", cod_operador=1, cod_equipo=11, cod_un=2,
            tipo_proceso_id=None, hr_inicio=8, hr_fin=12, hrs_no_op=0,
            motivo_no_op="0", combustible=0, aceite_cadena=0,
            tn_despachadas=10, m3=0, has=0, carros=0, plantas=0,
            km_carreteo=0, km_perfilado=0, mtrs_recorridos=0,
            remito="", remito2="", remito3="", remito_bitren="",
        ),
    ]
    db = FakeDb(rows=rows, count_value=37)
    user = SimpleNamespace(idPersonal=1, is_admin=1, encargado=0)

    monkeypatch.setattr(dashboard, "_resolve_records_query", lambda *a, **k: db.query_obj)

    import asyncio
    response = asyncio.run(dashboard.list_registros(
        un_id=2, page=2, page_size=20, user=user, db=db,
    ))

    assert response.total == 37
    assert response.page == 2
    assert response.page_size == 20
    assert response.total_pages == 2  # ceil(37 / 20)
    assert len(response.items) == 1
    assert response.items[0].id == 10
    # Paginación: offset = (2-1)*20 = 20
    assert db.query_obj.offset_value == 20
    assert db.query_obj.limit_value == 20
    # Orden aplicado
    assert len(db.query_obj.order_by_calls) >= 1


def test_list_registros_clamp_paginacion(monkeypatch):
    """Si page=0 o page_size>100, _normalize_pagination corrige."""
    db = FakeDb(rows=[], count_value=0)
    user = SimpleNamespace(idPersonal=1, is_admin=1, encargado=0)
    monkeypatch.setattr(dashboard, "_resolve_records_query", lambda *a, **k: db.query_obj)

    import asyncio
    response = asyncio.run(dashboard.list_registros(
        un_id=1, page=0, page_size=500, user=user, db=db,
    ))

    assert response.page == 1
    assert response.page_size == 100
    # El offset y limit se aplican sobre la query (no sobre el response)
    assert db.query_obj.offset_value == 0  # (1-1)*100 = 0
    assert db.query_obj.limit_value == 100


# ─── Refactor /mis-registros ──────────────────────────────────────────────


def test_mis_registros_sigue_limitado_al_operador(monkeypatch):
    """/mis-registros debe seguir llamando al helper con only_self=True
    y self_cod_operador = user.idPersonal. Verifica que el refactor no
    haya debilitado la regla de aislamiento por operador.
    """
    captured = {}

    def fake_resolve(db, user, **kwargs):
        captured["kwargs"] = kwargs
        captured["user_id"] = user.idPersonal
        return CapturingQuery(rows=[])

    monkeypatch.setattr(
        "app.api.routes.dashboard._resolve_records_query", fake_resolve,
    )

    # Mock de los modelos para evitar SQL real
    from app.api.routes import produccion as produccion_routes

    fake_personal = SimpleNamespace(
        idPersonal=1, Nombre="Test", dni=None, encargado=0,
        tipo_de_proceso_id=None, unidad_ids=[],
    )

    import asyncio
    response = asyncio.run(produccion_routes.get_mis_registros(
        fecha_desde=date(2026, 7, 1),
        fecha_hasta=date(2026, 7, 31),
        user=fake_personal,
        db=FakeDb(rows=[]),
    ))

    assert captured["kwargs"]["only_self"] is True
    assert captured["kwargs"]["self_cod_operador"] == 1  # fake_personal.id
    assert captured["kwargs"]["fecha_desde"] == date(2026, 7, 1)
    assert captured["kwargs"]["fecha_hasta"] == date(2026, 7, 31)
    # un_id no debe pasarse en modo only_self (ignorado por el helper)
    assert "un_id" not in captured["kwargs"] or captured["kwargs"].get("un_id") is None
