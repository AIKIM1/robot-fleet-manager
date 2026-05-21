from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self._connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self._connections)}")

    async def broadcast(self, data: dict[str, Any]) -> None:
        message = json.dumps(data)
        disconnected = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws)

    @property
    def connection_count(self) -> int:
        return len(self._connections)


ws_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                logger.debug(f"WebSocket received: {msg}")
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


class SimulationBroadcaster:
    def __init__(self, manager: ConnectionManager, update_rate: float = 30.0):
        self._manager = manager
        self._update_rate = update_rate
        self._latest_state: dict[str, Any] | None = None
        self._running = False

    def update_state(self, state: dict[str, Any]) -> None:
        self._latest_state = state

    async def start(self) -> None:
        self._running = True
        interval = 1.0 / self._update_rate
        while self._running:
            if self._latest_state and self._manager.connection_count > 0:
                await self._manager.broadcast(self._latest_state)
            await asyncio.sleep(interval)

    def stop(self) -> None:
        self._running = False


broadcaster = SimulationBroadcaster(ws_manager)
