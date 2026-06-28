from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, get_current_user
from app.api.schemas.users import UserRead, UserUpdate
from app.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(
    request: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(db_dependency),
) -> User:
    current_user.display_name = request.display_name
    db.commit()
    db.refresh(current_user)
    return current_user

