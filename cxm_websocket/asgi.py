import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from cxmwebsocket.routing import websocket_urlpatterns

django.setup()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cxm_websocket.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket":
        URLRouter(
            websocket_urlpatterns
        ),
})
