from datetime import date

import pytest

from app.seed import demo_data


def test_seed_aborts_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_INSTANCE", "indufor_demo")
    monkeypatch.setenv("ALLOW_DEMO_SEED", "true")

    with pytest.raises(demo_data.DemoSeedSafetyError, match="production"):
        demo_data.validate_seed_environment()


def test_seed_aborts_without_explicit_allow(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("APP_INSTANCE", "indufor_demo")
    monkeypatch.setenv("ALLOW_DEMO_SEED", "false")

    with pytest.raises(demo_data.DemoSeedSafetyError, match="ALLOW_DEMO_SEED"):
        demo_data.validate_seed_environment()


def test_seed_dry_run_does_not_print_secrets(monkeypatch, capsys):
    secret_url = "mysql://demo_user:super-secret-password@demo-db:3306/indufor_demo"
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("APP_INSTANCE", "indufor_demo")
    monkeypatch.setenv("ALLOW_DEMO_SEED", "true")
    monkeypatch.setenv("DATABASE_URL", secret_url)
    monkeypatch.setenv("DEMO_SEED_RECORDS", "3")

    exit_code = demo_data.main(["--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "super-secret-password" not in captured.out
    assert secret_url not in captured.out
    assert "indufor_demo" in captured.out


def test_demo_dataset_uses_clearly_fake_names():
    dataset = demo_data.build_demo_dataset(record_count=5, today=date(2026, 6, 17))

    personal_names = [row["Nombre"] for row in dataset.personal]
    mobile_names = [row["Detalle"] for row in dataset.moviles]
    production_names = [row["operador"] for row in dataset.produccion]
    production_ids = [row["id"] for row in dataset.produccion]

    assert "Admin Demo" in personal_names
    assert "Encargado Demo" in personal_names
    assert "Operador Demo 01" in personal_names
    assert "Movil Demo 01" in mobile_names
    assert set(production_names) <= set(personal_names)
    assert all("Demo" in name for name in personal_names + mobile_names + production_names)
    assert production_ids == [900001, 900002, 900003, 900004, 900005]


def test_mysql_foreign_key_checks_are_session_scoped(monkeypatch):
    executed = []

    class FakeSession:
        def execute(self, statement):
            executed.append(str(statement))

    monkeypatch.setattr(demo_data.settings, "DATABASE_URL", "mysql://user:pass@host/db")

    assert demo_data._set_mysql_foreign_key_checks(FakeSession(), enabled=False) is True
    assert demo_data._set_mysql_foreign_key_checks(FakeSession(), enabled=True) is True
    assert executed == ["SET FOREIGN_KEY_CHECKS=0", "SET FOREIGN_KEY_CHECKS=1"]


def test_foreign_key_checks_are_not_changed_for_non_mysql(monkeypatch):
    class FakeSession:
        def execute(self, statement):
            raise AssertionError("execute should not be called for non-MySQL URLs")

    monkeypatch.setattr(demo_data.settings, "DATABASE_URL", "sqlite:///demo.db")

    assert demo_data._set_mysql_foreign_key_checks(FakeSession(), enabled=False) is False
