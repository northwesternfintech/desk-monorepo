import asyncio
import websockets
import logging
from abc import ABC, abstractmethod
from typing import Optional
import threading
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketClient(ABC):
    def __init__(self, url: str, reconnect_interval: int = 5):
        self.url: str = url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.reconnect_interval: int = reconnect_interval
        self._stop_event: threading.Event = threading.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)

    def connect(self) -> None:
        self._thread = threading.Thread(target=self._run_event_loop)
        self._thread.start()

    def _run_event_loop(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect_and_listen())

    async def _connect_and_listen(self) -> None:
        while not self._stop_event.is_set():
            try:
                async with websockets.connect(self.url) as self.websocket:
                    logger.info(f"Connected to WebSocket at {self.url}")
                    await self._listen()
            except Exception as e:
                logger.error(f"Connection error: {e}")
                await self.on_error(e)

            if not self._stop_event.is_set():
                logger.info(f"Reconnecting in {self.reconnect_interval} seconds...")
                await asyncio.sleep(self.reconnect_interval)

    async def _listen(self) -> None:
        try:
            while not self._stop_event.is_set():
                message = await self.websocket.recv()
                self.on_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.on_close()
            # reconnect
            self.connect()
        except Exception as e:
            logger.error(f"Error while listening: {e}")
            self.on_error(e)

    @abstractmethod
    def on_message(self, message: str) -> None:
        logger.info(f"Received message: {message}")

    def on_close(self) -> None:
        logger.info("WebSocket closed")

    def on_error(self, error: Exception) -> None:
        logger.error(f"WebSocket error: {error}")

    def send_message(self, message: str) -> None:
        if self._loop is None:
            raise RuntimeError("WebSocket is not connected. Call connect() first.")
        future = asyncio.run_coroutine_threadsafe(
            self._send_message(message), self._loop
        )
        future.result()  # This will block until the message is sent

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
        self._executor.shutdown(wait=True)
        logger.info("WebSocket connection closed")
