"""dashboard/urls.py"""

from django.urls import path
from dashboard.views import dashboard_view, stats_api

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
    path("api/stats/", stats_api, name="dashboard-stats"),
]
