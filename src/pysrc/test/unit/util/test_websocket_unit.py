import pytest
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from pysrc.util.base_websocket_client import BaseWebSocketClient


class TestWebSocketClient:
    @pytest.fixture
    def websocket_client(self) -> BaseWebSocketClient:
        class MockWebSocketClient(BaseWebSocketClient):
            def on_message(self, message: str | bytes) -> None:
                pass

        return MockWebSocketClient(url="ws://example.com")

    @patch("websockets.connect", new_callable=AsyncMock)
    async def test_send_message(self, mock_connect: Any, websocket_client: BaseWebSocketClient) -> None:
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws
        websocket_client.websocket = mock_ws

        await websocket_client._send_message("hello")
        mock_ws.send.assert_called_once_with("hello")

    def test_close(self, websocket_client: BaseWebSocketClient) -> None:
        websocket_client._loop = MagicMock()
        websocket_client._stop_event = MagicMock()
        websocket_client._thread = MagicMock()

        websocket_client.close()

        websocket_client._stop_event.set.assert_called_once()
        websocket_client._loop.call_soon_threadsafe.assert_called_once()
        websocket_client._thread.join.assert_called_once()
