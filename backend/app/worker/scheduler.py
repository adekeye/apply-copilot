"""
APScheduler wrapper — runs the discovery job every hour.

The scheduler is started by FastAPI on startup (embedded mode).
It can also run as a standalone process via `python worker.py`.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.worker.discovery import run_discovery

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler(timezone="UTC")
    return _scheduler


def start_scheduler() -> None:
    scheduler = get_scheduler()
    if scheduler.running:
        return

    scheduler.add_job(
        run_discovery,
        trigger=IntervalTrigger(hours=1),
        id="job_discovery",
        name="Hourly job discovery",
        replace_existing=True,
        misfire_grace_time=300,  # allow up to 5 min late start before skipping
    )
    scheduler.start()
    logger.info("[scheduler] Started — job discovery will run every hour.")


def stop_scheduler() -> None:
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[scheduler] Stopped.")
