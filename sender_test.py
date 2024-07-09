token = "ABdrF-EKrBH6qAiN36PKELSrgvPOzaTYzw:1599849320938"

import asyncio
import websockets
import json

async def send_message():
    # async with websockets.connect("ws://localhost:8000/ws/conversation/?token=IntcInVzZXJfaWRcIjogNTMxLCBcImNvbXBhbnlfaWRcIjogOTd9Ig:1sPj9Q:kxjiMR5f0yPnyNdccSxRtRHJuil4YPANqRxQvCM1GTE") as websocket:
    async with websockets.connect("ws://localhost:8008/ws/redirect/") as websocket:
        message = "Hello, WebSocket!"
        await websocket.send(json.dumps({"channel_type": "send_notification_message", "channel_name":"notification_1_669", "data": {"y": "23"}}))
        # await websocket.send("hello")
        print(f"Sent message: {message}")

        response = await websocket.recv()
        print(f"Received message: {response}")

asyncio.get_event_loop().run_until_complete(send_message())