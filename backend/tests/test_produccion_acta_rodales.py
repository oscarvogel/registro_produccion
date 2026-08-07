"""Tests de regresion para `GET /api/produccion/actas/{numero}/rodales`.

Issue #133: el dropdown de Rodal en la app móvil debe mostrar los rodales
vinculados al Acta elegida, no los del último Predio cargado.

Estos tests validan el endpoint nuevo sin levantar FastAPI: llaman a la
función async con un doble de ``Session`` (FakeDb) que responde segun el
modelo que se le pida. Se hace monkeypatch de ``_table_exists`` para no
depender del engine real.
"""
import asyncio
from types import SimpleNamespace

from app.api.routes import produccion


class ActaRow:
    """Fila minima del modelo ``Acta`` (solo lo que el endpoint mira)."""

    def __init__(self, numero, rodal_id):
        self.numero = numero
        self.rodal_id = rodal_id


class RodalRow:
    """Fila minima del modelo ``Rodal`` (mapea a ``RodalResponse``)."""

    def __init__(self, idRodal, rodal, idPredio):
        self.idRodal = idRodal
        self.Rodal = rodal
        self.idPredio = idPredio


class FakeQuery:
    """Query en cadena que aplica filtros de igualdad simples.

    Soporta encadenar ``.filter(...)`` y ``.order_by(...)``. El filter
    inspecciona la expresión de SQLAlchemy (``BinaryExpression`` con
    ``left`` columna y ``right`` valor) y descarta las filas cuyo atributo
    no coincida con el valor. Si el filter no se puede inspeccionar (por
    ejemplo, una expresión compleja), no se aplica.
    """

    def __init__(self, rows):
        self._rows = list(rows)

    def filter(self, *conditions, **_kwargs):
        for cond in conditions:
            self._rows = [r for r in self._rows if _match_condition(r, cond)]
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def all(self):
        return list(self._rows)


def _match_condition(row, cond):
    """Si ``cond`` es ``Column == value`` o ``Column.in_(values)``, filtra.

    Para mantener el test simple, solo soporta equality y ``in_``.
    Si la expresión es compleja, devuelve True (no filtra).
    """
    # Equality: Column == value  (BinaryExpression)
    left = getattr(cond, "left", None)
    right = getattr(cond, "right", None)
    op = getattr(cond, "operator", None)
    if left is not None and right is not None and op is not None:
        op_name = getattr(op, "__name__", "")
        attr_name = getattr(left, "key", None) or getattr(left, "name", None)
        if op_name == "eq" and attr_name:
            return getattr(row, attr_name, None) == _unwrap_bindparam(right)
        # in_: el lado derecho es un tuple/lista
        if op_name == "in_op" and attr_name:
            values = right
            if hasattr(right, "value"):  # BindParameter con tupla adentro
                values = right.value
            try:
                return getattr(row, attr_name, None) in values
            except TypeError:
                return True
    return True


def _unwrap_bindparam(value):
    """Los valores literales del filter vienen envueltos en BindParameter."""
    return getattr(value, "value", value)


class FakeDb:
    """Doble de ``Session`` con dos colecciones: ``actas`` y ``rodales``.

    Acepta tanto ``db.query(Acta)`` como ``db.query(Acta.rodal_id)``
    (queries por columna). Para las queries por columna, identifica la
    tabla via ``column.table.name``.
    """

    def __init__(self, actas=None, rodales=None):
        self._actas = list(actas or [])
        self._rodales = list(rodales or [])

    def query(self, model, *_args, **_kwargs):
        # Caso 1: query por columna → tiene ``.table.name``
        table = getattr(model, "table", None)
        table_name = getattr(table, "name", None) if table is not None else None
        if table_name == "actas":
            return FakeQuery(self._actas)
        if table_name == "rodales":
            return FakeQuery(self._rodales)
        # Caso 2: query por modelo → tiene ``__name__``
        cls_name = getattr(model, "__name__", "")
        if cls_name == "Acta":
            return FakeQuery(self._actas)
        if cls_name == "Rodal":
            return FakeQuery(self._rodales)
        return FakeQuery([])


def _run(coro):
    return asyncio.run(coro)


def test_endpoint_devuelve_rodales_de_un_acta_con_multiples_filas(monkeypatch):
    """Caso del bug: acta 7900001260 tiene 2 filas, una por cada Rodal."""
    monkeypatch.setattr(produccion, "_table_exists", lambda _db, _t: True)
    actas = [
        ActaRow(numero="7900001260", rodal_id=10),
        ActaRow(numero="7900001260", rodal_id=11),
    ]
    rodales = [
        RodalRow(idRodal=10, rodal="01", idPredio=1),
        RodalRow(idRodal=11, rodal="94", idPredio=2),
        # Rodal de OTRA acta que NO debe aparecer
        RodalRow(idRodal=99, rodal="99", idPredio=3),
    ]
    db = FakeDb(actas=actas, rodales=rodales)

    result = _run(produccion.list_rodales_por_acta("7900001260", db=db))

    assert len(result) == 2
    rodales_devueltos = sorted([r.rodal for r in result])
    assert rodales_devueltos == ["01", "94"]


