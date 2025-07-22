# api/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class SupportChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for the real-time support chat.
    Its primary role now is to provide a stable channel name for the session.
    """
    async def connect(self):
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'channel_name': self.channel_name
        }))

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected: {self.channel_name} (Code: {close_code})")