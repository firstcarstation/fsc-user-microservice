from fastapi import FastAPI

from app.api.api_v1.routes import api_router
from app.core.config import settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
