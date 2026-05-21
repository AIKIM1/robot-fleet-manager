from src.fleet.robot import Robot, RobotCommand
from src.simulation.engine import SimulationEngine


def test_mock_step():
    engine = SimulationEngine()
    robot = Robot(name="TestBot", model_path="models/test.xml", robot_id="t1")
    engine.add_robot(robot)
    state = engine.step()
    assert engine.step_count == 1
    assert state["robots"][0]["id"] == "t1"


def test_stop_command():
    engine = SimulationEngine()
    robot = Robot(name="TestBot", model_path="models/test.xml")
    engine.add_robot(robot)
    robot.sensor_data.task_state = "MOVING"
    robot.send_command(RobotCommand(command_type="stop"))
    engine.step()
    assert robot.sensor_data.task_state == "IDLE"
