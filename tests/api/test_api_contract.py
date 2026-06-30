from collections.abc import Generator
from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.main import app
from app.api.routers.tournaments import serialize_match
from app.db.session import get_db
from app.domain.enums import MatchStatus, TournamentStage
from app.models.match import Match
from app.models.team import Team


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
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "Request validation failed."
    assert body["error"]["details"]["errors"][0]["loc"] == ["query", "redirect_uri"]


def test_pool_update_response_schema_matches_contract() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    pool_update_response = schemas["PoolUpdated"]
    assert pool_update_response["required"] == ["id", "name", "is_active"]
    assert set(pool_update_response["properties"]) == {"id", "name", "is_active"}


def test_pool_created_response_schema_matches_contract() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    pool_created_response = schemas["PoolCreated"]
    assert pool_created_response["required"] == [
        "id",
        "name",
        "tournament_id",
        "role",
        "participant_count",
        "created_at",
        "invite_code",
    ]
    assert set(pool_created_response["properties"]) == {
        "id",
        "name",
        "tournament_id",
        "role",
        "participant_count",
        "created_at",
        "invite_code",
    }


def test_pool_detail_response_schema_includes_active_state() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    pool_detail_response = schemas["PoolDetail"]
    assert pool_detail_response["required"] == [
        "id",
        "name",
        "tournament_id",
        "owner_user_id",
        "is_active",
        "participant_count",
        "created_at",
    ]
    assert set(pool_detail_response["properties"]) == {
        "id",
        "name",
        "tournament_id",
        "owner_user_id",
        "is_active",
        "participant_count",
        "created_at",
    }


def test_prediction_schemas_include_predicted_advancing_winner() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    assert "predicted_winner_team_id" in schemas["PredictionRequest"]["properties"]
    assert "predicted_winner_team_id" not in schemas["PredictionRequest"]["required"]
    assert "predicted_winner_team_id" in schemas["PredictionRead"]["properties"]
    assert "predicted_winner_team_id" in schemas["MatchPredictionRead"]["properties"]


def test_admin_match_correction_endpoints_match_contract() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    team_patch = paths["/api/v1/admin/matches/{match_id}/teams"]["patch"]
    status_patch = paths["/api/v1/admin/matches/{match_id}/status"]["patch"]

    assert team_patch["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/UpdateMatchTeamsRequest"
    }
    assert team_patch["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/MatchRead"
    }
    assert status_patch["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/UpdateMatchStatusRequest"
    }
    assert status_patch["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/MatchRead"
    }


def test_admin_match_correction_request_schemas_match_contract() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    team_request = schemas["UpdateMatchTeamsRequest"]
    status_request = schemas["UpdateMatchStatusRequest"]

    assert "required" not in team_request
    assert set(team_request["properties"]) == {"home_team_id", "away_team_id"}
    assert team_request["properties"]["home_team_id"]["anyOf"] == [
        {"type": "string", "format": "uuid"},
        {"type": "null"},
    ]
    assert team_request["properties"]["away_team_id"]["anyOf"] == [
        {"type": "string", "format": "uuid"},
        {"type": "null"},
    ]
    assert status_request["required"] == ["status"]
    assert status_request["properties"]["status"]["enum"] == [
        "scheduled",
        "locked",
        "in_progress",
        "cancelled",
    ]


def test_match_schema_includes_live_minute_and_team_brief_metadata() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    match_read = schemas["MatchRead"]
    team_brief = schemas["TeamBrief"]

    assert "live_minute" in match_read["properties"]
    assert "live_minute" not in match_read["required"]
    assert {"short_name", "fifa_code", "flag_url"}.issubset(
        team_brief["properties"]
    )
    assert team_brief["required"] == ["id", "name"]


def test_serialize_match_includes_team_metadata_and_hides_non_live_minute() -> None:
    tournament_id = uuid4()
    home = Team(
        id=uuid4(),
        tournament_id=tournament_id,
        name="Spain",
        short_name="ESP",
        fifa_code="ESP",
        flag_url="https://example.test/esp.svg",
    )
    away = Team(id=uuid4(), tournament_id=tournament_id, name="Portugal")
    match = Match(
        id=uuid4(),
        tournament_id=tournament_id,
        stage=TournamentStage.ROUND_OF_32,
        bracket_position=1,
        home_team=home,
        away_team=away,
        scheduled_at=datetime(2026, 6, 30, 19, tzinfo=UTC),
        status=MatchStatus.SCHEDULED,
        live_minute=47,
        admin_override=False,
    )

    payload = serialize_match(match)

    assert payload.home_team is not None
    assert payload.home_team.short_name == "ESP"
    assert payload.home_team.fifa_code == "ESP"
    assert payload.home_team.flag_url == "https://example.test/esp.svg"
    assert payload.away_team is not None
    assert payload.away_team.short_name is None
    assert payload.live_minute is None
