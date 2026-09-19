"""WebSocket route for live simulation streaming."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.session import session_manager
from app.api.websocket import ws_manager

ws_router = APIRouter(prefix="/simulations", tags=["WebSocket"])
logger = logging.getLogger(__name__)


@ws_router.websocket("/{simulation_id}/ws")
async def websocket_simulation_endpoint(websocket: WebSocket, simulation_id: str) -> None:
    """Live WebSocket connection for simulation streaming and interactive control."""
    try:
        session = session_manager.get_session(simulation_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Rejecting WebSocket connection for non-existent session %s: %s", simulation_id, exc)
        await websocket.close(code=4004, reason=f"Simulation {simulation_id} not found")
        return

    await ws_manager.connect(simulation_id, websocket)

    try:
        # Send initial connection framing and state envelope
        initial_snapshot = session.get_state_snapshot()
        await ws_manager.send_json(
            websocket,
            {
                "type": "state",
                "timestamp": initial_snapshot["simulation_time_seconds"],
                "data": initial_snapshot,
            },
        )

        while True:
            # Receive client messages / commands
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "step":
                step_sec = float(data.get("step_seconds", 1.0))
                snapshot = await session.step(step_seconds=step_sec)
                msg = {
                    "type": "state",
                    "timestamp": snapshot["simulation_time_seconds"],
                    "data": snapshot,
                }
                await ws_manager.broadcast(simulation_id, msg)

            elif action == "ping":
                await ws_manager.send_json(
                    websocket,
                    {"type": "pong", "timestamp": session.sim.state.simulation_time_seconds},
                )

    except WebSocketDisconnect:
        ws_manager.disconnect(simulation_id, websocket)
    except Exception as exc:  # noqa: BLE001
        logger.error("WebSocket error on simulation %s: %s", simulation_id, exc)
        ws_manager.disconnect(simulation_id, websocket)
