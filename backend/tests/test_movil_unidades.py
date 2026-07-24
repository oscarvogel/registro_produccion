import asyncio

from app.api.routes import admin_legacy
from app.schemas.admin import MovilCreate, MovilResponse, MovilUpdate


class FakeQuery:
    def __init__(self, row):
        self.row = row

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return self.row


class FakeDb:
    def __init__(self, row):
        self.row = row
        self.commits = 0
        self.refreshed = []
        self.deleted = []
        self.added = []

    def query(self, *_args, **_kwargs):
        return FakeQuery(self.row)

    def commit(self):
        self.commits += 1

    def refresh(self, row):
        self.refreshed.append(row)

    def get_bind(self):
        return self

    def add(self, _obj):
        self.added.append(_obj)


class MovilRow:
    idMovil = 17
    Patente = "MWY673"
    Detalle = "CAMION CARGADOR"
    tipo_proceso = "1"
    idUnidadNegocio = 1
    CantNeumaticos = 6
    capacidad_tanque = 200
    consumo_promedio = 25.5
    tipo_movil = 2
    anio_fabricacion = 2019
    nro_chasis = "CH-001"
    nro_motor = "MTR-002"
    VencTecnica = None
    Ruta = False
    VencRuta = None
    activo = 1
    observaciones = None


def test_movil_create_defaults_unidad_ids_to_empty_list():
    payload = MovilCreate(patente="MWY673", detalle="CAMION CARGADOR")

    assert payload.unidad_ids == []
    assert payload.id_unidad_negocio == 1


def test_movil_response_includes_unidad_ids(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_movil_unidad_ids", lambda _db, _row: [1, 2, 5])
    row = MovilRow()

    response = admin_legacy._to_movil_response(object(), row)

    assert response.idMovil == 17
    assert response.id_unidad_negocio == 1
    assert response.unidad_ids == [1, 2, 5]
    assert response.activo == 1


def test_movil_response_falls_back_to_principal_when_pivot_empty(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_movil_unidad_ids", lambda _db, _row: [])
    row = MovilRow()
    row.idUnidadNegocio = 3

    response = admin_legacy._to_movil_response(object(), row)

    assert response.id_unidad_negocio == 3
    assert response.unidad_ids == [3]


def test_movil_responses_bulk_hydrates_unit_ids(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_movil_unidad_ids_map", lambda _db, rows: {17: [4, 5], 18: [6]})
    row_a = MovilRow()
    row_a.idUnidadNegocio = 1
    row_b = MovilRow()
    row_b.idMovil = 18
    row_b.idUnidadNegocio = 1

    responses = admin_legacy._to_movil_responses(object(), [row_a, row_b])

    assert [r.unidad_ids for r in responses] == [[4, 5], [6]]
    assert responses[0].id_unidad_negocio == 4
    assert responses[1].id_unidad_negocio == 6


def test_sync_movil_unidades_falls_back_when_pivot_table_missing(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_table_exists", lambda _db, table: False)
    row = MovilRow()
    db = FakeDb(row)

    admin_legacy._sync_movil_unidades(db, row, [5, 7])

    assert row.idUnidadNegocio == 5
    assert db.added == []


def test_sync_movil_unidades_replaces_pivot_rows(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_table_exists", lambda _db, table: True)
    added: list = []
    deleted: list = []

    class PivotQuery:
        def filter(self, *_args, **_kwargs):
            return self

        def delete(self):
            deleted.append(True)
            return 0

    class PivotDb(FakeDb):
        def query(self, *args, **_kwargs):
            if args and args[0] is admin_legacy.MovilUnidadNegocio:
                return PivotQuery()
            return FakeDb(self.row).query(*args)

        def add(self, obj):
            added.append(obj)

    row = MovilRow()
    db = PivotDb(row)

    admin_legacy._sync_movil_unidades(db, row, [2, 3, 2, -1, 0])

    assert row.idUnidadNegocio == 2
    assert [obj.idUnidadNegocio for obj in added] == [2, 3]
    assert all(obj.idMovil == 17 for obj in added)
    assert deleted == [True]


def test_update_movil_persists_unidad_ids(monkeypatch):
    monkeypatch.setattr(admin_legacy, "_movil_unidad_ids", lambda _db, _row: [4, 5])
    monkeypatch.setattr(admin_legacy, "_sync_movil_unidades", lambda *_args: None)
    row = MovilRow()
    db = FakeDb(row)
    payload = MovilUpdate(unidad_ids=[4, 5])

    response = asyncio.run(admin_legacy.update_movil(17, payload, db=db, _=object()))

    assert response.unidad_ids == [4, 5]
    assert response.id_unidad_negocio == 4
    assert db.commits == 1


def test_update_movil_id_unidad_negocio_resyncs_pivot_when_no_unidad_ids(monkeypatch):
    sync_calls: list = []
    monkeypatch.setattr(admin_legacy, "_sync_movil_unidades", lambda db, row, ids: sync_calls.append((row.idMovil, list(ids))))
    row = MovilRow()
    db = FakeDb(row)
    payload = MovilUpdate(id_unidad_negocio=8)

    asyncio.run(admin_legacy.update_movil(17, payload, db=db, _=object()))

    assert sync_calls == [(17, [8])]


def test_create_movil_uses_first_unidad_id_as_principal(monkeypatch):
    sync_calls: list = []
    monkeypatch.setattr(admin_legacy, "_sync_movil_unidades", lambda db, row, ids: (sync_calls.append(list(ids)), setattr(row, "idUnidadNegocio", ids[0] if ids else row.idUnidadNegocio)))
    monkeypatch.setattr(admin_legacy, "_to_movil_response", lambda _db, row: MovilResponse(
        idMovil=row.idMovil or 99,
        patente=row.Patente or "",
        detalle=row.Detalle or "",
        tipo_proceso=row.tipo_proceso or "1",
        id_unidad_negocio=int(row.idUnidadNegocio or 1),
        unidad_ids=[int(row.idUnidadNegocio or 1)],
        cant_neumaticos=int(row.CantNeumaticos or 0),
        capacidad_tanque=int(row.capacidad_tanque or 0),
        consumo_promedio=float(row.consumo_promedio or 0),
        tipo_movil=int(row.tipo_movil or 1),
        anio_fabricacion=int(row.anio_fabricacion or 0),
        nro_chasis=row.nro_chasis or "",
        nro_motor=row.nro_motor or "",
        venc_tecnica=row.VencTecnica,
        ruta=bool(row.Ruta),
        venc_ruta=row.VencRuta,
        activo=int(row.activo or 0),
        observaciones=row.observaciones,
    ))
    row = MovilRow()
    db = FakeDb(row)

    asyncio.run(
        admin_legacy.create_movil(
            MovilCreate(patente="AA111", detalle="TRACTOR", unidad_ids=[3, 4, 5]),
            db=db,
            _=object(),
        )
    )

    assert sync_calls and sync_calls[0] == [3, 4, 5]
