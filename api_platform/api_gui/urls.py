"""api_gui/urls.py"""
from django.urls import path
from .views import gui_view

urlpatterns = [
    path('', gui_view, name='api-gui'),
]
