from __future__ import annotations

import logging
from typing import Any

import numpy as np

try:
    import mujoco
except ImportError:
    mujoco = None  # type: ignore[assignment]

from src.config import SimulationConfig

logger = logging.getLogger(__name__)


class SimulationRenderer:
    def __init__(self, config: SimulationConfig | None = None):
        self.config = config or SimulationConfig()
        self._renderer: Any | None = None
        self._scene: Any | None = None
        self._camera: Any | None = None

    def initialize(self, model: Any) -> None:
        if mujoco is None:
            logger.warning("MuJoCo not installed, renderer unavailable")
            return

        self._renderer = mujoco.Renderer(
            model, height=self.config.render_height, width=self.config.render_width
        )
        self._camera = mujoco.MjvCamera()
        self._camera.azimuth = 135
        self._camera.elevation = -30
        self._camera.distance = 3.0
        self._camera.lookat[:] = [0, 0, 0.5]
        logger.info("Renderer initialized")

    def render_frame(self, model: Any, data: Any) -> np.ndarray | None:
        if self._renderer is None:
            return None

        self._renderer.update_scene(data, camera=self._camera)
        return self._renderer.render()

    def extract_pose_data(self, robots: list[dict[str, Any]]) -> list[dict[str, Any]]:
        poses = []
        for robot in robots:
            poses.append({
                "id": robot["id"],
                "position": robot["position"],
                "orientation": robot["orientation"],
                "joint_angles": robot["sensor_data"]["joint_angles"],
            })
        return poses

    def set_camera(
        self,
        azimuth: float | None = None,
        elevation: float | None = None,
        distance: float | None = None,
        lookat: list[float] | None = None,
    ) -> None:
        if self._camera is None:
            return
        if azimuth is not None:
            self._camera.azimuth = azimuth
        if elevation is not None:
            self._camera.elevation = elevation
        if distance is not None:
            self._camera.distance = distance
        if lookat is not None:
            self._camera.lookat[:] = lookat

    def close(self) -> None:
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None
