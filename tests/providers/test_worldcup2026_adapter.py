import pytest

from app.domain.enums import MatchStatus, TournamentStage
from app.providers.worldcup2026 import ProviderError, WorldCup2026Adapter


class PayloadAdapter(WorldCup2026Adapter):
    def __init__(self, payloads):
        super().__init__(base_url="https://example.test")
        self.payloads = payloads

    def _get(self, path: str):
        payload = self.payloads[path]
        if isinstance(payload, dict):
            for key in ("data", "games", "matches", "teams", "results"):
                if isinstance(payload.get(key), list):
                    return payload[key]
        return payload


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
                    "status": "scheduled",
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


def test_adapter_accepts_current_provider_wrappers_and_field_names() -> None:
    adapter = PayloadAdapter(
        {
            "/teams": {
                "teams": [
                    {
                        "id": "1",
                        "name_en": "Mexico",
                        "fifa_code": "MEX",
                        "flag": "https://flagcdn.com/w80/mx.png",
                    },
                    {
                        "id": "20",
                        "name_en": "Ecuador",
                        "fifa_code": "ECU",
                    },
                    {
                        "id": "unused",
                        "name_en": "Unused Team",
                        "fifa_code": "ZZZ",
                    },
                ]
            },
            "/games": {
                "games": [
                    {
                        "id": "79",
                        "type": "r32",
                        "local_date": "06/30/2026 19:00",
                        "time_elapsed": "notstarted",
                        "home_team_id": "1",
                        "away_team_id": "20",
                    },
                    {
                        "id": "89",
                        "type": "r16",
                        "local_date": "07/04/2026 17:00",
                        "finished": "FALSE",
                        "home_team_id": "14",
                        "away_team_id": "0",
                    },
                    {
                        "id": "101",
                        "type": "third",
                        "local_date": "07/18/2026 17:00",
                        "time_elapsed": "notstarted",
                    },
                ]
            },
        }
    )

    matches = adapter.fetch_matches(2026)
    teams = adapter.fetch_teams(2026)

    assert [match.provider_ref for match in matches] == ["79", "89"]
    assert matches[0].stage == TournamentStage.ROUND_OF_32
    assert matches[0].status == MatchStatus.SCHEDULED
    assert matches[0].scheduled_at.isoformat() == "2026-06-30T19:00:00+00:00"
    assert matches[1].away_team_provider_ref is None
    assert {team.provider_ref for team in teams} == {"1", "20"}
    assert teams[0].name == "Mexico"
    assert teams[0].flag_url == "https://flagcdn.com/w80/mx.png"


def test_adapter_treats_nested_zero_team_refs_as_tbd() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                {
                    "id": "99",
                    "type": "qf",
                    "local_date": "07/11/2026 17:00",
                    "time_elapsed": "notstarted",
                    "home_team": {"id": "0"},
                    "awayTeam": {"id": 0},
                }
            ]
        }
    )

    matches = adapter.fetch_matches(2026)

    assert matches[0].home_team_provider_ref is None
    assert matches[0].away_team_provider_ref is None


def test_adapter_parses_live_minute_only_for_in_progress_matches() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                {
                    "id": "live",
                    "type": "r32",
                    "local_date": "06/30/2026 19:00",
                    "status": "live",
                    "minute": "67",
                },
                {
                    "id": "scheduled",
                    "type": "r32",
                    "local_date": "06/30/2026 21:00",
                    "status": "scheduled",
                    "minute": "12",
                },
                {
                    "id": "stoppage",
                    "type": "r32",
                    "local_date": "07/01/2026 19:00",
                    "status": "in_progress",
                    "minute": "45+2",
                },
            ]
        }
    )

    matches = adapter.fetch_matches(2026)

    assert matches[0].status == MatchStatus.IN_PROGRESS
    assert matches[0].live_minute == 67
    assert matches[1].live_minute is None
    assert matches[2].live_minute is None


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
                    "status": "scheduled",
                    "home_team_id": "esp",
                    "away_team_id": "por",
                }
            ],
        }
    )

    with pytest.raises(ProviderError):
        adapter.fetch_teams(2026)


