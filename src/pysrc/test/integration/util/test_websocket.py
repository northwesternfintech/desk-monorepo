import pytest
import asyncio
import json
from websockets.asyncio.server import serve, Server
from typing import AsyncGenerator, List
from pysrc.util.websocket import WebSocketClient


class MockWebSocketClient(WebSocketClient):
    def __init__(self, base_url: str):
        super().__init__(base_url)
        self.messages: List[dict] = []

    async def on_connect(self) -> None:
        subscribe_message = {"event": "subscribe", "feed": "test_feed"}
        await self.ws.send(json.dumps(subscribe_message))

    async def on_disconnect(self) -> None:
        pass

    async def on_message(self, message: dict) -> None:
        self.messages.append(message)


@pytest.fixture
async def mock_server() -> Server:
    async def handler(websocket, path):
        async for message in websocket:
            data = json.loads(message)
            if data.get("event") == "subscribe":
                await websocket.send(
                    json.dumps({"event": "subscribed", "feed": data["feed"]})
                )
            else:
                await websocket.send(
                    json.dumps({"feed": "test_feed", "data": "update"})
                )

    server = await serve(handler, "localhost", 0)
    server.sockets
    yield server

    server.close()
    await server.wait_closed()
