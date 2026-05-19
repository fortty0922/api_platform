from django.db import models


class ExternalPost(models.Model):
    """
    Stores sanitized & flattened data fetched from the external /external/stream API.
    The `ext_id` field is the idempotency key — we upsert on it.
    """

    ext_id = models.CharField(max_length=100, unique=True, db_index=True)
    author = models.CharField(max_length=255)
    content = models.TextField()          # [REDACTED] applied before save
    category = models.CharField(max_length=100)

    # Flattened from metrics { views, reports }
    views = models.IntegerField(default=0)
    reports = models.IntegerField(default=0)

    synced_at = models.DateTimeField(auto_now=True)   # updated on every upsert
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-synced_at"]
        verbose_name = "External Post"
        verbose_name_plural = "External Posts"

    def __str__(self):
        return f"[{self.ext_id}] {self.author}: {self.content[:60]}"
