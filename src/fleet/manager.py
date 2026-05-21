from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from src.fleet.robot import CommProtocol, Robot, RobotCommand, RobotStatus

logger = logging.getLogger(__name__)


class FleetManager:
    def __init__(self, max_robots: int = 5):
        self.max_robots = max_robots
        self._robots: dict[str, Robot] = {}
        self._event_callbacks: list[Callable[[str, str, dict[str, Any]], None]] = []
        self._log_entries: list[dict[str, Any]] = []

    @property
    def robots(self) -> dict[str, Robot]:
        return self._robots

    def register_robot(
        self,
        name: str,
        model_path: str,
        protocol: CommProtocol = CommProtocol.REST,
        robot_id: str | None = None,
    ) -> Robot:
        if len(self._robots) >= self.max_robots:
            raise ValueError(f"Maximum robot count ({self.max_robots}) reached")

        robot = Robot(name=name, model_path=model_path, protocol=protocol, robot_id=robot_id)
        self._robots[robot.id] = robot
        self._emit_event("robot_registered", robot.id, {"name": name})
        logger.info(f"Robot registered: {robot.id} ({name})")
        return robot

    def remove_robot(self, robot_id: str) -> None:
        if robot_id not in self._robots:
            raise KeyError(f"Robot {robot_id} not found")
        name = self._robots[robot_id].name
        del self._robots[robot_id]
        self._emit_event("robot_removed", robot_id, {"name": name})
        logger.info(f"Robot removed: {robot_id}")

    def get_robot(self, robot_id: str) -> Robot:
        if robot_id not in self._robots:
            raise KeyError(f"Robot {robot_id} not found")
        return self._robots[robot_id]

    def list_robots(self) -> list[dict[str, Any]]:
        return [robot.to_dict() for robot in self._robots.values()]

    def send_command(self, robot_id: str, command: RobotCommand) -> None:
        robot = self.get_robot(robot_id)
        robot.send_command(command)
        self._emit_event(
            "command_sent",
            robot_id,
            {"command_type": command.command_type, "params": command.params},
        )

    def broadcast_command(self, command: RobotCommand) -> None:
        for robot_id in self._robots:
            self.send_command(robot_id, command)

    def get_fleet_status(self) -> dict[str, Any]:
        statuses = [r.status for r in self._robots.values()]
        return {
            "total": len(self._robots),
            "running": statuses.count(RobotStatus.RUNNING),
            "idle": statuses.count(RobotStatus.IDLE),
            "error": statuses.count(RobotStatus.ERROR),
            "disconnected": statuses.count(RobotStatus.DISCONNECTED),
        }

    def on_event(self, callback: Callable[[str, str, dict[str, Any]], None]) -> None:
        self._event_callbacks.append(callback)

    def _emit_event(self, event_type: str, robot_id: str, data: dict[str, Any]) -> None:
        import time

        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "robot_id": robot_id,
            "data": data,
        }
        self._log_entries.append(entry)
        if len(self._log_entries) > 1000:
            self._log_entries = self._log_entries[-500:]

        for callback in self._event_callbacks:
            try:
                callback(event_type, robot_id, data)
            except Exception as e:
                logger.error(f"Event callback error: {e}")

    def get_logs(self, limit: int = 100, level: str | None = None) -> list[dict[str, Any]]:
        logs = self._log_entries
        if level:
            logs = [l for l in logs if l.get("level") == level]
        return logs[-limit:]