def test_adapter_raises_on_unknown_status() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                _completed_match(
                    status="abandoned",
                    score={"home_score": 1, "away_score": 0},
                    winner_team_id="esp",
                )
            ],
        }
    )

    with pytest.raises(ProviderError, match="unknown status"):
        adapter.fetch_matches(2026)


def test_adapter_raises_on_missing_status() -> None:
    payload = _completed_match(
        score={"home_score": 1, "away_score": 0},
        winner_team_id="esp",
    )
    del payload["status"]
    adapter = PayloadAdapter({"/games": [payload]})

    with pytest.raises(ProviderError, match="missing status"):
        adapter.fetch_matches(2026)


def test_adapter_preserves_zero_zero_nested_score_with_winner() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                _completed_match(
                    score={"home_score": 0, "away_score": 0},
                    winner_team_id="por",
                )
            ],
        }
    )

    matches = adapter.fetch_matches(2026)

    assert matches[0].home_score == 0
    assert matches[0].away_score == 0
    assert matches[0].winner_provider_ref == "por"


def test_adapter_preserves_one_sided_zero_nested_score() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                _completed_match(
                    score={"home_score": 0, "away_score": 2},
                    winner_team_id="por",
                )
            ],
        }
    )

    matches = adapter.fetch_matches(2026)

    assert matches[0].home_score == 0
    assert matches[0].away_score == 2
    assert matches[0].winner_provider_ref == "por"


def test_adapter_raises_on_completed_match_missing_winner() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                _completed_match(
                    score={"home_score": 1, "away_score": 1},
                    winner_team_id=None,
                )
            ],
        }
    )

    with pytest.raises(ProviderError, match="missing winner"):
        adapter.fetch_matches(2026)


def test_adapter_derives_missing_completed_winner_from_decisive_score() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                _completed_match(
                    score={"home_score": 0, "away_score": 2},
                    winner_team_id=None,
                )
            ],
        }
    )

    matches = adapter.fetch_matches(2026)

    assert matches[0].winner_provider_ref == "por"


def test_adapter_still_requires_winner_for_completed_tie() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                _completed_match(
                    score={"home_score": 1, "away_score": 1},
                    winner_team_id=None,
                )
            ],
        }
    )

    with pytest.raises(ProviderError, match="missing winner"):
        adapter.fetch_matches(2026)


def test_adapter_uses_penalties_only_for_tied_completed_winner() -> None:
    payload = _completed_match(
        score={"home_score": 1, "away_score": 1},
        winner_team_id=None,
    )
    payload["home_penalty_score"] = "3"
    payload["away_penalty_score"] = "4"
    adapter = PayloadAdapter({"/games": [payload]})

    matches = adapter.fetch_matches(2026)

    assert matches[0].home_score == 1
    assert matches[0].away_score == 1
    assert matches[0].winner_provider_ref == "por"


def test_adapter_raises_on_completed_match_missing_score() -> None:
    adapter = PayloadAdapter(
        {
            "/games": [
                _completed_match(
                    score={"home_score": 2},
                    winner_team_id="esp",
                )
            ],
        }
    )

    with pytest.raises(ProviderError, match="missing scores"):
        adapter.fetch_matches(2026)


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


def _completed_match(
    *,
    score: dict[str, int],
    winner_team_id: str | None,
    status: str = "finished",
) -> dict[str, object]:
    match: dict[str, object] = {
        "id": "m73",
        "type": "Round of 32",
        "match_number": 73,
        "date": "2026-06-28T18:00:00Z",
        "status": status,
        "home_team_id": "esp",
        "away_team_id": "por",
        "score": score,
    }
    if winner_team_id is not None:
        match["winner_team_id"] = winner_team_id
    return match
