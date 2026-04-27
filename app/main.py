import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.api_v1.routes import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(os.path.abspath(settings.LOCAL_UPLOAD_DIR), exist_ok=True)
    yield


def create_app() -> FastAPI:
    configure_logging()
    upload_dir = os.path.abspath(settings.LOCAL_UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)

    app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    app.include_router(api_router, prefix="/api/u1")
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")
    return app


app = create_app()
