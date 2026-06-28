from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str
    avatar_url: str | None = None


class UserUpdate(BaseModel):
    display_name: str
