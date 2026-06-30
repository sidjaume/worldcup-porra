from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.errors import register_error_handlers
from app.api.routers import admin, auth, ops, pools, predictions, rankings, tournaments, users
from app.config.settings import get_settings
from app.db.session import engine


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="World Cup Pool API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(pools.router, prefix="/api/v1")
    app.include_router(tournaments.router, prefix="/api/v1")
    app.include_router(predictions.router, prefix="/api/v1")
    app.include_router(rankings.router, prefix="/api/v1")
    app.include_router(admin.router, prefix="/api/v1")
    app.include_router(ops.router, prefix="/api/v1")

    @app.get("/health")
    def health() -> dict[str, str]:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}

    return app


app = create_app()
