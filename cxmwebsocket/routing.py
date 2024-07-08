from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/redirect/', consumers.Router.as_asgi()),
    path('ws/conversation/', consumers.ConversationConsumer.as_asgi()),
    path('ws/config/', consumers.NotificationConsumer.as_asgi()),
    path('ws/post/', consumers.ConversationRedirectToUser.as_asgi()),
]
