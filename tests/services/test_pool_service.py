from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.domain.enums import ParticipantStatus, PoolRole
from app.services.errors import ForbiddenError, NotFoundError, ValidationError
from app.services.pool_service import PoolService


class FakeDb:
    def __init__(self) -> None:
        self.committed = False
        self.refreshed = None

    def commit(self) -> None:
        self.committed = True

    def refresh(self, item) -> None:
        self.refreshed = item


class FakePoolsRepository:
    def __init__(self, *, pool, owner_participant, participant=None) -> None:
        self.pool = pool
        self.owner_participant = owner_participant
        self.participant = participant

    def get(self, pool_id):
        if pool_id == self.pool.id:
            return self.pool
        return None

    def get_participant(self, *, pool_id, user_id):
        if pool_id != self.pool.id:
            return None
        if user_id == self.owner_participant.user_id:
            return self.owner_participant
        if self.participant is not None and user_id == self.participant.user_id:
            return self.participant
        return None


def service_with_repo(repo: FakePoolsRepository, db: FakeDb | None = None) -> PoolService:
    service = PoolService(db or FakeDb(), SimpleNamespace())
    service.pools = repo
    return service


def owner_participant(user_id):
    return SimpleNamespace(
        user_id=user_id,
        role=PoolRole.OWNER,
        status=ParticipantStatus.ACTIVE,
    )


def test_update_pool_mutates_pool_and_refreshes_in_service() -> None:
    owner_user_id = uuid4()
    pool = SimpleNamespace(
        id=uuid4(),
        owner_user_id=owner_user_id,
        name="Office Pool",
        is_active=True,
    )
    db = FakeDb()
    service = service_with_repo(
        FakePoolsRepository(
            pool=pool,
            owner_participant=owner_participant(owner_user_id),
        ),
        db,
    )

    updated = service.update_pool(
        pool_id=pool.id,
        user_id=owner_user_id,
        name="Updated Pool",
        is_active=False,
    )

    assert updated is pool
    assert pool.name == "Updated Pool"
    assert pool.is_active is False
    assert db.committed is True
    assert db.refreshed is pool


def test_get_member_pool_rejects_inactive_pool() -> None:
    owner_user_id = uuid4()
    pool = SimpleNamespace(
        id=uuid4(),
        owner_user_id=owner_user_id,
        name="Office Pool",
        is_active=False,
    )
    service = service_with_repo(
        FakePoolsRepository(
            pool=pool,
            owner_participant=owner_participant(owner_user_id),
        )
    )

    with pytest.raises(ForbiddenError):
        service.get_member_pool(pool_id=pool.id, user_id=owner_user_id)


def test_update_pool_allows_owner_to_reactivate_inactive_pool() -> None:
    owner_user_id = uuid4()
    pool = SimpleNamespace(
        id=uuid4(),
        owner_user_id=owner_user_id,
        name="Office Pool",
        is_active=False,
    )
    db = FakeDb()
    service = service_with_repo(
        FakePoolsRepository(
            pool=pool,
            owner_participant=owner_participant(owner_user_id),
        ),
        db,
    )

    updated = service.update_pool(
        pool_id=pool.id,
        user_id=owner_user_id,
        name=None,
        is_active=True,
    )

    assert updated is pool
    assert pool.is_active is True
    assert db.committed is True
    assert db.refreshed is pool


def test_owner_actions_other_than_update_reject_inactive_pool() -> None:
    owner_user_id = uuid4()
    participant_user_id = uuid4()
    pool = SimpleNamespace(id=uuid4(), owner_user_id=owner_user_id, is_active=False)
    participant = SimpleNamespace(
        user_id=participant_user_id,
        role=PoolRole.PARTICIPANT,
        status=ParticipantStatus.ACTIVE,
        removed_at=None,
    )
    service = service_with_repo(
        FakePoolsRepository(
            pool=pool,
            owner_participant=owner_participant(owner_user_id),
            participant=participant,
        )
    )

    with pytest.raises(ForbiddenError):
        service.remove_participant(
            pool_id=pool.id,
            owner_user_id=owner_user_id,
            participant_user_id=participant_user_id,
        )


def test_remove_participant_marks_active_participant_removed() -> None:
    owner_user_id = uuid4()
    participant_user_id = uuid4()
    pool = SimpleNamespace(id=uuid4(), owner_user_id=owner_user_id, is_active=True)
    participant = SimpleNamespace(
        user_id=participant_user_id,
        role=PoolRole.PARTICIPANT,
        status=ParticipantStatus.ACTIVE,
        removed_at=None,
    )
    db = FakeDb()
    service = service_with_repo(
        FakePoolsRepository(
            pool=pool,
            owner_participant=owner_participant(owner_user_id),
            participant=participant,
        ),
        db,
    )

    service.remove_participant(
        pool_id=pool.id,
        owner_user_id=owner_user_id,
        participant_user_id=participant_user_id,
    )

    assert participant.status == ParticipantStatus.REMOVED
    assert participant.removed_at is not None
    assert participant.removed_at.tzinfo == UTC
    assert db.committed is True


def test_remove_participant_rejects_owner_self_removal() -> None:
    owner_user_id = uuid4()
    pool = SimpleNamespace(id=uuid4(), owner_user_id=owner_user_id, is_active=True)
    service = service_with_repo(
        FakePoolsRepository(
            pool=pool,
            owner_participant=owner_participant(owner_user_id),
        )
    )

    with pytest.raises(ValidationError):
        service.remove_participant(
            pool_id=pool.id,
            owner_user_id=owner_user_id,
            participant_user_id=owner_user_id,
        )


def test_remove_participant_rejects_missing_participant() -> None:
    owner_user_id = uuid4()
    pool = SimpleNamespace(id=uuid4(), owner_user_id=owner_user_id, is_active=True)
    service = service_with_repo(
        FakePoolsRepository(
            pool=pool,
            owner_participant=owner_participant(owner_user_id),
        )
    )

    with pytest.raises(NotFoundError):
        service.remove_participant(
            pool_id=pool.id,
            owner_user_id=owner_user_id,
            participant_user_id=uuid4(),
        )


def test_remove_participant_rejects_inactive_participant() -> None:
    owner_user_id = uuid4()
    participant_user_id = uuid4()
    pool = SimpleNamespace(id=uuid4(), owner_user_id=owner_user_id, is_active=True)
    participant = SimpleNamespace(
        user_id=participant_user_id,
        role=PoolRole.PARTICIPANT,
        status=ParticipantStatus.REMOVED,
        removed_at=datetime(2026, 6, 29, tzinfo=UTC),
    )
    service = service_with_repo(
        FakePoolsRepository(
            pool=pool,
            owner_participant=owner_participant(owner_user_id),
            participant=participant,
        )
    )

    with pytest.raises(ForbiddenError):
        service.remove_participant(
            pool_id=pool.id,
            owner_user_id=owner_user_id,
            participant_user_id=participant_user_id,
        )
