"""
ASGI config for App project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "App.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()


def get_application():
    from channels.routing import ProtocolTypeRouter, URLRouter
    from notifications.routing import websocket_urlpatterns

    return ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": URLRouter(
            websocket_urlpatterns
        ),
    })


application = get_application()
