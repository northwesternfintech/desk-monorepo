import asyncio
import websockets
import json
from abc import ABC, abstractmethod
from websockets.asyncio.client import ClientConnection
from typing import Optional


class WebSocketClient(ABC):
    def __init__(
        self, base_url: str, max_retries: int = 5, retry_delay: int = 5
    ) -> None:
        self.base_url = base_url
        self.max_retries = max_retries  # -1 for infinite
        self.retry_delay = retry_delay
        self.ws: Optional[ClientConnection] = None
        self._listener_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        loop = asyncio.get_event_loop()
        self._listener_task = loop.create_task(self._connect_and_listen())

    async def _connect_and_listen(self) -> None:
        retries = 0
        while self.max_retries == -1 or retries < self.max_retries:
            try:
                print(
                    f"Connecting to WebSocket at {self.base_url} (Attempt {retries + 1})..."
                )
                self.ws = await asyncio.wait_for(
                    websockets.connect(self.base_url), timeout=10
                )
                print("Connected to WebSocket.")

                await self.on_connect()

                await self._listen_for_messages()
                return
            except asyncio.TimeoutError:
                print("Connection attempt timed out.")
            except websockets.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
            finally:
                await self.on_disconnect()

            retries += 1
            if self.max_retries != -1 and retries >= self.max_retries:
                print("Max retries reached. Shutting websocket down.")
                break
            print(f"Retrying in {self.retry_delay} seconds...")
            await asyncio.sleep(self.retry_delay)

    async def _listen_for_messages(self) -> None:
        try:
            while True:
                print("Listening for messages from WebSocket...")
                if self.ws is None:
                    raise RuntimeError("WebSocket connection is not established.")
                async for message in self.ws:
                    try:
                        data = json.loads(message)
                        await self.on_message(data)
                    except json.JSONDecodeError:
                        print("Failed to parse message")
                    await asyncio.sleep(0.1)  # small delay for processing, can change
        except websockets.ConnectionClosed as e:
            print(f"WebSocket connection closed during listening: {e}")
        except Exception as e:
            print(f"Unexpected error while listening: {e}")

    @abstractmethod
    async def on_connect(self) -> None:
        pass

    @abstractmethod
    async def on_disconnect(self) -> None:
        pass

    @abstractmethod
    async def on_message(self, message: dict) -> None:
        pass
