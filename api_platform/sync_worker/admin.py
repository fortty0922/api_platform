from django.contrib import admin

from sync_worker.models import ExternalPost


@admin.register(ExternalPost)
class ExternalPostAdmin(admin.ModelAdmin):
    list_display = ("ext_id", "author", "category", "views", "reports", "synced_at")
    list_filter = ("category",)
    search_fields = ("ext_id", "author", "content")
    readonly_fields = ("ext_id", "synced_at", "created_at")
    ordering = ("-synced_at",)
