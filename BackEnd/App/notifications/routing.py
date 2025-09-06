from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    # Anchor at start and allow optional trailing slash
    re_path(r'^ws/notifications/?$', consumers.NotificationConsumer.as_asgi()),
    # Also add explicit non-regex paths to avoid any regex edge cases
    path('ws/notifications', consumers.NotificationConsumer.as_asgi()),
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]
