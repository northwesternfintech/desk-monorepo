import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

import websockets
from websockets.asyncio.client import ClientConnection

_logger = logging.getLogger(__name__)


class WebSocketClient(ABC):
    def __init__(
        self, base_url: str, retry_delay: int = 5, max_retries: Optional[int] = None
    ) -> None:
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.ws: Optional[ClientConnection] = None
        self._listener_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        loop = asyncio.get_event_loop()
        self._listener_task = loop.create_task(self._connect_and_listen())

    async def _connect_and_listen(self) -> None:
        retries = 0
        while self.max_retries is None or retries < self.max_retries:
            try:
                _logger.info(
                    f"Connecting to WebSocket at {self.base_url} (Attempt {retries + 1})..."
                )
                self.ws = await asyncio.wait_for(
                    websockets.connect(self.base_url), timeout=10
                )
                _logger.info("Connected to WebSocket.")

                await self.on_connect()

                await self._listen_for_messages()
                return
            except asyncio.TimeoutError as e:
                _logger.warning("Connection attempt timed out.")
                raise RuntimeError("WebSocket connection timed out.") from e

            except websockets.ConnectionClosed as e:
                _logger.warning(f"WebSocket connection closed: {e}")
                raise RuntimeError("WebSocket connection was unexpectedly closed.") from e

            except Exception as e:
                _logger.warning(f"Unexpected error: {e}")
                raise RuntimeError("An unexpected error occurred while handling the WebSocket.") from e
            finally:
                await self.on_disconnect()

            retries += 1
            if self.max_retries is not None and retries >= self.max_retries:
                _logger.warning("Max retries reached. Shutting websocket down.")
                break
            _logger.debug(f"Retrying in {self.retry_delay} seconds...")
            await asyncio.sleep(self.retry_delay)

    async def _listen_for_messages(self) -> None:
        try:
            while True:
                _logger.info("Listening for messages from WebSocket...")
                if self.ws is None:
                    raise RuntimeError("WebSocket connection is not established.")
                async for message in self.ws:
                    try:
                        data = json.loads(message)
                        await self.on_message(data)
                    except json.JSONDecodeError:
                        _logger.warning("Failed to parse message")
                    await asyncio.sleep(0.1)
        except websockets.ConnectionClosed as e:
            _logger.warning(f"WebSocket connection closed during listening: {e}")
        except Exception as e:
            _logger.warning(f"Unexpected error while listening: {e}")

    @abstractmethod
    async def on_connect(self) -> None:
        pass

    @abstractmethod
    async def on_disconnect(self) -> None:
        pass

    @abstractmethod
    async def on_message(self, message: dict) -> None:
        pass
