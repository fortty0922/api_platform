"""
URL configuration for api_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from mock_api.views import stream_view

from core.views import help_api_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # Mock external API — simulates third-party data source for local testing
    path('external/stream', stream_view, name='external-stream'),
    # Help / API Directory
    path('api/help/', help_api_view, name='api-help'),
    # User registration
    path('api/auth/', include('users.urls')),
    # Posts (list, create)
    path('api/posts/', include('posts.urls')),
    # Post Operations (put, patch, delete)
    path('api/operations/posts/', include('post_operations.urls')),
    # Server monitoring dashboard
    path('dashboard/', include('dashboard.urls')),
]

# Serve uploaded media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

