from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.fleet.manager import FleetManager
from src.fleet.robot import CommProtocol, RobotCommand

router = APIRouter(prefix="/api/robots", tags=["robots"])

fleet_manager: FleetManager | None = None


def set_fleet_manager(manager: FleetManager) -> None:
    global fleet_manager
    fleet_manager = manager


def _get_manager() -> FleetManager:
    if fleet_manager is None:
        raise HTTPException(status_code=500, detail="Fleet manager not initialized")
    return fleet_manager


class RobotCreate(BaseModel):
    name: str
    model_path: str = "models/robot_arm.xml"
    protocol: str = "REST"


class CommandRequest(BaseModel):
    command_type: str
    params: dict[str, Any] = {}


@router.get("")
def list_robots() -> list[dict[str, Any]]:
    return _get_manager().list_robots()


@router.get("/status")
def fleet_status() -> dict[str, Any]:
    return _get_manager().get_fleet_status()


@router.post("")
def register_robot(body: RobotCreate) -> dict[str, Any]:
    try:
        protocol = CommProtocol(body.protocol)
    except ValueError:
        protocol = CommProtocol.REST
    try:
        robot = _get_manager().register_robot(
            name=body.name, model_path=body.model_path, protocol=protocol
        )
        return robot.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/broadcast")
def broadcast_command(body: CommandRequest) -> dict[str, str]:
    cmd = RobotCommand(command_type=body.command_type, params=body.params)
    _get_manager().broadcast_command(cmd)
    return {"status": "broadcast", "command": body.command_type}


@router.get("/logs/all")
def get_logs(limit: int = 100) -> list[dict[str, Any]]:
    return _get_manager().get_logs(limit=limit)


@router.get("/{robot_id}")
def get_robot(robot_id: str) -> dict[str, Any]:
    try:
        return _get_manager().get_robot(robot_id).to_dict()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Robot {robot_id} not found")


@router.delete("/{robot_id}")
def remove_robot(robot_id: str) -> dict[str, str]:
    try:
        _get_manager().remove_robot(robot_id)
        return {"status": "removed", "robot_id": robot_id}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Robot {robot_id} not found")


@router.post("/{robot_id}/command")
def send_command(robot_id: str, body: CommandRequest) -> dict[str, str]:
    try:
        cmd = RobotCommand(command_type=body.command_type, params=body.params)
        _get_manager().send_command(robot_id, cmd)
        return {"status": "sent", "robot_id": robot_id, "command": body.command_type}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Robot {robot_id} not found")
