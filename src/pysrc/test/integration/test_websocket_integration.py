import pytest
import asyncio
import websockets
import threading
from typing import Optional, Generator, Any
from pysrc.util.websocket_handler import WebSocketClient


class EchoServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.server: Optional[websockets.WebSocketServer] = None
        self.stop_event = asyncio.Event()

    async def handler(self, websocket: websockets.WebSocketServerProtocol) -> None:
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    message = message.decode("utf-8")
                await websocket.send(f"Echo: {message}")
        finally:
            await websocket.close()

    async def run(self) -> None:
        self.server = await websockets.serve(self.handler, self.host, self.port)
        await self.stop_event.wait()

    def start(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run())

    def stop(self) -> None:
        self.stop_event.set()
        self.loop.stop()


class TestWebSocketClientIntegration:
    @pytest.fixture(scope="module")
    def echo_server(self) -> Generator[EchoServer, None, None]:
        server = EchoServer("localhost", 8765)
        thread = threading.Thread(target=server.start)
        thread.start()
        yield server
        server.stop()
        thread.join()

    @pytest.fixture
    def websocket_client(self) -> WebSocketClient:
        class TestWebSocketClient(WebSocketClient):
            def __init__(self, url: str):
                super().__init__(url)
                self.received_messages = []

            def on_message(self, message: str) -> None:
                self.received_messages.append(message)

        return TestWebSocketClient("ws://localhost:8765")

    def test_websocket_client_integration(self, echo_server: EchoServer, websocket_client: Any) -> None:
        websocket_client.connect()

        # Wait for the connection to be established
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))

        # Send a message
        websocket_client.send_message("Hello, WebSocket!")

        # Wait for the response
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))

        # Check if the message was echoed back
        assert websocket_client.received_messages == ["Echo: Hello, WebSocket!"]

        websocket_client.close()
