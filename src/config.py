from dataclasses import dataclass, field


@dataclass
class SimulationConfig:
    timestep: float = 0.002
    max_robots: int = 10
    default_model: str = "models/robot_arm.xml"
    render_width: int = 640
    render_height: int = 480
    use_gpu: bool = False


@dataclass
class BatteryConfig:
    """Geek+ S-Series 기준: DC51.1V, 30Ah 리튬이온"""
    capacity_ah: float = 30.0
    voltage: float = 51.1
    drain_rate_idle: float = 0.5
    drain_rate_moving: float = 2.0
    drain_rate_loaded: float = 2.8
    charge_rate: float = 10.0
    low_threshold: float = 20.0
    critical_threshold: float = 10.0
    full_threshold: float = 95.0


@dataclass
class ChargingStationConfig:
    positions: list = field(default_factory=lambda: [
        [5.5, 1.5, 0.0],
        [-5.5, 1.5, 0.0],
    ])


@dataclass
class InductionStationConfig:
    position: list = field(default_factory=lambda: [0.0, 3.5, 0.0])
    scan_time: float = 0.3
    error_rate: float = 0.001


@dataclass
class ParcelConfig:
    weight_categories: dict = field(default_factory=lambda: {
        "소형": {"min_kg": 0.5, "max_kg": 2.0, "probability": 0.4},
        "중형": {"min_kg": 2.0, "max_kg": 10.0, "probability": 0.4},
        "대형": {"min_kg": 10.0, "max_kg": 30.0, "probability": 0.2},
    })
    interval_min: float = 1.5
    interval_max: float = 3.0


@dataclass
class WarehouseConfig:
    width: float = 14.0
    depth: float = 10.0
    conveyor_y: float = 3.5
    zones: dict = field(default_factory=lambda: {
        "서울": [-5.5, -3.5, 0.0],
        "경기": [-3.5, -3.5, 0.0],
        "인천": [-1.5, -3.5, 0.0],
        "부산": [0.5, -3.5, 0.0],
        "대구": [2.5, -3.5, 0.0],
        "광주": [4.5, -3.5, 0.0],
        "대전": [-2.5, -5.0, 0.0],
        "기타": [1.5, -5.0, 0.0],
    })
    zone_weights: dict = field(default_factory=lambda: {
        "서울": 0.25, "경기": 0.20, "인천": 0.10, "부산": 0.12,
        "대구": 0.10, "광주": 0.08, "대전": 0.08, "기타": 0.07,
    })
    robot_speed: float = 2.0
    robot_speed_loaded: float = 1.5
    robot_speed_congested: float = 0.5
    collision_radius: float = 0.6
    robot_home_positions: list = field(default_factory=lambda: [
        [-2.5, 1.0, 0.0], [-0.5, 1.0, 0.0], [1.5, 1.0, 0.0],
        [-1.5, 2.0, 0.0], [0.5, 2.0, 0.0], [2.5, 2.0, 0.0],
    ])
    battery: BatteryConfig = field(default_factory=BatteryConfig)
    charging_stations: ChargingStationConfig = field(default_factory=ChargingStationConfig)
    induction: InductionStationConfig = field(default_factory=InductionStationConfig)
    parcels: ParcelConfig = field(default_factory=ParcelConfig)


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    rest_port: int = 8000
    grpc_port: int = 50051
    ws_update_rate: float = 30.0


@dataclass
class AppConfig:
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    warehouse: WarehouseConfig = field(default_factory=WarehouseConfig)
    server: ServerConfig = field(default_factory=ServerConfig)


config = AppConfig()
