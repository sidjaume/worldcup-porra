from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.errors import DomainError, PredictionLockedError
from app.services.errors import ServiceError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ServiceError)
    async def service_error_handler(
        request: Request,
        exc: ServiceError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": {}}},
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        status_code = 409 if isinstance(exc, PredictionLockedError) else 400
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.__class__.__name__,
                    "message": str(exc),
                    "details": {},
                }
            },
        )

