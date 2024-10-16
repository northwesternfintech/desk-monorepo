import asyncio
import websockets
import pytest
import threading
from pysrc.util.websocket_handler import WebSocketClient

class TestWebSocketClient(WebSocketClient):
    def __init__(self, url: str, reconnect_interval: int = 5):
        super().__init__(url, reconnect_interval)
        self.received_messages = []

    def on_message(self, message: str) -> None:
        self.received_messages.append(message)

@pytest.fixture
async def websocket_server():
    server = await websockets.serve(echo_handler, 'localhost', 8765)
    yield server
    server.close()
    await server.wait_closed()

async def echo_handler(websocket, path):
    async for message in websocket:
        await websocket.send(message)

@pytest.mark.asyncio
async def test_websocket_client_integration(websocket_server, event_loop):
    client = TestWebSocketClient("ws://localhost:8765")
    
    # Run the client in a background thread
    def run_client():
        client.connect()

    client_thread = threading.Thread(target=run_client)
    client_thread.start()

    # Give it a moment to connect
    await asyncio.sleep(1)

    # Send a message from the client and wait for the echo
    client.send_message("Hello")

    await asyncio.sleep(1)  # Allow time for the message to be received

    assert "Hello" in client.received_messages

    # Close the client and ensure proper cleanup
    client.close()
    client_thread.join()  # Wait for the client thread to finish