#!/usr/bin/env python3
"""
Gazebo utilities for robot movement and inspection.
"""

import rclpy
from geometry_msgs.msg import Twist, Pose
from nav_msgs.msg import Odometry
import math
import time
import logging

logger = logging.getLogger(__name__)


class RobotController:
    """Control robot movement in Gazebo simulation."""

    def __init__(self, node):
        """Initialize robot controller."""
        self.node = node
        self.cmd_vel_pub = node.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = node.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        self.current_pose = Pose()
        self.target_reached = False

    def odom_callback(self, msg):
        """Update current pose from odometry."""
        self.current_pose = msg.pose.pose

    def move_forward(self, distance: float, speed: float = 0.3) -> bool:
        """
        Move robot forward for specified distance.

        Args:
            distance: Distance in meters
            speed: Linear velocity in m/s

        Returns:
            True if successful
        """
        logger.info(f"Moving forward {distance}m at {speed}m/s")

        cmd = Twist()
        cmd.linear.x = speed

        start_x = self.current_pose.position.x
        start_y = self.current_pose.position.y

        while rclpy.ok():
            # Calculate traveled distance
            dx = self.current_pose.position.x - start_x
            dy = self.current_pose.position.y - start_y
            traveled = math.sqrt(dx**2 + dy**2)

            if traveled >= distance:
                break

            self.cmd_vel_pub.publish(cmd)
            time.sleep(0.1)

        # Stop robot
        cmd.linear.x = 0.0
        self.cmd_vel_pub.publish(cmd)

        logger.info("Movement complete")
        return True

    def rotate(self, angle: float, angular_speed: float = 0.5) -> bool:
        """
        Rotate robot by specified angle.

        Args:
            angle: Rotation angle in radians
            angular_speed: Angular velocity in rad/s

        Returns:
            True if successful
        """
        logger.info(f"Rotating {math.degrees(angle)}° at {angular_speed} rad/s")

        cmd = Twist()
        cmd.angular.z = angular_speed if angle > 0 else -angular_speed

        start_yaw = self.get_yaw()
        rotated = 0

        while rclpy.ok():
            rotated = self.get_yaw() - start_yaw
            if abs(rotated) >= abs(angle):
                break

            self.cmd_vel_pub.publish(cmd)
            time.sleep(0.1)

        # Stop robot
        cmd.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd)

        logger.info("Rotation complete")
        return True

    def move_to_waypoint(self, target_x: float, target_y: float) -> bool:
        """
        Move robot to target waypoint.

        Args:
            target_x: Target X position
            target_y: Target Y position

        Returns:
            True if reached waypoint
        """
        logger.info(f"Moving to waypoint ({target_x}, {target_y})")

        # Calculate distance and angle to target
        dx = target_x - self.current_pose.position.x
        dy = target_y - self.current_pose.position.y
        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)
        current_yaw = self.get_yaw()

        # Rotate to face target
        angle_diff = target_angle - current_yaw
        # Normalize angle to [-pi, pi]
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

        if abs(angle_diff) > 0.1:
            self.rotate(angle_diff)

        # Move forward
        if distance > 0.1:
            self.move_forward(distance)

        logger.info(f"Reached waypoint")
        return True

    def stop(self):
        """Stop robot movement."""
        cmd = Twist()
        self.cmd_vel_pub.publish(cmd)

    def get_yaw(self) -> float:
        """Get current yaw angle in radians."""
        from tf_transformations import euler_from_quaternion
        quaternion = [
            self.current_pose.orientation.x,
            self.current_pose.orientation.y,
            self.current_pose.orientation.z,
            self.current_pose.orientation.w
        ]
        _, _, yaw = euler_from_quaternion(quaternion)
        return yaw

    def get_position(self) -> tuple:
        """Get current position as (x, y, z)."""
        return (
            self.current_pose.position.x,
            self.current_pose.position.y,
            self.current_pose.position.z
        )


class GazeboDemo:
    """Automated inspection demo in Gazebo."""

    def __init__(self, node):
        """Initialize demo."""
        self.node = node
        self.controller = RobotController(node)
        self.inspection_count = 0

    def run_inspection_sequence(self, waypoints: list) -> bool:
        """
        Run automated inspection sequence.

        Args:
            waypoints: List of (x, y, name) tuples

        Returns:
            True if successful
        """
        logger.info("Starting automated inspection sequence")

        for waypoint in waypoints:
            x, y, name = waypoint
            logger.info(f"Moving to {name} ({x}, {y})")

            # Move to waypoint
            self.controller.move_to_waypoint(x, y)

            # Wait for inspection
            logger.info(f"Inspecting {name}...")
            time.sleep(5)  # Allow time for analysis

            self.inspection_count += 1

        logger.info("Inspection sequence complete")
        return True


def main():
    """Demo usage."""
    rclpy.init()
    node = rclpy.create_node('gazebo_utils_demo')

    controller = RobotController(node)

    # Example waypoints
    waypoints = [
        (2.0, -1.0, "Shelf 1"),
        (2.0, 1.25, "Shelf 2"),
        (2.0, 3.5, "Shelf 3"),
    ]

    demo = GazeboDemo(node)

    try:
        demo.run_inspection_sequence(waypoints)
    except KeyboardInterrupt:
        controller.stop()
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
