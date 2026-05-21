from __future__ import annotations

import json
import logging
import socketserver
import threading
from typing import Any

from src.fleet.manager import FleetManager
from src.fleet.robot import RobotCommand

logger = logging.getLogger(__name__)


class RobotTCPHandler(socketserver.StreamRequestHandler):
    fleet_manager: FleetManager | None = None

    def handle(self) -> None:
        logger.info(f"TCP connection from {self.client_address}")
        try:
            while True:
                raw = self.rfile.readline().strip()
                if not raw:
                    break
                try:
                    request = json.loads(raw.decode("utf-8"))
                    response = self._process_request(request)
                    self.wfile.write(json.dumps(response).encode("utf-8") + b"\n")
                    self.wfile.flush()
                except json.JSONDecodeError:
                    error = {"error": "Invalid JSON"}
                    self.wfile.write(json.dumps(error).encode("utf-8") + b"\n")
                    self.wfile.flush()
        except (ConnectionResetError, BrokenPipeError):
            logger.info(f"TCP client disconnected: {self.client_address}")

    def _process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        action = request.get("action")
        manager = self.__class__.fleet_manager

        if manager is None:
            return {"error": "Fleet manager not initialized"}

        if action == "list_robots":
            return {"robots": manager.list_robots()}

        elif action == "get_robot":
            robot_id = request.get("robot_id")
            try:
                return {"robot": manager.get_robot(robot_id).to_dict()}
            except KeyError:
                return {"error": f"Robot {robot_id} not found"}

        elif action == "send_command":
            robot_id = request.get("robot_id")
            cmd_type = request.get("command_type")
            params = request.get("params", {})
            try:
                cmd = RobotCommand(command_type=cmd_type, params=params)
                manager.send_command(robot_id, cmd)
                return {"status": "sent"}
            except KeyError:
                return {"error": f"Robot {robot_id} not found"}

        elif action == "fleet_status":
            return {"status": manager.get_fleet_status()}

        return {"error": f"Unknown action: {action}"}


class TCPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 9000):
        self.host = host
        self.port = port
        self._server: socketserver.ThreadingTCPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self, fleet_manager: FleetManager) -> None:
        RobotTCPHandler.fleet_manager = fleet_manager
        self._server = socketserver.ThreadingTCPServer(
            (self.host, self.port), RobotTCPHandler
        )
        self._server.allow_reuse_address = True
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        logger.info(f"TCP server started on {self.host}:{self.port}")

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server = None
        logger.info("TCP server stopped")
