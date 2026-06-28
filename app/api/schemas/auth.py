from pydantic import BaseModel

from app.api.schemas.users import UserRead


class ExchangeCodeRequest(BaseModel):
    code: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class AuthResponse(TokenResponse):
    user: UserRead

