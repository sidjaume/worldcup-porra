from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.enums import ParticipantStatus, PoolRole
from app.repositories.pools import PoolsRepository
from app.repositories.tournaments import TournamentsRepository
from app.services.errors import ConflictError, ForbiddenError, NotFoundError
from app.services.security import SecurityService
from app.config.settings import Settings


class PoolService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.security = SecurityService(settings)
        self.pools = PoolsRepository(db)
        self.tournaments = TournamentsRepository(db)

    def create_pool(self, *, user_id: UUID, tournament_id: UUID, name: str) -> tuple:
        if self.tournaments.get_tournament(tournament_id) is None:
            raise NotFoundError("Tournament not found.")

        for _ in range(5):
            invite_code = self.security.create_invite_code()
            try:
                pool = self.pools.create_pool(
                    tournament_id=tournament_id,
                    owner_user_id=user_id,
                    name=name,
                    invite_code_hash=self.security.token_hash(invite_code),
                )
                self.db.commit()
                return pool, invite_code
            except IntegrityError:
                self.db.rollback()
        raise ConflictError("Could not generate a unique invite code.")

    def list_user_pools(self, user_id: UUID) -> list[tuple]:
        return self.pools.list_for_user(user_id)

    def get_member_pool(self, *, pool_id: UUID, user_id: UUID):
        pool = self.pools.get(pool_id)
        if pool is None:
            raise NotFoundError("Pool not found.")
        participant = self.pools.get_participant(pool_id=pool_id, user_id=user_id)
        if participant is None or participant.status != ParticipantStatus.ACTIVE:
            raise ForbiddenError("You are not a participant in this pool.")
        return pool, participant

    def require_owner(self, *, pool_id: UUID, user_id: UUID):
        pool, participant = self.get_member_pool(pool_id=pool_id, user_id=user_id)
        if participant.role != PoolRole.OWNER:
            raise ForbiddenError("Only the pool owner can perform this action.")
        return pool

    def join_by_invite_code(self, *, user_id: UUID, invite_code: str):
        pool = self.pools.get_by_invite_hash(self.security.token_hash(invite_code))
        if pool is None:
            raise NotFoundError("Pool not found for invite code.")
        participant = self.pools.get_participant(pool_id=pool.id, user_id=user_id)
        if participant is not None:
            if participant.status == ParticipantStatus.ACTIVE:
                return pool, participant
            participant.status = ParticipantStatus.ACTIVE
            participant.removed_at = None
            self.db.commit()
            return pool, participant
        participant = self.pools.add_participant(pool_id=pool.id, user_id=user_id)
        self.db.commit()
        return pool, participant

    def list_participants(self, *, pool_id: UUID, user_id: UUID):
        self.get_member_pool(pool_id=pool_id, user_id=user_id)
        return self.pools.list_participants(pool_id)

    def rotate_invite_code(self, *, pool_id: UUID, user_id: UUID) -> str:
        pool = self.require_owner(pool_id=pool_id, user_id=user_id)
        for _ in range(5):
            invite_code = self.security.create_invite_code()
            try:
                self.pools.rotate_invite_code(pool, self.security.token_hash(invite_code))
                self.db.commit()
                return invite_code
            except IntegrityError:
                self.db.rollback()
        raise ConflictError("Could not generate a unique invite code.")

