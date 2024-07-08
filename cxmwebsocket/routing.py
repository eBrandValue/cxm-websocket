from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/hello/', consumers.MyConsumer.as_asgi()),
]
