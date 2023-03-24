
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import os

import django

django.setup()

# from channels.rounting import get_default_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'login_with_face.settings'
django_asgi_app = get_asgi_application()

import chat.routings
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routings.websocket_urlpatterns
        )
    )
})
