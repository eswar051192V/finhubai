"""Scheduled maintenance hooks (IST)."""

from __future__ import annotations

import logging
from datetime import date, datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from backend.config import get_settings
from backend.db import session_scope
from backend.models import PipelineRun

log = logging.getLogger(__name__)
IST = ZoneInfo("Asia/Kolkata")


def _log_run(job_name: str, status: str, detail: str | None = None) -> None:
    try:
        with session_scope() as session:
            session.add(PipelineRun(job_name=job_name, status=status, detail=detail))
    except Exception as e:
        log.warning("pipeline db log failed: %s", e)


def pre_market_refresh() -> None:
    log.info("pre_market_refresh %s", date.today().isoformat())
    _log_run("pre_market_refresh", "ok", date.today().isoformat())


def intraday_tick() -> None:
    log.info("intraday_tick %s", datetime.now(IST).isoformat())
    _log_run("intraday_tick", "ok", datetime.now(IST).isoformat())


def eod_refresh() -> None:
    log.info("eod_refresh %s", date.today().isoformat())
    _log_run("eod_refresh", "ok", date.today().isoformat())


def build_scheduler() -> BackgroundScheduler:
    settings = get_settings()
    sched = BackgroundScheduler(timezone=IST)
    # Cron-style hooks; refine market hours later
    sched.add_job(pre_market_refresh, "cron", hour=8, minute=0)
    sched.add_job(
        intraday_tick,
        "interval",
        minutes=5,
        id="intraday_interval",
        replace_existing=True,
    )
    sched.add_job(eod_refresh, "cron", hour=18, minute=0)
    _ = settings  # future: feature flags
    return sched
