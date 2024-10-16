import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from websockets.exceptions import ConnectionClosed
from pysrc.util.websocket_handler import WebSocketClient


class TestWebSocketClient:
    @pytest.fixture
    def websocket_client(self):
        class MockWebSocketClient(WebSocketClient):
            def on_message(self, message: str) -> None:
                pass

        return MockWebSocketClient(url="ws://example.com")

    @patch("websockets.connect", new_callable=AsyncMock)
    async def test_send_message(self, mock_connect, websocket_client):
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws
        websocket_client.websocket = mock_ws

        await websocket_client._send_message("hello")
        mock_ws.send.assert_called_once_with("hello")

    def test_close(self, websocket_client):
        websocket_client._loop = MagicMock()
        websocket_client._stop_event = MagicMock()
        websocket_client._thread = MagicMock()
        websocket_client._executor = MagicMock()

        websocket_client.close()

        websocket_client._stop_event.set.assert_called_once()
        websocket_client._loop.call_soon_threadsafe.assert_called_once()
        websocket_client._thread.join.assert_called_once()
        websocket_client._executor.shutdown.assert_called_once_with(wait=True)
