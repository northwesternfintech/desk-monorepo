import pytest
import asyncio
import json
from websockets.asyncio.server import serve, Server, ServerConnection
from typing import AsyncGenerator
from pysrc.util.websocket import WebSocketClient


class MockWebSocketClient(WebSocketClient):
    def __init__(self, base_url: str):
        super().__init__(base_url)
        self.messages: list[dict] = []

    async def on_connect(self) -> None:
        subscribe_message = {"event": "subscribe", "feed": "test_feed"}
        assert self.ws is not None, "WebSocket can't be None."
        await self.ws.send(json.dumps(subscribe_message))

    async def on_disconnect(self) -> None:
        pass

    async def on_message(self, message: dict) -> None:
        self.messages.append(message)


@pytest.fixture
async def mock_server() -> AsyncGenerator[Server, None]:
    async def handler(connection: ServerConnection) -> None:
        async for message in connection:
            data = json.loads(message)
            if data.get("event") == "subscribe":
                await connection.send(
                    json.dumps({"event": "subscribed", "feed": data["feed"]})
                )
            else:
                await connection.send(
                    json.dumps({"feed": "test_feed", "data": "update"})
                )

    server = await serve(handler, "localhost", 0)
    server.sockets
    try:
        yield server
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_mock_websocket_client(mock_server: AsyncGenerator[Server, None]) -> None:
    server_instance = await mock_server.__anext__()
    port = list(server_instance.sockets)[0].getsockname()[1]

    client = MockWebSocketClient(f"ws://localhost:{port}")
    client.start()

    try:
        await asyncio.sleep(1)  

        assert len(client.messages) > 0, "Client should have received messages."
        assert any(
            msg.get("event") == "subscribed" for msg in client.messages
        ), "Client did not receive subscription confirmation."
        assert any(
            msg.get("feed") == "test_feed" for msg in client.messages
        ), "Client did not receive test feed updates."
    finally:
        if client._listener_task:
            client._listener_task.cancel()

        server_instance.close()
        await server_instance.wait_closed()
