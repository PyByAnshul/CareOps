import logging
from collections import defaultdict
from typing import Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.addons.users.models import User
from app.core.realtime.connection import Connection
from app.core.security.jwt import decode_token

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and workspace broadcasting."""
    
    def __init__(self):
        # workspace_id -> list of connections
        self.workspace_connections: Dict[int, List[Connection]] = defaultdict(list)
    
    async def authenticate(self, websocket: WebSocket, token: str, db: Session) -> Optional[User]:
        """Authenticate user from token."""
        payload = decode_token(token)
        
        if not payload:
            logger.warning("Invalid token in WebSocket connection")
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("No user_id in token payload")
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            logger.warning(f"User {user_id} not found or inactive")
            return None
        
        return user
    
    async def connect(self, websocket: WebSocket, user: User) -> Connection:
        """Accept and register a new connection."""
        await websocket.accept()
        
        connection = Connection(websocket, user, user.workspace_id)
        self.workspace_connections[user.workspace_id].append(connection)
        
        logger.info(f"User {user.id} connected to workspace {user.workspace_id}")
        
        # Send welcome message
        await connection.send_json({
            "type": "connected",
            "workspace_id": user.workspace_id,
            "user_id": user.id,
        })
        
        return connection
    
    def disconnect(self, connection: Connection) -> None:
        """Remove connection from manager."""
        workspace_id = connection.workspace_id
        if workspace_id in self.workspace_connections:
            if connection in self.workspace_connections[workspace_id]:
                self.workspace_connections[workspace_id].remove(connection)
                logger.info(f"User {connection.user_id} disconnected from workspace {workspace_id}")
            
            # Clean up empty workspace lists
            if not self.workspace_connections[workspace_id]:
                del self.workspace_connections[workspace_id]
    
    async def broadcast_to_workspace(self, workspace_id: int, message: dict) -> None:
        """Broadcast message to all connections in a workspace."""
        connections = self.workspace_connections.get(workspace_id, [])
        
        if not connections:
            logger.debug(f"No active connections for workspace {workspace_id}")
            return
        
        logger.info(f"Broadcasting to {len(connections)} connections in workspace {workspace_id}")
        
        # Send to all connections
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to connection: {str(e)}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_user(self, workspace_id: int, user_id: int, message: dict) -> None:
        """Send message to specific user in workspace."""
        connections = self.workspace_connections.get(workspace_id, [])
        
        for connection in connections:
            if connection.user_id == user_id:
                await connection.send_json(message)


# Global connection manager instance
connection_manager = ConnectionManager()
