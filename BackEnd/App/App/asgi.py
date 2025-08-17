"""
ASGI config for App project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from authentication.middleware import JWTAuthMiddleware, RateLimitMiddleware
from tutoring_sessions.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')

# Create middleware stack
websocket_middleware = RateLimitMiddleware(
    JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    )
)

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": websocket_middleware,
})
