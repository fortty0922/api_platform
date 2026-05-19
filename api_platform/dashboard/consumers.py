"""
dashboard/consumers.py — WebSocket consumer for real-time dashboard push.

Connects clients to the 'dashboard' group and broadcasts stats every 3 seconds.
"""

import asyncio
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.db.models import Max

logger = logging.getLogger(__name__)

PUSH_INTERVAL = 3  # seconds between each push


class DashboardConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "dashboard"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()
        logger.info("Dashboard WS connected: %s", self.channel_name)
        # Start background push loop
        self._push_task = asyncio.ensure_future(self._push_loop())

    async def disconnect(self, close_code):
        self._push_task.cancel()
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)
        logger.info("Dashboard WS disconnected: %s (code=%s)", self.channel_name, close_code)

    # ── Message handler (group broadcast) ─────────────────────────────────────
    async def dashboard_update(self, event):
        """Called when group_send sends a 'dashboard.update' message."""
        await self.send(text_data=event["payload"])

    # ── Background push loop ───────────────────────────────────────────────────
    async def _push_loop(self):
        """Gather stats and broadcast to all connected clients every PUSH_INTERVAL seconds."""
        try:
            while True:
                data = await self._gather_stats()
                payload = json.dumps(data, ensure_ascii=False, default=str)
                await self.channel_layer.group_send(
                    self.GROUP_NAME,
                    {"type": "dashboard.update", "payload": payload},
                )
                await asyncio.sleep(PUSH_INTERVAL)
        except asyncio.CancelledError:
            pass

    # ── Stats collection (sync DB calls run in thread pool) ───────────────────
    async def _gather_stats(self) -> dict:
        from asgiref.sync import sync_to_async
        return await sync_to_async(self._collect_stats_sync)()

    @staticmethod
    def _collect_stats_sync() -> dict:
        """All ORM queries — runs in Django's thread pool via sync_to_async."""
        from django.utils import timezone as dj_tz
        from posts.models import Post
        from sync_worker.models import ExternalPost

        now = dj_tz.now()
        total_synced = ExternalPost.objects.count()
        last_synced_at = ExternalPost.objects.aggregate(t=Max("synced_at"))["t"]
        user_count = User.objects.count()
        post_count = Post.objects.count()

        recent_ext = list(
            ExternalPost.objects.order_by("-synced_at").values(
                "ext_id", "author", "category", "views", "synced_at"
            )[:5]
        )
        for p in recent_ext:
            p["synced_at"] = p["synced_at"].isoformat() if p["synced_at"] else None

        recent_user = list(
            Post.objects.select_related("author")
            .order_by("-created_at")
            .values("id", "title", "author__username", "created_at")[:5]
        )
        for p in recent_user:
            p["created_at"] = p["created_at"].isoformat() if p["created_at"] else None

        # Scheduler next_run
        next_run = None
        try:
            from sync_worker.scheduler import _scheduler
            if _scheduler and _scheduler.running:
                job = _scheduler.get_job("sync_external_posts")
                if job and job.next_run_time:
                    next_run = job.next_run_time.isoformat()
        except Exception:
            pass

        return {
            "server_time": now.isoformat(),
            "sync": {
                "total_synced": total_synced,
                "last_synced_at": last_synced_at.isoformat() if last_synced_at else None,
                "next_run": next_run,
                "scheduler_running": next_run is not None,
            },
            "users": {"total": user_count},
            "posts": {"total": post_count},
            "recent_external_posts": recent_ext,
            "recent_user_posts": recent_user,
        }
