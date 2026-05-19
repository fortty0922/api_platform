"""
apps.py — SyncWorkerConfig

Starts the APScheduler inside ready() so it boots automatically
when Django starts, without any manual HTTP trigger.
"""

import logging
import os

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class SyncWorkerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sync_worker"
    verbose_name = "Sync Worker"

    def ready(self) -> None:
        """
        Called once by Django after all apps are loaded.
        We start the scheduler here so the cron job is active from
        the first request onwards (and with runserver --noreload there
        is exactly one scheduler instance).
        """
        # Skip scheduler during manage.py commands (migrate, shell, etc.)
        # to avoid accidental DB access before migrations are applied.
        import sys

        skip_commands = {"migrate", "makemigrations", "shell", "test", "collectstatic"}
        if any(cmd in sys.argv for cmd in skip_commands):
            logger.info("[SYNC_WORKER] Skipping scheduler start during management command.")
            return

        # Also skip when Django is running in the auto-reloader child watcher
        # (RUN_MAIN=true means we are inside the real server process).
        # This prevents the scheduler from starting twice with --reload.
        if os.environ.get("RUN_MAIN") != "true" and "runserver" in sys.argv:
            return

        from sync_worker import scheduler  # noqa: PLC0415

        scheduler.start()
