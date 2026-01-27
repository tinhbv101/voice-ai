"""WebSocket connection manager for handling multiple clients."""

import uuid
from typing import Dict, Set
from fastapi import WebSocket
import asyncio
import logging

from src.websocket_protocol import WebSocketMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        """Initialize connection manager."""
        # Active connections: session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Connection metadata: session_id -> metadata dict
        self.connection_metadata: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket instance

        Returns:
            Session ID for the connection
        """
        await websocket.accept()

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Register connection
        self.active_connections[session_id] = websocket
        self.connection_metadata[session_id] = {
            "connected_at": asyncio.get_event_loop().time(),
            "message_count": 0
        }

        logger.info(f"New WebSocket connection: {session_id}")
        return session_id

    def disconnect(self, session_id: str):
        """
        Disconnect and unregister a WebSocket connection.

        Args:
            session_id: Session ID to disconnect
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            del self.connection_metadata[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(
        self,
        session_id: str,
        message: WebSocketMessage
    ):
        """
        Send message to a specific client.

        Args:
            session_id: Target session ID
            message: Message to send
        """
        if session_id not in self.active_connections:
            logger.warning(f"Session not found: {session_id}")
            return

        websocket = self.active_connections[session_id]

        try:
            json_message = message.to_json()
            logger.debug(f"Sending message to {session_id}: {json_message[:100]}...")
            await websocket.send_text(json_message)
            logger.debug(f"Message sent successfully to {session_id}")

            # Update metadata
            if session_id in self.connection_metadata:
                self.connection_metadata[session_id]["message_count"] += 1

        except Exception as e:
            logger.error(f"Error sending message to {session_id}: {e}")
            self.disconnect(session_id)

    async def send_text(self, session_id: str, text: str):
        """
        Send plain text to a specific client.

        Args:
            session_id: Target session ID
            text: Text to send
        """
        if session_id not in self.active_connections:
            logger.warning(f"Session not found: {session_id}")
            return

        websocket = self.active_connections[session_id]

        try:
            await websocket.send_text(text)

            # Update metadata
            if session_id in self.connection_metadata:
                self.connection_metadata[session_id]["message_count"] += 1

        except Exception as e:
            logger.error(f"Error sending text to {session_id}: {e}")
            self.disconnect(session_id)

    async def broadcast(self, message: WebSocketMessage):
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast
        """
        disconnected_sessions = []

        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message.to_json())

                # Update metadata
                if session_id in self.connection_metadata:
                    self.connection_metadata[session_id]["message_count"] += 1

            except Exception as e:
                logger.error(f"Error broadcasting to {session_id}: {e}")
                disconnected_sessions.append(session_id)

        # Clean up disconnected sessions
        for session_id in disconnected_sessions:
            self.disconnect(session_id)

    def get_active_count(self) -> int:
        """
        Get number of active connections.

        Returns:
            Number of active connections
        """
        return len(self.active_connections)

    def get_session_metadata(self, session_id: str) -> Dict:
        """
        Get metadata for a session.

        Args:
            session_id: Session ID

        Returns:
            Metadata dictionary
        """
        return self.connection_metadata.get(session_id, {})

    def is_connected(self, session_id: str) -> bool:
        """
        Check if session is connected.

        Args:
            session_id: Session ID to check

        Returns:
            True if connected
        """
        return session_id in self.active_connections
