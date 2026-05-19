"""
ASGI config for api_platform project.

Supports both HTTP (Django) and WebSocket (Django Channels) protocols.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_platform.settings')

# Initialize Django ASGI application early so AppRegistry is populated.
django_asgi_app = get_asgi_application()

from dashboard.routing import websocket_urlpatterns  # noqa: E402 (must be after django init)

application = ProtocolTypeRouter({
    # Regular HTTP requests → Django
    "http": django_asgi_app,
    # WebSocket requests → Channels router
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
