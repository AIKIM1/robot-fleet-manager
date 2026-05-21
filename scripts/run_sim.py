"""Run a headless simulation for testing/CI."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fleet.robot import Robot
from src.simulation.engine import SimulationEngine


def main():
    parser = argparse.ArgumentParser(description="Run headless robot simulation")
    parser.add_argument("--robots", type=int, default=3, help="Number of robots")
    parser.add_argument("--steps", type=int, default=1000, help="Simulation steps")
    args = parser.parse_args()

    engine = SimulationEngine()

    for i in range(args.robots):
        robot = Robot(
            name=f"Robot-{i+1}",
            model_path="models/robot_arm.xml",
            robot_id=f"r{i+1}",
        )
        engine.add_robot(robot)

    print(f"Running simulation: {args.robots} robots, {args.steps} steps")
    t0 = time.time()

    for step in range(args.steps):
        state = engine.step()
        if step % 100 == 0:
            print(
                f"  Step {step}: sim_time={state['sim_time']:.3f}s, "
                f"robots={len(state['robots'])}"
            )

    elapsed = time.time() - t0
    print(f"Completed {args.steps} steps in {elapsed:.2f}s")
    print(f"Average: {args.steps / elapsed:.0f} steps/sec")


if __name__ == "__main__":
    main()
