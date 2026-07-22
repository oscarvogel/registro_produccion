from datetime import date
import asyncio
from types import SimpleNamespace
from contextlib import contextmanager

import pytest
from pydantic import ValidationError

from app.api.routes import produccion
from app.schemas.produccion import TableroProduccionCreate


def test_create_accepts_legacy_path_without_redirect():
    create_paths = {
        route.path
        for route in produccion.router.routes
        if "POST" in getattr(route, "methods", set())
    }

    assert "/produccion" in create_paths
    assert "/produccion/" in create_paths


def test_create_schema_accepts_form_uuid_for_idempotent_retries():
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 21),
        form_uuid="offline-uuid-7",
    )

    assert payload.form_uuid == "offline-uuid-7"


def test_form_uuid_is_limited_to_database_column_length():
    with pytest.raises(ValidationError):
        TableroProduccionCreate(
            fecha=date(2026, 7, 21),
            form_uuid="x" * 40,
        )


class DuplicateQuery:
    def __init__(self, existing):
        self.existing = existing

    def filter(self, *_args):
        return self

    def first(self):
        return self.existing


class DuplicateDb:
    def __init__(self, existing):
        self.existing = existing
        self.add_called = False
        self.is_active = True

    def query(self, *_args):
        return DuplicateQuery(self.existing)

    def add(self, _row):
        self.add_called = True


class ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar(self):
        return self.value


class LockDb:
    def __init__(self, value=1):
        self.value = value
        self.calls = []

    def execute(self, statement, params):
        self.calls.append((str(statement), params))
        return ScalarResult(self.value)

    def close(self):
        self.calls.append(("CLOSE", {}))


class LockBind:
    def __init__(self, connection):
        self.connection = connection

    def connect(self):
        return self.connection


class SessionWithBind:
    def __init__(self, connection):
        self.bind = LockBind(connection)

    def get_bind(self):
        return self.bind


def test_form_submission_lock_uses_mysql_named_lock():
    db = LockDb()

    assert produccion._acquire_form_submission_lock(db, "registro_produccion:create") is True
    produccion._release_form_submission_lock(db, "registro_produccion:create")

    assert "GET_LOCK" in db.calls[0][0]
    assert "RELEASE_LOCK" in db.calls[1][0]


def test_form_submission_lock_keeps_one_dedicated_connection_until_release():
    connection = LockDb()
    session = SessionWithBind(connection)

    with produccion._form_submission_lock(session, "registro_produccion:create"):
        assert "GET_LOCK" in connection.calls[0][0]
        assert all("RELEASE_LOCK" not in statement for statement, _ in connection.calls)

    assert "RELEASE_LOCK" in connection.calls[-2][0]
    assert connection.calls[-1][0] == "CLOSE"


def test_create_returns_existing_record_for_a_retried_form_uuid(monkeypatch):
    existing = SimpleNamespace(id=42, form_uuid="offline-uuid-7")
    db = DuplicateDb(existing)
    monkeypatch.setattr(produccion, "_validate_restricted_payload", lambda *_args: None)
    @contextmanager
    def no_lock(*_args):
        yield

    monkeypatch.setattr(produccion, "_form_submission_lock", no_lock)
    payload = TableroProduccionCreate(
        fecha=date(2026, 7, 21),
        form_uuid="offline-uuid-7",
    )

    result = asyncio.run(produccion.create_produccion(payload, db=db, user=SimpleNamespace()))

    assert result is existing
    assert db.add_called is False
