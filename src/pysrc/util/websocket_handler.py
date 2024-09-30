import logging
import websockets
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsocketClient:
    def __init__(self, url):
        self.url = url

    async def listen(self):
      async with websockets.connect(self.url) as websocket:
        try:
          logger.info("Connected to websocket at {self.url}")
          while True:
              message = await websocket.recv()
              await self.on_message(message)
        except websockets.exceptions.ConnectionClosed as e:
          logger.error(f"Connection closed: {e}")
          await self.on_disconnect()

        except Exception as e:
          logger.error(f"Error: {e}")
          await self.on_disconnect()
    
    async def on_message(self, message):
      logger.info(f"Received message: {message}")
    
    async def on_disconnect(self):
      logger.info("Disconnected from websocket")
