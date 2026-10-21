from pathlib import Path

import os

import pytest

from app import migrate


class FakeCursor:
    def __init__(self, extra_sets=0):
        self.executed = []
        self.nextset_calls = 0
        self._extra_sets = extra_sets
        self._seen = 0
        self._rows = [(1,)]

    def execute(self, sql, params=None):
        self.executed.append(sql)
        if "GET_LOCK" in sql:
            self._rows = [(self._lock_result,)]

    def fetchone(self):
        return self._rows[0]

    def nextset(self):
        self.nextset_calls += 1
        self._seen += 1
        return self._seen <= self._extra_sets

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


class FakeConnection:
    def __init__(self, extra_sets=0, lock_result=1):
        self.cursor_obj = FakeCursor(extra_sets=extra_sets)
        self.cursor_obj._lock_result = lock_result
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def close(self):
        self.closed = True


def test_discover_migrations_only_sql_sorted(tmp_path: Path):
    (tmp_path / "b_migration.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "a_migration.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "notas.txt").write_text("no", encoding="utf-8")

    found = migrate.discover_migrations(tmp_path)

    assert [p.name for p in found] == ["a_migration.sql", "b_migration.sql"]


def test_discover_migrations_missing_dir_returns_empty(tmp_path: Path):
    assert migrate.discover_migrations(tmp_path / "nope") == []


def test_apply_file_executes_and_drains_result_sets(tmp_path: Path):
    script = tmp_path / "m.sql"
    script.write_text("SET @x := 1; PREPARE s FROM @x; EXECUTE s;", encoding="utf-8")
    connection = FakeConnection(extra_sets=2)

    migrate.apply_file(connection, script)

    assert connection.cursor_obj.executed == [script.read_text(encoding="utf-8")]
    # Un nextset como minimo hasta agotar los 2 result sets extra.
    assert connection.cursor_obj.nextset_calls == 3


def test_apply_file_ignores_empty_file(tmp_path: Path):
    script = tmp_path / "empty.sql"
    script.write_text("   \n", encoding="utf-8")
    connection = FakeConnection()

    migrate.apply_file(connection, script)

    assert connection.cursor_obj.executed == []


def test_run_applies_all_files_in_order_and_closes(tmp_path: Path, monkeypatch):
    (tmp_path / "01_first.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "02_second.sql").write_text("SELECT 2;", encoding="utf-8")
    connection = FakeConnection()
    monkeypatch.setattr(migrate, "_connect", lambda: connection)

    applied = migrate.run(tmp_path)

    assert applied == 2
    assert connection.closed is True
    executed = [s for s in connection.cursor_obj.executed if "LOCK" not in s]
    assert executed == ["SELECT 1;", "SELECT 2;"]


def test_run_serializes_with_a_mysql_lock(tmp_path: Path, monkeypatch):
    """produccion_fg e indufor share the same DB: without the lock both
    could apply the same ALTER in the same deploy."""
    (tmp_path / "01_first.sql").write_text("SELECT 1;", encoding="utf-8")
    connection = FakeConnection()
    monkeypatch.setattr(migrate, "_connect", lambda: connection)

    migrate.run(tmp_path)

    executed = connection.cursor_obj.executed
    assert any("GET_LOCK" in statement for statement in executed)
    assert any("RELEASE_LOCK" in statement for statement in executed)


def test_run_fails_when_the_lock_cannot_be_acquired(tmp_path: Path, monkeypatch):
    (tmp_path / "01_first.sql").write_text("SELECT 1;", encoding="utf-8")
    connection = FakeConnection(lock_result=0)
    monkeypatch.setattr(migrate, "_connect", lambda: connection)

    with pytest.raises(migrate.MigrationError, match="lock"):
        migrate.run(tmp_path)
    assert connection.closed is True


def test_run_releases_the_lock_even_when_a_migration_fails(tmp_path: Path, monkeypatch):
    (tmp_path / "01_bad.sql").write_text("BROKEN;", encoding="utf-8")
    connection = FakeConnection()
    monkeypatch.setattr(migrate, "_connect", lambda: connection)

    def boom(_connection, _path):
        raise RuntimeError("syntax error")

    monkeypatch.setattr(migrate, "apply_file", boom)

    with pytest.raises(migrate.MigrationError):
        migrate.run(tmp_path)

    assert any("RELEASE_LOCK" in statement for statement in connection.cursor_obj.executed)
    assert connection.closed is True


def test_run_wraps_failures_in_migration_error(tmp_path: Path, monkeypatch):
    (tmp_path / "01_bad.sql").write_text("BROKEN;", encoding="utf-8")
    connection = FakeConnection()
    monkeypatch.setattr(migrate, "_connect", lambda: connection)

    def boom(_connection, _path):
        raise RuntimeError("syntax error")

    monkeypatch.setattr(migrate, "apply_file", boom)

    with pytest.raises(migrate.MigrationError, match="01_bad.sql"):
        migrate.run(tmp_path)
    assert connection.closed is True


def test_migrations_dir_respects_env_override(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(migrate.settings, "DB_MIGRATIONS_DIR", str(tmp_path), raising=False)

    assert migrate.migrations_dir() == tmp_path


def test_migrations_dir_defaults_to_repo_folder(monkeypatch):
    monkeypatch.setattr(migrate.settings, "DB_MIGRATIONS_DIR", "", raising=False)
    monkeypatch.delenv("DB_MIGRATIONS_DIR", raising=False)

    assert migrate.migrations_dir().name == "db_migrations"


def test_main_returns_one_on_migration_error(monkeypatch):
    def boom(*_args, **_kwargs):
        raise migrate.MigrationError("nope")

    monkeypatch.setattr(migrate, "run", boom)

    assert migrate.main() == 1


def test_load_secret_env_populates_environment(tmp_path: Path, monkeypatch):
    secret = tmp_path / "registro.env"
    secret.write_text(
        'export DATABASE_URL="mysql://u:p@h:3306/db"\n# comentario\nNOTA=1 # inline\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("REGISTRO_ENV_FILE", str(secret))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("NOTA", raising=False)

    migrate._load_secret_env()

    assert os.environ["DATABASE_URL"] == "mysql://u:p@h:3306/db"
    assert os.environ["NOTA"] == "1"


def test_load_secret_env_without_file_is_noop(monkeypatch):
    monkeypatch.delenv("REGISTRO_ENV_FILE", raising=False)

    migrate._load_secret_env()  # no debe lanzar


def test_setting_prefers_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "from-env")

    assert migrate._setting("DATABASE_URL", "fallback") == "from-env"
    assert migrate._setting("NO_EXISTE_XYZ", "fallback") == "fallback"
