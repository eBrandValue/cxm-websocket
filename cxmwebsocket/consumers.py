import logging
import urllib
import demjson3
import random
import string

from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer

LOGGER = logging.getLogger(__name__)


class BaseConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.company_id = None
        self.user_id = None
        super(BaseConsumer, self).__init__(*args, **kwargs)

    async def receive(self, text_data):
        if text_data == '__ping__':
            await self.send(text_data="__pong__")

    def initial_parse(self):
        try:
            token = [t for t in self.scope["headers"] if t[0].startswith(b'sec-websocket-protocol')][0][1].decode()
            keys = token.split(", ")
            LOGGER.info("keys", keys)
            if keys and keys[1] == settings.HANDSHAKE_TOKEN and keys[0] == "cxm":
                query_dict = urllib.parse.parse_qs(self.scope['query_string'])
                LOGGER.info("query_dict", query_dict)
                self.company_id = query_dict[b"companyId"][0].decode()
                self.user_id = query_dict[b"userId"][0].decode()
                if self.company_id and self.user_id:
                    return True
        except Exception as e:
            LOGGER.error("Error when parsing initial WS connection URI, %s" % e)

        return False


class NotificationConsumer(BaseConsumer):
    CHANNEL_NAME = "notification"

    @property
    def group_name(self):
        return "%s_%s_%s" % (self.CHANNEL_NAME, self.company_id, self.user_id)

    async def connect(self):
        if self.initial_parse():
            await self.accept("cxm")
            LOGGER.info("%s connected to %s" % (self.user_id, self.group_name))  # user email
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.CHANNEL_NAME, self.channel_name)
        LOGGER.info("%s disconnected from %s" % (self.company_id, self.CHANNEL_NAME))

    async def send_notification_message(self, event):
        await self.send_json(event["data"])


class ConversationConsumer(BaseConsumer):
    CHANNEL_NAME = "conversation"

    @property
    def group_name(self):
        return "%s_%s" % (self.CHANNEL_NAME, self.company_id)

    async def connect(self):
        if self.initial_parse():
            await self.accept("cxm")
            LOGGER.info("%s connected to %s" % (self.user_id, self.group_name))  # user email
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.CHANNEL_NAME, self.channel_name)
        LOGGER.info("%s disconnected from %s" % (self.company_id, self.CHANNEL_NAME))

    async def send_conversation_to_user(self, event):
        await self.send_json(event["data"])


class ConversationRedirectToUser(BaseConsumer):
    @property
    def group_name(self):
        return "user_%s_%s" % (self.company_id, self.user_id)

    async def connect(self):
        if self.initial_parse():
            await self.accept("cxm")
            LOGGER.info("%s connected to %s" % (self.user_id, self.group_name))  # user email
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        LOGGER.info("%s disconnected from %s" % (self.company_id, self.group_name))

    async def send_conversation_to_user(self, event):
        await self.send_json(event["data"])


class Router(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = None

    @staticmethod
    def generate_name(length=7):
        characters = string.ascii_letters + string.digits + '-.'
        return ''.join(random.choice(characters) for _ in range(length))

    async def connect(self):
        try:
            keys = [t for t in self.scope["headers"] if t[0].startswith(b'sec-websocket-key')]
            self.name = keys[0][1].decode().replace("=", "").replace("/", "").replace("+", "")
        except Exception as e:
            LOGGER.error("Error occurred when generating client name, error: %s" % e)
            self.name = self.generate_name()

        await self.channel_layer.group_add(
            self.name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = text_data
        if type(data) is str and (data == '__ping__' or data == '"__ping__"'):
            await self.send(text_data="__pong__")
        else:
            LOGGER.info("Received updated data, sending it to the groups. data: %s", data)
            data = demjson3.decode(data)
            channel_type = data.get("channel_type")
            channel_name = data.get("channel_name")
            await self.channel_layer.group_send(channel_name, {"type": channel_type, "data": data.get("data")})
