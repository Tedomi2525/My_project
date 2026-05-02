from collections.abc import Iterable

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.core.config import CORS_ORIGINS
from app.database import engine


def create_service_app(
    *,
    title: str,
    routers: Iterable[APIRouter],
    create_tables: bool = False,
) -> FastAPI:
    if create_tables:
        models.Base.metadata.create_all(bind=engine)

    app = FastAPI(title=title)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in routers:
        app.include_router(router)

    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": title}

    return app
