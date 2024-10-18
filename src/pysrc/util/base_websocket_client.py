import asyncio
import websockets
import logging
from abc import ABC, abstractmethod
from typing import Optional
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseWebSocketClient(ABC):
    def __init__(self, url: str, reconnect_interval: int = 5):
        self.url: str = url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.reconnect_interval: int = reconnect_interval
        self._stop_event: threading.Event = threading.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self.received_messages: list[str] = []
        self._connected: bool = False

    def connect(self) -> None:
        self._thread = threading.Thread(target=self._run_event_loop)
        self._thread.start()

    def _run_event_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect_and_listen())

    async def _connect_and_listen(self) -> None:
        try:
            self.websocket = await websockets.connect(self.url)
            logger.info(f"Connected to WebSocket at {self.url}")
            self._connected = True
            await self._listen() 
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self._connected = False
            self.on_connection_error(e)  # connection-specific error

    async def _listen(self) -> None:
        try:
            while not self._stop_event.is_set():
                if self.websocket:
                    message = await self.websocket.recv()
                    self.on_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.on_close()
        except Exception as e:
            logger.error(f"Error while listening: {e}")
            self.on_listen_error(e)  # listening-specific error

    @abstractmethod
    def on_message(self, message: str | bytes) -> None:
        if isinstance(message, bytes):
            message = message.decode("utf-8")
        logger.info(f"Received message: {message}")
        self.received_messages.append(message)

    def on_close(self) -> None:
        logger.info("WebSocket closed")

    def on_connection_error(self, error: Exception) -> None:
        """Handle connection-specific errors."""
        logger.error(f"WebSocket connection error: {error}")
        # reconnect logic
        if self._loop:
            self._loop.call_later(self.reconnect_interval, self.connect)


    def on_listen_error(self, error: Exception) -> None:
        """Handle listening-specific errors."""
        logger.error(f"WebSocket listening error: {error}")

    def send_message(self, message: str) -> None:
        if not self._connected or not self._loop:
            raise RuntimeError("WebSocket is not connected. Call connect() first.")
        future = asyncio.run_coroutine_threadsafe(self._send_message(message), self._loop)
        future.result()

    async def _send_message(self, message: str) -> None:
        if self.websocket:
            await self.websocket.send(message)
            logger.info(f"Sent message: {message}")
        else:
            logger.error("WebSocket is not connected")

    def close(self) -> None:
        self._stop_event.set()
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join()
        logger.info("WebSocket connection closed")

