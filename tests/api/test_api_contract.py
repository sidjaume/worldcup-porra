from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.main import app
from app.db.session import get_db


class FakeConnection:
    def execute(self, statement) -> None:
        assert str(statement) == str(text("SELECT 1"))


class FakeDb:
    def connect(self) -> "FakeDb":
        return self

    def __enter__(self) -> FakeConnection:
        return FakeConnection()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass


def override_db() -> Generator[None, None, None]:
    yield None


def test_health_endpoint_returns_ok(monkeypatch) -> None:
    monkeypatch.setattr("app.api.main.engine", FakeDb())

    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_protected_endpoint_returns_standard_unauthorized_error() -> None:
    app.dependency_overrides[get_db] = override_db
    try:
        response = TestClient(app).get("/api/v1/users/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Authentication is required.",
            "details": {},
        }
    }


def test_google_start_requires_redirect_uri() -> None:
    response = TestClient(app).get("/api/v1/auth/google/start")

    assert response.status_code == 422

