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
            LOGGER.info("keys: %s" % keys)
            if keys and keys[1] == settings.HANDSHAKE_TOKEN and keys[0] == "cxm":
                query_dict = urllib.parse.parse_qs(self.scope['query_string'])
                LOGGER.info("query_dict: %s" % query_dict)
                self.company_id = query_dict[b"companyId"][0].decode()
                self.user_id = query_dict[b"userId"][0].decode()
                if self.company_id and self.user_id:
                    return True
        except Exception as e:
            LOGGER.error("Error when parsing initial WS connection URI, %s" % e)

        return False


class Consumerinho(BaseConsumer):
    CHANNEL_NAME = "cxm"

    @property
    def company_group(self):
        return "%s_company_%s" % (self.CHANNEL_NAME, self.company_id)

    @property
    def user_group(self):
        return "%s_user_%s" % (self.CHANNEL_NAME, self.user_id)

    async def connect(self):
        if self.initial_parse():
            await self.accept("cxm")
            await self.channel_layer.group_add(self.company_group, self.channel_name)
            await self.channel_layer.group_add(self.user_group, self.channel_name)
            LOGGER.info("%s connected to %s and %s" % (self.user_id, self.company_group, self.user_group))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.company_group, self.channel_name)
        await self.channel_layer.group_discard(self.user_group, self.channel_name)
        LOGGER.info("%s disconnected from %s and %s" % (self.user_id, self.company_group, self.user_group))

    async def send_to_user(self, event):
        await self.send_json(event["data"])

    async def send_to_company(self, event):
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
            decoded_data = demjson3.decode(data)
            data = decoded_data.get("data")
            channel_type, channel_name = decoded_data.get("channel_type"), decoded_data.get("channel_name")
            await self.channel_layer.group_send(channel_name, {"type": channel_type, "data": data})
