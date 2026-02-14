import logging
from typing import Optional

from fastapi import WebSocket

from app.addons.users.models import User

logger = logging.getLogger(__name__)


class Connection:
    """WebSocket connection with user and workspace context."""
    
    def __init__(self, websocket: WebSocket, user: User, workspace_id: int):
        self.websocket = websocket
        self.user = user
        self.workspace_id = workspace_id
        self.user_id = user.id
    
    async def send_json(self, data: dict) -> None:
        """Send JSON data to client."""
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send message to user {self.user_id}: {str(e)}")
    
    async def close(self) -> None:
        """Close the connection."""
        try:
            await self.websocket.close()
        except Exception as e:
            logger.error(f"Error closing connection for user {self.user_id}: {str(e)}")
