from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ROS 2 bridge stub - requires rclpy and ROS 2 environment
# Install: pip install rclpy (requires ROS 2 Jazzy setup)

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String

    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False
    logger.info("ROS 2 not available. Install rclpy for ROS 2 support.")


class ROSBridge:
    def __init__(self):
        self._node: Any | None = None
        self._publishers: dict[str, Any] = {}
        self._subscribers: dict[str, Any] = {}

    @property
    def available(self) -> bool:
        return ROS_AVAILABLE

    def initialize(self, node_name: str = "fleet_manager") -> bool:
        if not ROS_AVAILABLE:
            logger.warning("ROS 2 not available, bridge not initialized")
            return False

        try:
            rclpy.init()
            self._node = Node(node_name)
            logger.info(f"ROS 2 node '{node_name}' initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ROS 2 node: {e}")
            return False

    def create_publisher(self, topic: str, robot_id: str) -> None:
        if self._node is None:
            return

        pub = self._node.create_publisher(String, f"/fleet/{robot_id}/{topic}", 10)
        self._publishers[f"{robot_id}/{topic}"] = pub
        logger.info(f"ROS 2 publisher created: /fleet/{robot_id}/{topic}")

    def create_subscriber(self, topic: str, robot_id: str, callback: Any) -> None:
        if self._node is None:
            return

        sub = self._node.create_subscription(
            String, f"/fleet/{robot_id}/{topic}", callback, 10
        )
        self._subscribers[f"{robot_id}/{topic}"] = sub
        logger.info(f"ROS 2 subscriber created: /fleet/{robot_id}/{topic}")

    def publish(self, topic: str, robot_id: str, data: str) -> None:
        key = f"{robot_id}/{topic}"
        if key in self._publishers:
            msg = String()
            msg.data = data
            self._publishers[key].publish(msg)

    def spin_once(self) -> None:
        if self._node:
            rclpy.spin_once(self._node, timeout_sec=0.01)

    def shutdown(self) -> None:
        if self._node:
            self._node.destroy_node()
            self._node = None
        if ROS_AVAILABLE:
            try:
                rclpy.shutdown()
            except Exception:
                pass
        logger.info("ROS 2 bridge shutdown")


ros_bridge = ROSBridge()
