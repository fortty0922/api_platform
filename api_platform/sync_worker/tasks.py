"""
tasks.py — The ETL pipeline

Steps:
  1. FETCH  : HTTP GET /external/stream with X-API-KEY from env
  2. FILTER : Skip records where flagged=True OR metrics.reports > 10
  3. MASK   : Replace any [...] bracketed text in content with [REDACTED]
  4. FLATTEN: Extract metrics.views / metrics.reports to top-level
  5. UPSERT : update_or_create on ext_id (idempotent)
"""

import logging
import os
import re

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)

# Read at call-time (not import-time) so that dotenv has already been loaded
# by Django settings before these values are consumed.
# For open source safety, we do NOT default to localhost anymore.
_DEFAULT_URL = None
REQUEST_TIMEOUT = 10  # seconds


# ── Regex for data masking ─────────────────────────────────────────────────────
BRACKET_PATTERN = re.compile(r"\[.*?\]")


# ── Pipeline helpers ───────────────────────────────────────────────────────────

def _fetch_raw() -> list[dict]:
    """Call the external API and return the raw `data` array."""
    api_url = os.environ.get("EXTERNAL_API_URL", _DEFAULT_URL)
    
    if not api_url:
        logger.warning("⚠️ EXTERNAL_API_URL is not set in .env! Skipping fetch.")
        return []

    api_key = os.environ.get("EXTERNAL_API_KEY", "")
    headers = {"X-API-KEY": api_key}
    try:
        response = requests.get(api_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("❌ Failed to fetch from %s: %s", api_url, e)
        return []

    payload = response.json()
    logger.info(
        "✅ [FETCH] status=%s  timestamp=%s  records=%d",
        payload.get("status"),
        payload.get("timestamp"),
        len(payload.get("data", [])),
    )
    logger.debug("Raw payload: %s", payload)
    return payload.get("data", [])


def _filter_item(item: dict) -> bool:
    """
    Return True if the item should be KEPT.
    Milestone 2: skip flagged=True OR reports > 10.
    """
    flagged = item.get("flagged", False)
    reports = item.get("metrics", {}).get("reports", 0)

    if flagged:
        logger.info("🚫 [FILTER] Skipping flagged item id=%s", item.get("id"))
        return False
    if reports > 10:
        logger.info(
            "🚫 [FILTER] Skipping high-report item id=%s (reports=%d)",
            item.get("id"),
            reports,
        )
        return False
    return True


def _transform(item: dict) -> dict:
    """
    Milestone 2 — Mask bracketed metadata & flatten the schema.
    Returns a dict ready to be passed to ExternalPost.update_or_create.
    """
    raw_content = item.get("content", "")
    masked_content = BRACKET_PATTERN.sub("[REDACTED]", raw_content)

    metrics = item.get("metrics", {})
    return {
        "ext_id": item["id"],
        "author": item.get("author", ""),
        "content": masked_content,
        "category": item.get("category", ""),
        "views": metrics.get("views", 0),
        "reports": metrics.get("reports", 0),
    }


def _upsert(record: dict) -> None:
    """
    Milestone 3 — Idempotent INSERT-or-UPDATE using Django's update_or_create.
    Lookup key : ext_id
    Update fields: all other columns (synced_at updated automatically via auto_now)
    """
    from sync_worker.models import ExternalPost  # late import to avoid AppRegistryNotReady

    ext_id = record.pop("ext_id")
    obj, created = ExternalPost.objects.update_or_create(
        ext_id=ext_id,
        defaults=record,
    )
    action = "INSERT" if created else "UPDATE"
    logger.info("💾 [UPSERT] %s id=%s author=%s", action, ext_id, obj.author)


# ── Main task (called by scheduler every minute) ───────────────────────────────

def sync_external_posts() -> None:
    """
    Full ETL pipeline: fetch → filter → transform → upsert.
    All exceptions are caught here so the scheduler never crashes.
    """
    logger.info("⏰ [SYNC] Starting sync job at %s", timezone.now().isoformat())

    try:
        raw_items = _fetch_raw()

        kept = [item for item in raw_items if _filter_item(item)]
        logger.info(
            "📊 [ETL] %d total / %d kept after filter", len(raw_items), len(kept)
        )

        for item in kept:
            transformed = _transform(item)
            _upsert(transformed)

        logger.info("✅ [SYNC] Job completed successfully.")

    except requests.exceptions.Timeout:
        logger.error("❌ [SYNC] Request timed out — will retry next cycle.")
    except requests.exceptions.ConnectionError as exc:
        logger.error("❌ [SYNC] Connection error: %s", exc)
    except requests.exceptions.HTTPError as exc:
        logger.error(
            "❌ [SYNC] HTTP error %s: %s", exc.response.status_code, exc
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("❌ [SYNC] Unexpected error: %s", exc)
