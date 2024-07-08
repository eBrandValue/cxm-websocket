import json
import logging
import urllib
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

LOGGER = logging.getLogger(__name__)


class BaseConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.company_id = None
        self.user_id = None
        super(BaseConsumer, self).__init__(*args, **kwargs)

    async def receive(self, text_data):
        if text_data == '__ping__':
            await self.send(text_data="__pong__")

    async def initial_parse(self):
        try:
            query_dict = urllib.parse.parse_qs(self.scope['query_string'])
            self.company_id = query_dict["b'companyId"][0].decode()
            self.user_id = query_dict["b'userId"][0].decode()
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
            await self.accept()
            LOGGER.info("%s connected to %s" % (self.user_id, self.group_name))  # user email
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.CHANNEL_NAME, self.channel_name)
        LOGGER.info("%s disconnected from %s" % (self.company.name, self.CHANNEL_NAME))

    async def send_notification_message(self, event):
        await self.send_json(event["data"])


class ConversationConsumer(BaseConsumer):
    CHANNEL_NAME = "conversation"

    @property
    def group_name(self):
        return "%s_%s_%s" % (self.CHANNEL_NAME, self.company_id, self.user_id)

    async def connect(self):
        if self.initial_parse():
            await self.accept()
            LOGGER.info("%s connected to %s" % (self.user_id, self.group_name))  # user email
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.CHANNEL_NAME, self.channel_name)
        LOGGER.info("%s disconnected from %s" % (self.company.name, self.CHANNEL_NAME))

    async def send_conversation_to_user(self, event):
        await self.send_json(event["data"])


class ConversationRedirectToUser(BaseConsumer):
    @property
    def group_name(self):
        return "user_%s_%s" % (self.company_id, self.user_id)

    async def connect(self):
        if self.initial_parse():
            await self.accept()
            LOGGER.info("%s connected to %s" % (self.user_id, self.group_name))  # user email
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.CHANNEL_NAME, self.channel_name)
        LOGGER.info("%s disconnected from %s" % (self.company.name, self.CHANNEL_NAME))

    async def send_conversation_to_user(self, event):
        await self.send_json(event["data"])


class Router(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, data):
        if type(data) is str and data == '__ping__':
            await self.send(text_data="__pong__")
        else:
            # channel_layer = get_channel_layer()
            # await channel_layer.group_send("user_58_31")
            # consume json data
            # await self.send(text_data=json.dumps({
            #     'message': text_data
            # }))
            pass
class BaseConsumer2(AsyncWebsocketConsumer):
    def __init__(self):
        self.company_id = None
        self.user_id = None

    @property
    def group_name(self):
        return "conversation_%s_%s" % (self.company_id, self.user_id)  # company id and user id

    async def connect(self):
        query_dict = urllib.parse.parse_qs(self.scope['query_string'])
        self.company_id = query_dict["b'companyId"][0].decode()
        self.user_id = query_dict["b'userId"][0].decode()
        await self.accept()
        LOGGER.info("%s connected to %s" % (self.user_id, self.group_name))  # user email
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def receive(self, text_data):
        if text_data == '__ping__':
            # channel_layer = await get_channel_layer()
            await self.send(text_data="__pong__")
            await self.channel_layer.group_send("user_58_31", {"type": "test", "message": "hello"})
        else:
            await self.send(text_data=json.dumps({
                'message': text_data
            }))

    async def test(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


class MyConsumer(AsyncWebsocketConsumer):
    @property
    def group_name(self):
        return "user_%s_%s" % ("58", "31")

    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        pass

    async def test(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def receive(self, text_data):
        if text_data == '__ping__':
            await self.send(text_data="__pong__")
        else:
            await self.send(text_data=json.dumps({
                'message': text_data
            }))
        # text_data_json = json.loads(text_data)
        # message = text_data_json['message']
