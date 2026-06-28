from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config.settings import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.users import UsersRepository
from app.services.auth_service import AuthService
from app.services.errors import UnauthorizedError


bearer_scheme = HTTPBearer(auto_error=False)


def settings_dependency() -> Settings:
    return get_settings()


def db_dependency() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Authentication is required.")
    auth_service = AuthService(db, settings)
    user_id = auth_service.verify_access_token(credentials.credentials)
    user = UsersRepository(db).get(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("User is not active.")
    return user

