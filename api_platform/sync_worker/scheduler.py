"""
scheduler.py — APScheduler setup

Creates a BackgroundScheduler that runs sync_external_posts() every 1 minute.
Called once from SyncWorkerConfig.ready() on server startup.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def start() -> None:
    """Start the background scheduler (idempotent — safe to call once)."""
    global _scheduler  # noqa: PLW0603

    from sync_worker.tasks import sync_external_posts  # avoid circular import

    if _scheduler and _scheduler.running:
        logger.warning("[SCHEDULER] Already running — skipping start.")
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        sync_external_posts,
        trigger=IntervalTrigger(minutes=1),
        id="sync_external_posts",
        name="Sync External Posts every 1 minute",
        replace_existing=True,
        max_instances=1,       # prevent overlap if a run takes >1 minute
    )
    _scheduler.start()
    logger.info("⏱️  [SCHEDULER] Started — sync job will run every 1 minute.")
