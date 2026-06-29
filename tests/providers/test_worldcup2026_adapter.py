import pytest

from app.domain.enums import MatchStatus, TournamentStage
from app.providers.worldcup2026 import ProviderError, WorldCup2026Adapter


class PayloadAdapter(WorldCup2026Adapter):
    def __init__(self, payloads):
        super().__init__(base_url="https://example.test")
        self.payloads = payloads

    def _get(self, path: str):
        return self.payloads[path]


def test_adapter_filters_knockout_matches_and_derives_stage_positions() -> None:
    adapter = PayloadAdapter(
        {
            "/teams": [
                {"id": "esp", "name": "Spain", "code": "ESP"},
                {"id": "bra", "name": "Brazil", "code": "BRA"},
                {"id": "por", "name": "Portugal", "code": "POR"},
                {"id": "jpn", "name": "Japan", "code": "JPN"},
                {"id": "phi", "name": "Philippines", "code": "PHI"},
            ],
            "/games": [
                {
                    "id": "g1",
                    "type": "Group Stage",
                    "match_number": 1,
                    "date": "2026-06-11T18:00:00Z",
                },
                {
                    "id": "m74",
                    "type": "Round of 32",
                    "match_number": 74,
                    "date": "2026-06-29T18:00:00Z",
                    "home_team_id": "esp",
                    "away_team_id": "por",
                },
                {
                    "id": "m73",
                    "type": "Round of 32",
                    "match_number": 73,
                    "date": "2026-06-28T18:00:00Z",
                    "status": "finished",
                    "home_team_id": "bra",
                    "away_team_id": "jpn",
                    "home_score": 1,
                    "away_score": 1,
                    "winner_team_id": "jpn",
                },
            ],
        }
    )

    matches = adapter.fetch_matches(2026)

    assert [match.provider_ref for match in matches] == ["m73", "m74"]
    assert [match.bracket_position for match in matches] == [1, 2]
    assert matches[0].stage == TournamentStage.ROUND_OF_32
    assert matches[0].status == MatchStatus.COMPLETED
    assert matches[0].winner_provider_ref == "jpn"
    assert {team.provider_ref for team in adapter.fetch_teams(2026)} == {
        "bra",
        "esp",
        "jpn",
        "por",
    }


def test_adapter_raises_on_malformed_team_record() -> None:
    adapter = PayloadAdapter(
        {
            "/teams": [
                {"id": "esp", "name": "Spain", "code": "ESP"},
                {"id": "", "name": "Missing Ref"},
            ],
            "/games": [
                {
                    "id": "m73",
                    "type": "Round of 32",
                    "match_number": 73,
                    "date": "2026-06-28T18:00:00Z",
                    "home_team_id": "esp",
                    "away_team_id": "por",
                }
            ],
        }
    )

    with pytest.raises(ProviderError):
        adapter.fetch_teams(2026)


def test_adapter_raises_on_unexpected_payload_shape(monkeypatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"unexpected": true}'

    def fake_urlopen(request, timeout):  # noqa: ARG001
        return FakeResponse()

    monkeypatch.setattr("app.providers.worldcup2026.urllib.request.urlopen", fake_urlopen)

    adapter = WorldCup2026Adapter(base_url="https://example.test")

    with pytest.raises(ProviderError):
        adapter._get("/games")
