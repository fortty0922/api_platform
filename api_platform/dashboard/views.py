"""dashboard/views.py — Status monitoring console."""

import json
from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone as dj_timezone

from posts.models import Post
from sync_worker.models import ExternalPost


def dashboard_view(request):
    """Render the main dashboard HTML page."""
    return render(request, "dashboard/index.html")


def stats_api(request):
    """
    GET /dashboard/api/stats/
    Returns real-time system metrics as JSON.
    Polled every 10 seconds by the dashboard frontend.
    """
    now = dj_timezone.now()

    # ── Sync worker stats ─────────────────────────────────────────────────────
    total_synced = ExternalPost.objects.count()
    last_synced_at = ExternalPost.objects.aggregate(t=Max("synced_at"))["t"]

    # ── User & post stats ─────────────────────────────────────────────────────
    user_count = User.objects.count()
    post_count = Post.objects.count()

    # ── Recent external posts (last 5) ────────────────────────────────────────
    recent_posts = list(
        ExternalPost.objects.order_by("-synced_at").values(
            "ext_id", "author", "category", "views", "synced_at"
        )[:5]
    )
    for p in recent_posts:
        p["synced_at"] = p["synced_at"].isoformat() if p["synced_at"] else None

    # ── Recent user posts (last 5) ────────────────────────────────────────────
    recent_user_posts = list(
        Post.objects.select_related("author")
        .order_by("-created_at")
        .values("id", "title", "author__username", "created_at")[:5]
    )
    for p in recent_user_posts:
        p["created_at"] = p["created_at"].isoformat() if p["created_at"] else None

    # ── Scheduler next run (read from APScheduler if available) ───────────────
    next_run = None
    try:
        from sync_worker.scheduler import _scheduler
        if _scheduler and _scheduler.running:
            job = _scheduler.get_job("sync_external_posts")
            if job and job.next_run_time:
                next_run = job.next_run_time.isoformat()
    except Exception:
        pass

    return JsonResponse({
        "server_time": now.isoformat(),
        "sync": {
            "total_synced": total_synced,
            "last_synced_at": last_synced_at.isoformat() if last_synced_at else None,
            "next_run": next_run,
            "scheduler_running": next_run is not None,
        },
        "users": {
            "total": user_count,
        },
        "posts": {
            "total": post_count,
        },
        "recent_external_posts": recent_posts,
        "recent_user_posts": recent_user_posts,
    })
