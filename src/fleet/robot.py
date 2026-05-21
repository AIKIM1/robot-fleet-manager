from __future__ import annotations

import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np


class RobotStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    CHARGING = "CHARGING"
    ERROR = "ERROR"
    DISCONNECTED = "DISCONNECTED"


class CommProtocol(str, Enum):
    REST = "REST"
    TCP = "TCP"
    ROS = "ROS"


@dataclass
class RobotCommand:
    command_type: str
    params: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class SensorData:
    joint_angles: list[float] = field(default_factory=list)
    joint_velocities: list[float] = field(default_factory=list)
    forces: list[float] = field(default_factory=list)
    torques: list[float] = field(default_factory=list)
    # 택배 분류
    carrying_parcel: bool = False
    parcel_destination: str = ""
    parcel_id: str = ""
    task_state: str = "IDLE"
    parcels_sorted: int = 0
    target_position: list[float] = field(default_factory=list)
    # 배터리
    battery_level: float = 100.0
    battery_charging: bool = False
    charging_station_id: int = -1
    # 속도 / 운동
    current_speed: float = 0.0
    total_distance: float = 0.0
    # 택배 상세
    parcel_weight: float = 0.0
    parcel_size_category: str = ""
    # 통계
    errors_count: int = 0
    uptime_seconds: float = 0.0
    # 안전
    obstacle_detected: bool = False


class Robot:
    def __init__(
        self,
        name: str,
        model_path: str,
        protocol: CommProtocol = CommProtocol.REST,
        robot_id: str | None = None,
    ):
        self.id = robot_id or str(uuid.uuid4())[:8]
        self.name = name
        self.model_path = model_path
        self.protocol = protocol
        self.status = RobotStatus.IDLE
        self.position = np.zeros(3)
        self.orientation = np.array([1.0, 0.0, 0.0, 0.0])
        self.sensor_data = SensorData()
        self.command_queue: deque[RobotCommand] = deque(maxlen=100)
        self.created_at = time.time()
        self.last_update = time.time()
        self.mujoco_body_id: int | None = None

    def send_command(self, command: RobotCommand) -> None:
        self.command_queue.append(command)

    def pop_command(self) -> RobotCommand | None:
        if self.command_queue:
            return self.command_queue.popleft()
        return None

    def update_state(
        self,
        position: np.ndarray | None = None,
        orientation: np.ndarray | None = None,
        sensor_data: SensorData | None = None,
    ) -> None:
        if position is not None:
            self.position = position
        if orientation is not None:
            self.orientation = orientation
        if sensor_data is not None:
            self.sensor_data = sensor_data
        self.last_update = time.time()

    def to_dict(self) -> dict[str, Any]:
        sd = self.sensor_data
        return {
            "id": self.id,
            "name": self.name,
            "model_path": self.model_path,
            "protocol": self.protocol.value,
            "status": self.status.value,
            "position": self.position.tolist(),
            "orientation": self.orientation.tolist(),
            "sensor_data": {
                "joint_angles": sd.joint_angles,
                "joint_velocities": sd.joint_velocities,
                "forces": sd.forces,
                "torques": sd.torques,
                "carrying_parcel": sd.carrying_parcel,
                "parcel_destination": sd.parcel_destination,
                "parcel_id": sd.parcel_id,
                "task_state": sd.task_state,
                "parcels_sorted": sd.parcels_sorted,
                "target_position": sd.target_position,
                "battery_level": sd.battery_level,
                "battery_charging": sd.battery_charging,
                "charging_station_id": sd.charging_station_id,
                "current_speed": sd.current_speed,
                "total_distance": sd.total_distance,
                "parcel_weight": sd.parcel_weight,
                "parcel_size_category": sd.parcel_size_category,
                "errors_count": sd.errors_count,
                "uptime_seconds": sd.uptime_seconds,
                "obstacle_detected": sd.obstacle_detected,
            },
            "last_update": self.last_update,
        }
