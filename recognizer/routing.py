from django.urls import re_path

from .consumers import AsyncStreamConsumer

websocket_urlpatterns = [
    re_path(r'', AsyncStreamConsumer.as_asgi()),
]