def test_endpoint_acta_no_encontrada_devuelve_lista_vacia(monkeypatch):
    """Si el numero de acta no existe, devolver lista vacia (no 404)."""
    monkeypatch.setattr(produccion, "_table_exists", lambda _db, _t: True)
    db = FakeDb(
        actas=[ActaRow(numero="OTRA", rodal_id=10)],
        rodales=[RodalRow(idRodal=10, rodal="01", idPredio=1)],
    )

    result = _run(produccion.list_rodales_por_acta("NO-EXISTE", db=db))

    assert result == []


def test_endpoint_acta_sin_rodal_id_devuelve_lista_vacia(monkeypatch):
    """Filas con ``rodal_id=0`` (basura/sin asignar) no deben explotar."""
    monkeypatch.setattr(produccion, "_table_exists", lambda _db, _t: True)
    actas = [
        ActaRow(numero="X", rodal_id=0),
        ActaRow(numero="X", rodal_id=0),
    ]
    db = FakeDb(actas=actas, rodales=[])

    result = _run(produccion.list_rodales_por_acta("X", db=db))

    assert result == []


def test_endpoint_numero_vacio_devuelve_lista_vacia(monkeypatch):
    """``acta_numero`` vacio o solo espacios: lista vacia sin tocar la DB."""
    monkeypatch.setattr(produccion, "_table_exists", lambda _db, _t: True)
    db = FakeDb(
        actas=[ActaRow(numero="X", rodal_id=10)],
        rodales=[RodalRow(idRodal=10, rodal="01", idPredio=1)],
    )

    for vacio in ["", "   "]:
        result = _run(produccion.list_rodales_por_acta(vacio, db=db))
        assert result == []


def test_endpoint_normaliza_numero_con_espacios(monkeypatch):
    """El numero viene con espacios (ej. del form); debe trim-ear antes de buscar."""
    monkeypatch.setattr(produccion, "_table_exists", lambda _db, _t: True)
    actas = [ActaRow(numero="7900001260", rodal_id=10)]
    rodales = [RodalRow(idRodal=10, rodal="01", idPredio=1)]
    db = FakeDb(actas=actas, rodales=rodales)

    result = _run(produccion.list_rodales_por_acta("  7900001260  ", db=db))

    assert len(result) == 1
    assert result[0].rodal == "01"


def test_endpoint_deduplica_si_hay_filas_repetidas_para_mismo_rodal(monkeypatch):
    """Si dos filas de actas repiten el mismo ``rodal_id``, no duplicar en la respuesta."""
    monkeypatch.setattr(produccion, "_table_exists", lambda _db, _t: True)
    actas = [
        ActaRow(numero="DUP", rodal_id=10),
        ActaRow(numero="DUP", rodal_id=10),
        ActaRow(numero="DUP", rodal_id=10),
    ]
    rodales = [RodalRow(idRodal=10, rodal="01", idPredio=1)]
    db = FakeDb(actas=actas, rodales=rodales)

    result = _run(produccion.list_rodales_por_acta("DUP", db=db))

    assert len(result) == 1
    assert result[0].idRodal == 10


def test_endpoint_respeta_caso_un_solo_rodal(monkeypatch):
    """Caso normal (un acta con un solo rodal) sigue funcionando."""
    monkeypatch.setattr(produccion, "_table_exists", lambda _db, _t: True)
    actas = [ActaRow(numero="UNICO", rodal_id=42)]
    rodales = [RodalRow(idRodal=42, rodal="A", idPredio=1)]
    db = FakeDb(actas=actas, rodales=rodales)

    result = _run(produccion.list_rodales_por_acta("UNICO", db=db))

    assert len(result) == 1
    assert result[0].idRodal == 42
    assert result[0].rodal == "A"
    assert result[0].idPredio == 1


def test_endpoint_no_explota_si_tabla_actas_no_existe(monkeypatch):
    """Defensivo: si la tabla ``actas`` no esta, devolver lista vacia (no 500)."""
    def fake_table_exists(_db, table):
        return table != "actas"
    monkeypatch.setattr(produccion, "_table_exists", fake_table_exists)
    db = FakeDb()

    result = _run(produccion.list_rodales_por_acta("LO-QUE-SEA", db=db))

    assert result == []
