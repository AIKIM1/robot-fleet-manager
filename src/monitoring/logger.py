from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LogLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass
class LogEntry:
    timestamp: float
    level: LogLevel
    event_type: str
    robot_id: str | None
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "event_type": self.event_type,
            "robot_id": self.robot_id,
            "message": self.message,
            "data": self.data,
        }


class EventLogger:
    def __init__(self, max_entries: int = 2000):
        self._entries: list[LogEntry] = []
        self._max_entries = max_entries
        self._logger = logging.getLogger("fleet_events")

    def log(
        self,
        level: LogLevel,
        event_type: str,
        message: str,
        robot_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            event_type=event_type,
            robot_id=robot_id,
            message=message,
            data=data or {},
        )
        self._entries.append(entry)

        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries // 2 :]

        self._logger.log(
            getattr(logging, level.value, logging.INFO),
            f"[{event_type}] {robot_id or 'system'}: {message}",
        )

    def info(self, event_type: str, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.INFO, event_type, message, **kwargs)

    def warn(self, event_type: str, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.WARN, event_type, message, **kwargs)

    def error(self, event_type: str, message: str, **kwargs: Any) -> None:
        self.log(LogLevel.ERROR, event_type, message, **kwargs)

    def get_entries(
        self,
        limit: int = 100,
        level: str | None = None,
        robot_id: str | None = None,
    ) -> list[dict[str, Any]]:
        entries = self._entries
        if level:
            entries = [e for e in entries if e.level.value == level]
        if robot_id:
            entries = [e for e in entries if e.robot_id == robot_id]
        return [e.to_dict() for e in entries[-limit:]]

    def clear(self) -> None:
        self._entries.clear()


event_logger = EventLogger()
