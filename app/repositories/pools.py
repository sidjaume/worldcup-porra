from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.enums import ParticipantStatus, PoolRole
from app.models.pool import Pool, PoolParticipant


class PoolsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_pool(
        self,
        *,
        tournament_id: UUID,
        owner_user_id: UUID,
        name: str,
        invite_code_hash: str,
    ) -> Pool:
        now = datetime.now(UTC)
        pool = Pool(
            tournament_id=tournament_id,
            owner_user_id=owner_user_id,
            name=name,
            invite_code_hash=invite_code_hash,
            invite_code_last_rotated_at=now,
            is_active=True,
        )
        self.db.add(pool)
        self.db.flush()
        self.db.add(
            PoolParticipant(
                pool_id=pool.id,
                user_id=owner_user_id,
                role=PoolRole.OWNER,
                status=ParticipantStatus.ACTIVE,
                joined_at=now,
            )
        )
        self.db.flush()
        return pool

    def list_for_user(self, user_id: UUID) -> list[tuple[Pool, PoolRole, int]]:
        participant_count = (
            select(
                PoolParticipant.pool_id,
                func.count(PoolParticipant.id).label("participant_count"),
            )
            .where(PoolParticipant.status == ParticipantStatus.ACTIVE)
            .group_by(PoolParticipant.pool_id)
            .subquery()
        )
        rows = self.db.execute(
            select(Pool, PoolParticipant.role, participant_count.c.participant_count)
            .join(PoolParticipant, PoolParticipant.pool_id == Pool.id)
            .join(participant_count, participant_count.c.pool_id == Pool.id)
            .where(
                PoolParticipant.user_id == user_id,
                PoolParticipant.status == ParticipantStatus.ACTIVE,
                Pool.is_active.is_(True),
            )
            .order_by(Pool.created_at.desc())
        )
        return [(pool, role, int(count)) for pool, role, count in rows]

    def get(self, pool_id: UUID) -> Pool | None:
        return self.db.get(Pool, pool_id)

    def get_by_invite_hash(self, invite_code_hash: str) -> Pool | None:
        return self.db.scalar(
            select(Pool).where(
                Pool.invite_code_hash == invite_code_hash,
                Pool.is_active.is_(True),
            )
        )

    def get_participant(
        self,
        *,
        pool_id: UUID,
        user_id: UUID,
    ) -> PoolParticipant | None:
        return self.db.scalar(
            select(PoolParticipant).where(
                PoolParticipant.pool_id == pool_id,
                PoolParticipant.user_id == user_id,
            )
        )

    def add_participant(
        self,
        *,
        pool_id: UUID,
        user_id: UUID,
        role: PoolRole = PoolRole.PARTICIPANT,
    ) -> PoolParticipant:
        participant = PoolParticipant(
            pool_id=pool_id,
            user_id=user_id,
            role=role,
            status=ParticipantStatus.ACTIVE,
            joined_at=datetime.now(UTC),
        )
        self.db.add(participant)
        self.db.flush()
        return participant

    def list_participants(self, pool_id: UUID) -> list[PoolParticipant]:
        return list(
            self.db.scalars(
                select(PoolParticipant)
                .where(
                    PoolParticipant.pool_id == pool_id,
                    PoolParticipant.status == ParticipantStatus.ACTIVE,
                )
                .order_by(PoolParticipant.joined_at.asc())
            )
        )

    def participant_count(self, pool_id: UUID) -> int:
        return int(
            self.db.scalar(
                select(func.count(PoolParticipant.id)).where(
                    PoolParticipant.pool_id == pool_id,
                    PoolParticipant.status == ParticipantStatus.ACTIVE,
                )
            )
            or 0
        )

    def rotate_invite_code(self, pool: Pool, invite_code_hash: str) -> None:
        pool.invite_code_hash = invite_code_hash
        pool.invite_code_last_rotated_at = datetime.now(UTC)
        self.db.flush()

