from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app import main as main_module
from app.main import DATABASE_ERROR_DETAIL, SERVER_ERROR_DETAIL, app


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


def test_database_errors_return_safe_message_without_sql():
    route_path = "/__test__/database-error-safe-message"

    if not any(getattr(route, "path", None) == route_path for route in app.routes):
        app.add_api_route(route_path, broken_database_route, methods=["GET"])

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get(route_path)

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail == DATABASE_ERROR_DETAIL
    assert "SELECT" not in detail
    assert "personal" not in detail
    assert "Lost connection" not in detail


def test_global_exception_handler_hides_sql_details():
    route_path = "/__test__/sql-error"

    if not any(getattr(route, "path", None) == route_path for route in app.routes):
        @app.get(route_path)
        async def sql_error_route():
            raise RuntimeError("pymysql.err.OperationalError: SELECT password_hash FROM usuarios")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get(route_path)

    assert response.status_code == 500
    assert response.json() == {"detail": SERVER_ERROR_DETAIL}
    assert "pymysql" not in response.text
    assert "SELECT" not in response.text
    assert "password_hash" not in response.text


async def broken_database_route():
    raise OperationalError(
        "SELECT personal.idPersonal FROM personal WHERE personal.idPersonal = %(idPersonal_1)s",
        {"idPersonal_1": 951},
        Exception("Lost connection to MySQL server during query"),
    )
