import pytest

from src.fleet.manager import FleetManager
from src.fleet.robot import Robot, RobotCommand, RobotStatus


def test_create_robot():
    robot = Robot(name="TestBot", model_path="models/test.xml")
    assert robot.name == "TestBot"
    assert robot.status == RobotStatus.IDLE


def test_command_queue():
    robot = Robot(name="TestBot", model_path="models/test.xml")
    robot.send_command(RobotCommand(command_type="stop"))
    assert robot.pop_command().command_type == "stop"
    assert robot.pop_command() is None


def test_register_limit():
    fm = FleetManager(max_robots=1)
    fm.register_robot("Bot1", "models/test.xml")
    with pytest.raises(ValueError):
        fm.register_robot("Bot2", "models/test.xml")
