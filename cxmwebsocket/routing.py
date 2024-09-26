from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/redirect/', consumers.Router.as_asgi()),
    path('ws/cxm/', consumers.Consumerinho.as_asgi()),
]
