from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.db.session import SessionLocal
from app.domain.enums import NextSlot, TournamentStage
from app.models.match import Match
from app.models.team import Team
from app.models.tournament import Tournament


TOURNAMENT_NAME = "FIFA World Cup 2026"
TOURNAMENT_YEAR = 2026


def main() -> None:
    with SessionLocal() as db:
        tournament = db.scalar(
            select(Tournament).where(
                Tournament.name == TOURNAMENT_NAME,
                Tournament.year == TOURNAMENT_YEAR,
            )
        )
        if tournament is None:
            tournament = Tournament(
                name=TOURNAMENT_NAME,
                year=TOURNAMENT_YEAR,
                is_active=True,
            )
            db.add(tournament)
            db.flush()

        existing_matches = db.scalar(
            select(Match).where(Match.tournament_id == tournament.id).limit(1)
        )
        if existing_matches is not None:
            print("Development seed already exists; nothing to do.")
            return

        teams = list(
            db.scalars(
                select(Team)
                .where(Team.tournament_id == tournament.id)
                .order_by(Team.name.asc())
            )
        )
        for index in range(len(teams) + 1, 33):
            team = Team(
                tournament_id=tournament.id,
                name=f"Seed Team {index:02d}",
                short_name=f"T{index:02d}",
                fifa_code=f"T{index:02d}",
            )
            db.add(team)
            teams.append(team)
        db.flush()
        teams = teams[:32]

        start = datetime(2026, 7, 1, 18, 0, tzinfo=UTC)
        round_of_32 = _create_stage(
            tournament_id=tournament.id,
            stage=TournamentStage.ROUND_OF_32,
            count=16,
            start=start,
            teams=teams,
        )
        round_of_16 = _create_stage(
            tournament_id=tournament.id,
            stage=TournamentStage.ROUND_OF_16,
            count=8,
            start=start + timedelta(days=5),
        )
        quarter_finals = _create_stage(
            tournament_id=tournament.id,
            stage=TournamentStage.QUARTER_FINAL,
            count=4,
            start=start + timedelta(days=9),
        )
        semi_finals = _create_stage(
            tournament_id=tournament.id,
            stage=TournamentStage.SEMI_FINAL,
            count=2,
            start=start + timedelta(days=13),
        )
        final = _create_stage(
            tournament_id=tournament.id,
            stage=TournamentStage.FINAL,
            count=1,
            start=start + timedelta(days=17),
        )

        matches = round_of_32 + round_of_16 + quarter_finals + semi_finals + final
        db.add_all(matches)
        db.flush()

        _link_stage(round_of_32, round_of_16)
        _link_stage(round_of_16, quarter_finals)
        _link_stage(quarter_finals, semi_finals)
        _link_stage(semi_finals, final)

        db.commit()
        print("Development seed created.")


def _create_stage(
    *,
    tournament_id,
    stage: TournamentStage,
    count: int,
    start: datetime,
    teams: list[Team] | None = None,
) -> list[Match]:
    matches: list[Match] = []
    for position in range(1, count + 1):
        team_index = (position - 1) * 2
        match = Match(
            tournament_id=tournament_id,
            stage=stage,
            bracket_position=position,
            home_team_id=teams[team_index].id if teams else None,
            away_team_id=teams[team_index + 1].id if teams else None,
            scheduled_at=start + timedelta(hours=position - 1),
        )
        matches.append(match)
    return matches


def _link_stage(source: list[Match], target: list[Match]) -> None:
    for index, match in enumerate(source):
        next_match = target[index // 2]
        match.next_match_id = next_match.id
        match.next_match_slot = NextSlot.HOME if index % 2 == 0 else NextSlot.AWAY


if __name__ == "__main__":
    main()
