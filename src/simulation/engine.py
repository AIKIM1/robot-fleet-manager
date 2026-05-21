from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass
from typing import Any

import numpy as np

try:
    import mujoco
except ImportError:
    mujoco = None  # type: ignore[assignment]

from src.config import SimulationConfig, WarehouseConfig
from src.fleet.robot import Robot, RobotCommand, RobotStatus, SensorData
from src.monitoring.logger import event_logger


@dataclass
class ConveyorParcel:
    id: str
    destination: str
    weight: float
    size_category: str
    position: list[float]
    assigned_robot: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class SimulationEngine:
    def __init__(self, config: SimulationConfig | None = None, warehouse: WarehouseConfig | None = None):
        self.config = config or SimulationConfig()
        self.warehouse = warehouse or WarehouseConfig()
        self._robots: dict[str, Robot] = {}
        self._robot_home: dict[str, np.ndarray] = {}
        self._waypoints: dict[str, list[np.ndarray]] = {}
        self._running = False
        self._sim_thread: threading.Thread | None = None
        self._step_count = 0
        self._callbacks: list[Any] = []
        self._lock = threading.Lock()
        self._next_parcel_time = 3.0
        self._parcel_counter = 0
        self._paused = False
        self._zone_counts = {z: 0 for z in self.warehouse.zones}
        self._total_errors = 0
        self._throughput_history: list[tuple[float, int]] = []
        self._conveyor_queue: list[ConveyorParcel] = []
        self._conveyor_slot = 0
        self._charging_stations = [
            {"position": np.array(pos, dtype=float), "occupied_by": None}
            for pos in self.warehouse.charging_stations.positions
        ]

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def step_count(self) -> int:
        return self._step_count

    def load_scene(self, xml_path: str | None = None) -> None:
        if mujoco is None:
            return
        model = mujoco.MjModel.from_xml_path(xml_path or self.config.default_model)
        model.opt.timestep = self.config.timestep
        self._model = model
        self._data = mujoco.MjData(model)

    def add_robot(self, robot: Robot, home_index: int = 0) -> None:
        self._robots[robot.id] = robot
        home = self.warehouse.robot_home_positions[home_index % len(self.warehouse.robot_home_positions)]
        self._robot_home[robot.id] = np.array(home, dtype=float)
        robot.position = np.array(home, dtype=float)
        robot.sensor_data = SensorData(battery_level=100.0, task_state="IDLE")
        robot.status = RobotStatus.IDLE

    def remove_robot(self, robot_id: str) -> None:
        self._robots.pop(robot_id, None)
        self._robot_home.pop(robot_id, None)
        self._waypoints.pop(robot_id, None)

    def on_step(self, callback: Any) -> None:
        self._callbacks.append(callback)

    def start(self, realtime: bool = True) -> None:
        if self._running:
            return
        self._running = True
        for robot in self._robots.values():
            robot.status = RobotStatus.RUNNING
        self._sim_thread = threading.Thread(target=self._run_loop, args=(realtime,), daemon=True)
        self._sim_thread.start()

    def stop(self) -> None:
        self._running = False
        if self._sim_thread:
            self._sim_thread.join(timeout=2.0)
            self._sim_thread = None
        for robot in self._robots.values():
            robot.status = RobotStatus.IDLE

    def reset(self) -> None:
        with self._lock:
            self._step_count = 0
            self._parcel_counter = 0
            self._next_parcel_time = 3.0
            self._paused = False
            self._conveyor_queue.clear()
            self._waypoints.clear()
            self._zone_counts = {z: 0 for z in self.warehouse.zones}
            self._total_errors = 0
            self._throughput_history.clear()
            for robot in self._robots.values():
                robot.position = self._robot_home.get(robot.id, np.zeros(3)).copy()
                robot.sensor_data = SensorData(battery_level=100.0, task_state="IDLE")
                robot.status = RobotStatus.IDLE

    def step(self) -> dict[str, Any]:
        with self._lock:
            self._process_commands()
            self._warehouse_step()
            self._step_count += 1
        state = self._get_state()
        for callback in self._callbacks:
            callback(state)
        return state

    def _run_loop(self, realtime: bool) -> None:
        dt = self.config.timestep
        while self._running:
            started = time.time()
            self.step()
            if realtime:
                time.sleep(max(0.0, dt - (time.time() - started)))

    def _process_commands(self) -> None:
        for robot in self._robots.values():
            cmd = robot.pop_command()
            while cmd:
                self._execute_command(robot, cmd)
                cmd = robot.pop_command()

    def _execute_command(self, robot: Robot, cmd: RobotCommand) -> None:
        if cmd.command_type == "stop":
            robot.sensor_data.task_state = "IDLE"
            robot.sensor_data.carrying_parcel = False
            self._waypoints.pop(robot.id, None)
            self._paused = True
        elif cmd.command_type == "reset":
            robot.position = self._robot_home.get(robot.id, np.zeros(3)).copy()
            robot.sensor_data = SensorData(battery_level=100.0, task_state="IDLE")
        elif cmd.command_type == "resume":
            self._paused = False
        elif cmd.command_type == "charge":
            robot.sensor_data.task_state = "WAITING_CHARGE"
        elif cmd.command_type == "move":
            robot.sensor_data.target_position = list(cmd.params.get("target", [0, 0, 0]))
            robot.sensor_data.task_state = "MOVING"

    def _warehouse_step(self) -> None:
        sim_time = self._step_count * self.config.timestep
        dt = self.config.timestep
        if not self._paused and sim_time >= self._next_parcel_time:
            self._assign_parcel(sim_time)
        if not self._paused:
            self._dispatch_parcels()
        self._apply_collision_avoidance()
        for robot in self._robots.values():
            self._update_battery(robot, dt)
            state = robot.sensor_data.task_state
            if state == "IDLE":
                self._move_toward(robot, self._robot_home.get(robot.id, np.zeros(3)), dt)
            elif state == "PICKING":
                target = np.array(robot.sensor_data.target_position or [0, self.warehouse.conveyor_y, 0])
                if self._move_toward(robot, target, dt):
                    self._conveyor_queue = [p for p in self._conveyor_queue if p.id != robot.sensor_data.parcel_id]
                    robot.sensor_data.carrying_parcel = True
                    zone = self.warehouse.zones.get(robot.sensor_data.parcel_destination, [0, 0, 0])
                    self._waypoints[robot.id] = [np.array(zone, dtype=float)]
                    robot.sensor_data.task_state = "MOVING"
            elif state == "MOVING":
                waypoints = self._waypoints.get(robot.id, [])
                if waypoints and self._move_toward(robot, waypoints[0], dt, robot.sensor_data.carrying_parcel):
                    waypoints.pop(0)
                if not waypoints:
                    robot.sensor_data.task_state = "DROPPING" if robot.sensor_data.carrying_parcel else "IDLE"
            elif state == "DROPPING":
                dest = robot.sensor_data.parcel_destination
                if dest:
                    self._zone_counts[dest] = self._zone_counts.get(dest, 0) + 1
                robot.sensor_data.parcels_sorted += 1
                event_logger.info("delivered", f"{robot.sensor_data.parcel_id} -> {dest}", robot_id=robot.id)
                robot.sensor_data = SensorData(battery_level=robot.sensor_data.battery_level, task_state="RETURNING")
            elif state == "RETURNING":
                if self._move_toward(robot, self._robot_home.get(robot.id, np.zeros(3)), dt):
                    robot.sensor_data.task_state = "IDLE"
            elif state == "WAITING_CHARGE":
                station = next((s for s in self._charging_stations if s["occupied_by"] is None), None)
                if station:
                    station["occupied_by"] = robot.id
                    robot.sensor_data.charging_station_id = self._charging_stations.index(station)
                    robot.sensor_data.target_position = station["position"].tolist()
                    robot.sensor_data.task_state = "CHARGING"
                    robot.status = RobotStatus.CHARGING
            elif state == "CHARGING":
                sid = robot.sensor_data.charging_station_id
                station = self._charging_stations[sid]
                if self._move_toward(robot, station["position"], dt):
                    robot.sensor_data.battery_charging = True
                    if robot.sensor_data.battery_level >= self.warehouse.battery.full_threshold:
                        station["occupied_by"] = None
                        robot.sensor_data.task_state = "IDLE"
                        robot.sensor_data.battery_charging = False
                        robot.status = RobotStatus.RUNNING
            robot.last_update = time.time()

    def _move_toward(self, robot: Robot, target: np.ndarray, dt: float, loaded: bool = False) -> bool:
        diff = target - robot.position
        dist = float(np.linalg.norm(diff))
        if dist < 0.08:
            robot.position = target.copy()
            robot.sensor_data.current_speed = 0.0
            return True
        speed = self.warehouse.robot_speed_loaded if loaded else self.warehouse.robot_speed
        step = min(speed * dt, dist)
        robot.position = robot.position + diff / dist * step
        robot.sensor_data.current_speed = speed
        robot.sensor_data.total_distance += step
        return False

    def _update_battery(self, robot: Robot, dt: float) -> None:
        sd = robot.sensor_data
        rate = self.warehouse.battery.charge_rate if sd.battery_charging else -self.warehouse.battery.drain_rate_moving
        sd.battery_level = max(0.0, min(100.0, sd.battery_level + rate * dt / 60.0))

    def _apply_collision_avoidance(self) -> None:
        robots = list(self._robots.values())
        for r in robots:
            r.sensor_data.obstacle_detected = False
        for i, a in enumerate(robots):
            for b in robots[i + 1:]:
                if np.linalg.norm(a.position - b.position) < self.warehouse.collision_radius * 2:
                    a.sensor_data.obstacle_detected = True
                    b.sensor_data.obstacle_detected = True

    def _assign_parcel(self, sim_time: float) -> None:
        if len(self._conveyor_queue) >= 6:
            self._next_parcel_time = sim_time + 0.5
            return
        dest = random.choices(list(self.warehouse.zone_weights), weights=list(self.warehouse.zone_weights.values()))[0]
        size = random.choices(list(self.warehouse.parcels.weight_categories), weights=[0.4, 0.4, 0.2])[0]
        info = self.warehouse.parcels.weight_categories[size]
        self._parcel_counter += 1
        self._conveyor_queue.append(ConveyorParcel(
            id=f"PKG-{self._parcel_counter:04d}",
            destination=dest,
            weight=round(random.uniform(info["min_kg"], info["max_kg"]), 1),
            size_category=size,
            position=[-3.0 + (self._conveyor_slot % 6) * 1.2, self.warehouse.conveyor_y, 0.0],
        ))
        self._conveyor_slot += 1
        self._next_parcel_time = sim_time + random.uniform(self.warehouse.parcels.interval_min, self.warehouse.parcels.interval_max)

    def _dispatch_parcels(self) -> None:
        idle = [r for r in self._robots.values() if r.sensor_data.task_state == "IDLE"]
        for parcel in [p for p in self._conveyor_queue if p.assigned_robot is None]:
            if not idle:
                return
            robot = idle.pop(0)
            parcel.assigned_robot = robot.id
            robot.sensor_data.parcel_id = parcel.id
            robot.sensor_data.parcel_destination = parcel.destination
            robot.sensor_data.parcel_weight = parcel.weight
            robot.sensor_data.parcel_size_category = parcel.size_category
            robot.sensor_data.target_position = parcel.position
            robot.sensor_data.task_state = "PICKING"

    def _calc_kpis(self) -> dict[str, Any]:
        total = sum(self._zone_counts.values())
        batteries = [r.sensor_data.battery_level for r in self._robots.values()]
        return {
            "throughput_per_hour": total,
            "accuracy_rate": 1.0 if total == 0 else 1.0 - self._total_errors / max(total, 1),
            "fleet_battery_avg": round(sum(batteries) / max(len(batteries), 1), 1),
            "uptime_percent": 100.0,
            "total_errors": self._total_errors,
            "total_distance": round(sum(r.sensor_data.total_distance for r in self._robots.values()), 1),
        }

    def _get_state(self) -> dict[str, Any]:
        return {
            "timestamp": time.time(),
            "step": self._step_count,
            "sim_time": self._step_count * self.config.timestep,
            "paused": self._paused,
            "robots": [r.to_dict() for r in self._robots.values()],
            "zone_counts": dict(self._zone_counts),
            "total_parcels": sum(self._zone_counts.values()),
            "kpis": self._calc_kpis(),
            "charging_stations": [{"position": s["position"].tolist(), "occupied_by": s["occupied_by"]} for s in self._charging_stations],
            "conveyor_parcels": [p.to_dict() for p in self._conveyor_queue],
        }
