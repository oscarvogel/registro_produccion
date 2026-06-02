from types import SimpleNamespace

from app.api.routes import produccion


class FakeQuery:
    def __init__(self, rows):
        self.rows = rows
        self.filter_calls = 0

    def filter(self, *_args, **_kwargs):
        self.filter_calls += 1
        return self

    def all(self):
        return self.rows


class FakeDb:
    def __init__(self, rows):
        self.query_obj = FakeQuery(rows)

    def query(self, *_args, **_kwargs):
        return self.query_obj


def test_personal_unidad_ids_map_batches_relation_lookup(monkeypatch):
    monkeypatch.setattr(produccion, "_table_exists", lambda _db, _table_name: True)
    db = FakeDb([(1, 7), (1, 8), (2, None), (3, 9)])
    people = [
        SimpleNamespace(idPersonal=1, unidad_negocio=4),
        SimpleNamespace(idPersonal=2, unidad_negocio=5),
        SimpleNamespace(idPersonal=3, unidad_negocio=None),
    ]

    result = produccion._personal_unidad_ids_map(db, people)

    assert result == {
        1: [7, 8],
        2: [5],
        3: [9],
    }
    assert db.query_obj.filter_calls == 1
