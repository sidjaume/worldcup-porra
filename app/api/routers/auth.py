from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.dependencies import db_dependency, settings_dependency
from app.api.schemas.auth import (
    AuthResponse,
    ExchangeCodeRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from app.config.settings import Settings
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/start")
def google_start(
    redirect_uri: str = Query(...),
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> RedirectResponse:
    url = AuthService(db, settings).google_start_url(redirect_uri)
    return RedirectResponse(url=url)


@router.get("/google/callback")
def google_callback(
    code: str,
    state: str,
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> RedirectResponse:
    redirect_uri, exchange_code = AuthService(db, settings).handle_google_callback(
        code=code,
        state=state,
    )
    separator = "&" if "?" in redirect_uri else "?"
    return RedirectResponse(
        url=f"{redirect_uri}{separator}{urlencode({'code': exchange_code})}"
    )


@router.post("/exchange", response_model=AuthResponse)
def exchange_code(
    request: ExchangeCodeRequest,
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> dict:
    return AuthService(db, settings).exchange_code(request.code)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: RefreshRequest,
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> dict:
    return AuthService(db, settings).refresh(request.refresh_token)


@router.post("/logout", status_code=204)
def logout(
    request: LogoutRequest,
    db: Session = Depends(db_dependency),
    settings: Settings = Depends(settings_dependency),
) -> None:
    AuthService(db, settings).logout(request.refresh_token)

