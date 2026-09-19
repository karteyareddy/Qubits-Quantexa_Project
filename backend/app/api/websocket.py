"""WebSocket Connection Manager for live simulation state updates."""

import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """Manages active WebSocket connections per simulation session."""

    def __init__(self) -> None:
        # Maps simulation_id -> set of active WebSockets
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, simulation_id: str, websocket: WebSocket) -> None:
        """Accept connection and add to simulation subscription set."""
        await websocket.accept()
        if simulation_id not in self._connections:
            self._connections[simulation_id] = set()
        self._connections[simulation_id].add(websocket)
        logger.info("WebSocket connected to simulation %s", simulation_id)

    def disconnect(self, simulation_id: str, websocket: WebSocket) -> None:
        """Remove connection from subscription set."""
        if simulation_id in self._connections:
            self._connections[simulation_id].discard(websocket)
            if not self._connections[simulation_id]:
                del self._connections[simulation_id]
        logger.info("WebSocket disconnected from simulation %s", simulation_id)

    async def send_json(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Send JSON message to a single websocket, handling disconnects."""
        try:
            await websocket.send_json(message)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Error sending WebSocket message: %s", exc)

    async def broadcast(self, simulation_id: str, message: dict[str, Any]) -> None:
        """Broadcast JSON message envelope to all active subscribers for a simulation."""
        if simulation_id not in self._connections:
            return

        dead_sockets: set[WebSocket] = set()
        for websocket in list(self._connections[simulation_id]):
            try:
                await websocket.send_json(message)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Broadcasting error on socket for %s: %s", simulation_id, exc)
                dead_sockets.add(websocket)

        for ws in dead_sockets:
            self._connections[simulation_id].discard(ws)


# Global connection manager instance
ws_manager = WebSocketConnectionManager()
