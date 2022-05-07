import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
# from channels.rounting import get_default_application
import django
from channels.auth import AuthMiddlewareStack
import recognizer.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'login_with_face.settings')
django.setup()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            recognizer.routing.websocket_urlpatterns
        )
    )
})