"""api_gui/views.py"""
from django.shortcuts import render

def gui_view(request):
    """Render the API GUI Single Page Application."""
    return render(request, 'api_gui/index.html')
