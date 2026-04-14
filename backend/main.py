from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import models  # noqa: F401  — register metadata
from backend.config import get_settings
from backend.data.pipeline import build_scheduler
from backend.db import init_extensions_and_tables
from backend.routes import router

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = build_scheduler()
    try:
        init_extensions_and_tables()
        log.info("Database initialized")
    except Exception as e:
        log.warning("Database init skipped or failed: %s", e)
    scheduler.start()
    log.info("Scheduler started")
    yield
    scheduler.shutdown(wait=False)
    log.info("Scheduler stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="FinanceLab API", lifespan=lifespan)
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
