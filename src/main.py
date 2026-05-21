from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.communication.rest_api import router as robot_router
from src.communication.rest_api import set_fleet_manager
from src.communication.tcp_server import TCPServer
from src.communication.websocket import broadcaster, websocket_endpoint
from src.config import config
from src.fleet.manager import FleetManager
from src.fleet.robot import CommProtocol
from src.monitoring.logger import event_logger
from src.simulation.engine import SimulationEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger(__name__)

fleet_manager = FleetManager(max_robots=config.simulation.max_robots)
sim_engine = SimulationEngine(config.simulation, config.warehouse)
tcp_server = TCPServer(port=9000)


def on_sim_step(state: dict[str, Any]) -> None:
    broadcaster.update_state(state)


sim_engine.on_step(on_sim_step)


def setup_demo_robots() -> None:
    model_path = str(
        Path(__file__).parent / "simulation" / "models" / "robot_arm.xml"
    )

    robots_config = [
        ("분류봇-A", "sorter-a"),
        ("분류봇-B", "sorter-b"),
        ("분류봇-C", "sorter-c"),
        ("분류봇-D", "sorter-d"),
        ("분류봇-E", "sorter-e"),
        ("분류봇-F", "sorter-f"),
    ]

    for i, (name, rid) in enumerate(robots_config):
        robot = fleet_manager.register_robot(
            name=name,
            model_path=model_path,
            protocol=CommProtocol.REST,
            robot_id=rid,
        )
        sim_engine.add_robot(robot, home_index=i)

    event_logger.info("system", f"{len(robots_config)}대 분류 로봇 등록 완료 (충전소 2개소)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    set_fleet_manager(fleet_manager)
    setup_demo_robots()

    model_path = str(
        Path(__file__).parent / "simulation" / "models" / "robot_arm.xml"
    )
    try:
        sim_engine.load_scene(model_path)
    except Exception as e:
        logger.warning(f"Could not load MuJoCo scene: {e}. Using mock simulation.")

    sim_engine.start(realtime=True)

    # TCP 서버는 포트 충돌 문제로 비활성화 (REST API + WebSocket으로 충분)
    # tcp_server.start(fleet_manager)

    broadcast_task = asyncio.create_task(broadcaster.start())
    event_logger.info("system", "Server started")
    logger.info(f"REST API: http://localhost:{config.server.rest_port}/docs")
    logger.info(f"WebSocket: ws://localhost:{config.server.rest_port}/ws")

    yield

    sim_engine.stop()
    try:
        tcp_server.stop()
    except Exception:
        pass
    broadcaster.stop()
    broadcast_task.cancel()
    event_logger.info("system", "Server stopped")


app = FastAPI(
    title="Robot Fleet Manager",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(robot_router)
app.websocket("/ws")(websocket_endpoint)


@app.get("/api/simulation/status")
def simulation_status() -> dict[str, Any]:
    return {
        "running": sim_engine.is_running,
        "step_count": sim_engine.step_count,
        "sim_time": sim_engine.step_count * config.simulation.timestep,
    }


@app.post("/api/simulation/start")
def start_simulation() -> dict[str, str]:
    sim_engine.start(realtime=True)
    event_logger.info("simulation", "Simulation started")
    return {"status": "started"}


@app.post("/api/simulation/stop")
def stop_simulation() -> dict[str, str]:
    sim_engine.stop()
    event_logger.info("simulation", "Simulation stopped")
    return {"status": "stopped"}


@app.post("/api/simulation/reset")
def reset_simulation() -> dict[str, str]:
    sim_engine.reset()
    event_logger.clear()
    event_logger.info("simulation", "시뮬레이션 초기화 완료")
    return {"status": "reset"}


@app.post("/api/simulation/reset-stats")
def reset_stats() -> dict[str, str]:
    sim_engine._zone_counts = {z: 0 for z in config.warehouse.zones}
    sim_engine._total_errors = 0
    sim_engine._throughput_history.clear()
    sim_engine._parcel_counter = 0
    for robot in sim_engine._robots.values():
        robot.sensor_data.parcels_sorted = 0
        robot.sensor_data.errors_count = 0
        robot.sensor_data.total_distance = 0.0
        robot.sensor_data.uptime_seconds = 0.0
    event_logger.clear()
    event_logger.info("simulation", "택배 처리 통계 초기화 완료")
    return {"status": "stats_reset"}


@app.get("/api/logs")
def get_logs(limit: int = 100, level: str | None = None) -> list[dict[str, Any]]:
    return event_logger.get_entries(limit=limit, level=level)


frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.server.host, port=config.server.rest_port)
