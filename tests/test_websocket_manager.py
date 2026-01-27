"""Tests for WebSocket connection manager."""

import pytest
from unittest.mock import Mock, AsyncMock
from src.websocket_manager import ConnectionManager
from src.websocket_protocol import WebSocketMessage, MessageType


class TestConnectionManager:
    """Test connection manager."""

    @pytest.fixture
    def manager(self):
        """Create connection manager instance."""
        return ConnectionManager()

    @pytest.mark.asyncio
    async def test_connect_creates_session(self, manager):
        """Test that connect creates a new session."""
        mock_ws = AsyncMock()

        session_id = await manager.connect(mock_ws)

        assert session_id is not None
        assert len(session_id) > 0
        assert manager.is_connected(session_id)
        assert manager.get_active_count() == 1
        mock_ws.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_removes_session(self, manager):
        """Test that disconnect removes session."""
        mock_ws = AsyncMock()

        session_id = await manager.connect(mock_ws)
        manager.disconnect(session_id)

        assert not manager.is_connected(session_id)
        assert manager.get_active_count() == 0

    @pytest.mark.asyncio
    async def test_send_message_sends_to_client(self, manager):
        """Test sending message to client."""
        mock_ws = AsyncMock()
        session_id = await manager.connect(mock_ws)

        message = WebSocketMessage(
            type=MessageType.TEXT_RESPONSE,
            data={"text": "Hello"},
            session_id=session_id
        )

        await manager.send_message(session_id, message)

        mock_ws.send_text.assert_called_once()
        sent_data = mock_ws.send_text.call_args[0][0]
        assert "Hello" in sent_data

    @pytest.mark.asyncio
    async def test_send_message_invalid_session(self, manager):
        """Test sending message to invalid session."""
        message = WebSocketMessage(
            type=MessageType.TEXT_RESPONSE,
            data={"text": "Hello"},
            session_id="invalid"
        )

        # Should not raise exception
        await manager.send_message("invalid", message)

    @pytest.mark.asyncio
    async def test_send_text_sends_plain_text(self, manager):
        """Test sending plain text to client."""
        mock_ws = AsyncMock()
        session_id = await manager.connect(mock_ws)

        await manager.send_text(session_id, "Hello world")

        mock_ws.send_text.assert_called_once_with("Hello world")

    @pytest.mark.asyncio
    async def test_broadcast_sends_to_all(self, manager):
        """Test broadcasting message to all clients."""
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()

        session1 = await manager.connect(mock_ws1)
        session2 = await manager.connect(mock_ws2)

        message = WebSocketMessage(
            type=MessageType.STATUS,
            data={"status": "test"},
            session_id=None
        )

        await manager.broadcast(message)

        assert mock_ws1.send_text.called
        assert mock_ws2.send_text.called

    @pytest.mark.asyncio
    async def test_get_session_metadata(self, manager):
        """Test getting session metadata."""
        mock_ws = AsyncMock()
        session_id = await manager.connect(mock_ws)

        metadata = manager.get_session_metadata(session_id)

        assert "connected_at" in metadata
        assert "message_count" in metadata
        assert metadata["message_count"] == 0

    @pytest.mark.asyncio
    async def test_send_message_updates_count(self, manager):
        """Test that sending message updates message count."""
        mock_ws = AsyncMock()
        session_id = await manager.connect(mock_ws)

        message = WebSocketMessage(
            type=MessageType.TEXT_RESPONSE,
            data={"text": "Hello"},
            session_id=session_id
        )

        await manager.send_message(session_id, message)

        metadata = manager.get_session_metadata(session_id)
        assert metadata["message_count"] == 1

    @pytest.mark.asyncio
    async def test_multiple_connections(self, manager):
        """Test handling multiple connections."""
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        mock_ws3 = AsyncMock()

        session1 = await manager.connect(mock_ws1)
        session2 = await manager.connect(mock_ws2)
        session3 = await manager.connect(mock_ws3)

        assert manager.get_active_count() == 3
        assert session1 != session2 != session3

        manager.disconnect(session2)
        assert manager.get_active_count() == 2
        assert manager.is_connected(session1)
        assert not manager.is_connected(session2)
        assert manager.is_connected(session3)
