from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app


def test_root_returns_project_welcome_message():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to registro_produccion"}


def test_health_returns_instance_and_database_status(monkeypatch):
    monkeypatch.setattr(main_module.settings, "APP_INSTANCE", "indufor")
    monkeypatch.setattr(main_module.settings, "APP_VERSION", "test-commit")
    monkeypatch.setattr(main_module, "check_database_health", lambda: True)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "registro_produccion"
    assert data["instance"] == "indufor"
    assert data["database"] == "ok"
    assert data["version"] == "test-commit"
    assert "time" in data
    assert "DATABASE_URL" not in data


def test_health_returns_unhealthy_when_database_check_fails(monkeypatch):
    monkeypatch.setattr(main_module.settings, "APP_INSTANCE", "produccion_fg")
    monkeypatch.setattr(main_module.settings, "EXPECTED_DB_NAME", "")
    monkeypatch.setattr(main_module, "check_database_health", lambda: False)
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["status"] == "error"
    assert response.json()["instance"] == "produccion_fg"
    assert response.json()["database"] == "error"


def test_health_reports_expected_database_name_match(monkeypatch):
    monkeypatch.setattr(main_module.settings, "APP_INSTANCE", "indufor_demo")
    monkeypatch.setattr(main_module.settings, "EXPECTED_DB_NAME", "indufor_demo")
    monkeypatch.setattr(main_module, "check_database_health", lambda: True)
    monkeypatch.setattr(main_module, "get_current_database_name", lambda: "indufor_demo")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "ok"
    assert data["database_name"] == {
        "expected": "indufor_demo",
        "actual": "indufor_demo",
        "matches": True,
    }
    assert "DATABASE_URL" not in data


def test_health_fails_when_expected_database_name_mismatches(monkeypatch):
    monkeypatch.setattr(main_module.settings, "APP_INSTANCE", "indufor_demo")
    monkeypatch.setattr(main_module.settings, "EXPECTED_DB_NAME", "indufor_demo")
    monkeypatch.setattr(main_module, "check_database_health", lambda: True)
    monkeypatch.setattr(main_module, "get_current_database_name", lambda: "indufor")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "error"
    assert data["database"] == "ok"
    assert data["database_name"]["matches"] is False
    assert data["database_name"]["actual"] == "indufor"
