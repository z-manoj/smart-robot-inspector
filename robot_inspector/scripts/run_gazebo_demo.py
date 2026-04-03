#!/usr/bin/env python3
"""
Automated Gazebo warehouse inspection demo.
Demonstrates full workflow: navigation, inspection, report generation.
"""

import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Pose, Point, Quaternion
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import json
import math
import time
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class GazeboDemoNode(Node):
    """Main demo node for Gazebo inspection."""

    def __init__(self):
        super().__init__('gazebo_demo')

        # Publishers and subscribers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        self.analysis_sub = self.create_subscription(
            String,
            '/robot_inspector/analysis',
            self.analysis_callback,
            10
        )

        # State
        self.current_pose = Pose()
        self.current_position = Point()
        self.current_yaw = 0.0
        self.latest_analysis = None
        self.inspection_results = []
        self.inspection_count = 0

        # Waypoints for inspection
        self.waypoints = [
            {'id': 1, 'x': 1.0, 'y': 0.0, 'name': 'Shelf 1', 'description': 'Normal shelf - red/green/blue items'},
            {'id': 2, 'x': 1.0, 'y': 3.0, 'name': 'Shelf 2', 'description': 'Damaged shelf - tilted/fallen items'},
            {'id': 3, 'x': 1.0, 'y': 6.0, 'name': 'Shelf 3', 'description': 'Normal shelf - yellow/cyan/purple items'},
        ]

        # Configuration
        self.movement_speed = 0.3  # m/s
        self.angular_speed = 0.5   # rad/s
        self.inspection_duration = 15  # seconds - wait for Bedrock analysis
        self.position_tolerance = 0.1  # meters
        self.angle_tolerance = 0.1    # radians

        self.get_logger().info("Gazebo Demo Node initialized")
        self.get_logger().info(f"  Inspection waypoints: {len(self.waypoints)}")
        self.get_logger().info(f"  Movement speed: {self.movement_speed} m/s")
        self.get_logger().info(f"  Inspection duration: {self.inspection_duration}s")

    def odom_callback(self, msg: Odometry):
        """Update position from odometry."""
        self.current_pose = msg.pose.pose
        self.current_position = msg.pose.pose.position

        # Extract yaw from quaternion
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.current_yaw = math.atan2(siny_cosp, cosy_cosp)

    def analysis_callback(self, msg: String):
        """Receive analysis results from inspector node."""
        try:
            data = json.loads(msg.data)
            self.latest_analysis = data
            self.get_logger().info(
                f"Received analysis: {data['analysis']['overall_status']} "
                f"({len(data['analysis'].get('detected_issues', []))} issues)"
            )
        except Exception as e:
            self.get_logger().error(f"Error parsing analysis: {e}")

    def publish_velocity(self, linear_x: float, angular_z: float):
        """Publish velocity command."""
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        self.cmd_vel_pub.publish(msg)

    def stop(self):
        """Stop robot movement."""
        self.publish_velocity(0.0, 0.0)

    def move_to_waypoint(self, target_x: float, target_y: float, waypoint_name: str = "Waypoint") -> bool:
        """
        Move robot to target waypoint.

        Args:
            target_x: Target X position
            target_y: Target Y position
            waypoint_name: Name of waypoint for logging

        Returns:
            True if reached waypoint
        """
        self.get_logger().info(f"Moving to {waypoint_name} ({target_x:.2f}, {target_y:.2f})")

        start_time = time.time()
        timeout = 60  # seconds

        while time.time() - start_time < timeout:
            # Calculate distance to target
            dx = target_x - self.current_position.x
            dy = target_y - self.current_position.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.position_tolerance:
                self.get_logger().info(f"Reached {waypoint_name}")
                self.stop()
                return True

            # Calculate target angle
            target_angle = math.atan2(dy, dx)
            angle_diff = target_angle - self.current_yaw

            # Normalize angle to [-pi, pi]
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

            # Rotate if needed
            if abs(angle_diff) > self.angle_tolerance:
                angular_z = self.angular_speed if angle_diff > 0 else -self.angular_speed
                self.publish_velocity(0.0, angular_z)
            else:
                # Move forward
                self.publish_velocity(self.movement_speed, 0.0)

            # Process callbacks so odom_callback fires
            rclpy.spin_once(self, timeout_sec=0.1)

        self.get_logger().warn(f"Timeout reaching {waypoint_name}")
        self.stop()
        return False

    def face_direction(self, target_yaw: float):
        """Turn robot to face a specific direction (yaw angle in radians)."""
        start_time = time.time()
        while time.time() - start_time < 10:
            angle_diff = target_yaw - self.current_yaw
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

            if abs(angle_diff) < self.angle_tolerance:
                self.stop()
                rclpy.spin_once(self, timeout_sec=0.1)
                return
            angular_z = self.angular_speed if angle_diff > 0 else -self.angular_speed
            self.publish_velocity(0.0, angular_z)
            rclpy.spin_once(self, timeout_sec=0.1)
        self.stop()

    def inspect_waypoint(self, waypoint: dict) -> dict:
        """
        Inspect a waypoint.

        Args:
            waypoint: Waypoint dict with id, x, y, name, description

        Returns:
            Inspection result dict
        """
        self.get_logger().info(f"Inspecting {waypoint['name']}: {waypoint['description']}")

        # Move to waypoint
        self.move_to_waypoint(waypoint['x'], waypoint['y'], waypoint['name'])

        # Turn to face the shelf (shelves are at x=3, robot at x=1, so face +x = yaw 0)
        self.get_logger().info(f"Turning to face {waypoint['name']}...")
        self.face_direction(0.0)  # Face +x direction

        # Wait for inspection and image analysis
        self.latest_analysis = None
        start_time = time.time()

        while time.time() - start_time < self.inspection_duration:
            if self.latest_analysis:
                break
            rclpy.spin_once(self, timeout_sec=0.5)

        self.inspection_count += 1

        # Collect results
        result = {
            'waypoint_id': waypoint['id'],
            'waypoint_name': waypoint['name'],
            'position': {
                'x': float(self.current_position.x),
                'y': float(self.current_position.y),
                'z': float(self.current_position.z),
            },
            'timestamp': datetime.now().isoformat(),
            'analysis': self.latest_analysis['analysis'] if self.latest_analysis else None,
        }

        self.inspection_results.append(result)

        # Print summary
        if result['analysis']:
            status = result['analysis']['overall_status']
            issues = len(result['analysis'].get('detected_issues', []))
            confidence = result['analysis'].get('confidence_score', 0)
            self.get_logger().info(
                f"✓ {waypoint['name']}: {status} "
                f"({issues} issues, {confidence:.1%} confidence)"
            )
        else:
            self.get_logger().warn(f"✗ {waypoint['name']}: No analysis received")

        time.sleep(2)  # Pause between waypoints

        return result

    def run_demo(self) -> bool:
        """
        Run complete inspection demo.

        Returns:
            True if successful
        """
        self.get_logger().info("=" * 70)
        self.get_logger().info("GAZEBO WAREHOUSE INSPECTION DEMO")
        self.get_logger().info("=" * 70)
        self.get_logger().info(f"Starting demo at {datetime.now().isoformat()}")
        self.get_logger().info(f"Total waypoints: {len(self.waypoints)}")

        demo_start = time.time()

        # Inspect each waypoint
        for waypoint in self.waypoints:
            try:
                self.inspect_waypoint(waypoint)
            except Exception as e:
                self.get_logger().error(f"Error inspecting {waypoint['name']}: {e}")

        demo_end = time.time()
        demo_duration = demo_end - demo_start

        # Generate report
        self.generate_report(demo_duration)

        self.get_logger().info("=" * 70)
        self.get_logger().info("DEMO COMPLETE")
        self.get_logger().info("=" * 70)

        return True

    def generate_report(self, duration: float):
        """
        Generate inspection report.

        Args:
            duration: Demo duration in seconds
        """
        self.get_logger().info("Generating inspection report...")

        # Create report directory
        report_dir = Path('./gazebo_demo_reports')
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_id = f"gazebo_demo_{timestamp}"

        # Aggregate statistics
        total_issues = 0
        critical_count = 0
        high_count = 0

        for result in self.inspection_results:
            if result['analysis']:
                issues = result['analysis'].get('detected_issues', [])
                total_issues += len(issues)
                for issue in issues:
                    severity = issue.get('severity', '').upper()
                    if severity == 'CRITICAL':
                        critical_count += 1
                    elif severity == 'HIGH':
                        high_count += 1

        # Overall status
        if critical_count > 0:
            overall_status = 'FAIL'
        elif high_count > 0:
            overall_status = 'REVIEW_REQUIRED'
        else:
            overall_status = 'PASS'

        # Create JSON report
        json_report = {
            'report_id': report_id,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'inspection_count': self.inspection_count,
            'overall_status': overall_status,
            'summary': {
                'total_issues': total_issues,
                'critical_issues': critical_count,
                'high_issues': high_count,
                'waypoints_inspected': len(self.inspection_results),
            },
            'inspection_results': self.inspection_results,
        }

        # Save JSON
        json_file = report_dir / f"{report_id}.json"
        with open(json_file, 'w') as f:
            json.dump(json_report, f, indent=2)
        self.get_logger().info(f"JSON report: {json_file}")

        # Create Markdown report
        md_content = f"""# Gazebo Warehouse Inspection Report

**Report ID:** {report_id}
**Generated:** {json_report['timestamp']}
**Duration:** {duration:.2f} seconds
**Overall Status:** `{overall_status}`

## Summary

- **Waypoints Inspected:** {len(self.inspection_results)}
- **Total Issues:** {total_issues}
- **Critical Issues:** {critical_count}
- **High Priority Issues:** {high_count}

## Inspection Results

"""

        for result in self.inspection_results:
            md_content += f"\n### {result['waypoint_name']}\n\n"
            md_content += f"**Position:** ({result['position']['x']:.2f}, {result['position']['y']:.2f}, {result['position']['z']:.2f})\n\n"

            if result['analysis']:
                analysis = result['analysis']
                md_content += f"**Status:** {analysis['overall_status']}\n\n"
                md_content += f"**Confidence:** {analysis.get('confidence_score', 0):.1%}\n\n"

                issues = analysis.get('detected_issues', [])
                if issues:
                    md_content += "**Issues Found:**\n\n"
                    for issue in issues:
                        md_content += f"- **[{issue.get('severity', 'UNKNOWN')}]** {issue.get('issue', 'Unknown')}\n"
                        md_content += f"  - Location: {issue.get('location', 'N/A')}\n"
                        md_content += f"  - Recommendation: {issue.get('recommendation', 'N/A')}\n\n"
                else:
                    md_content += "**No issues detected**\n\n"
            else:
                md_content += "**Status:** Analysis not received\n\n"

        # Save Markdown
        md_file = report_dir / f"{report_id}.md"
        with open(md_file, 'w') as f:
            f.write(md_content)
        self.get_logger().info(f"Markdown report: {md_file}")

        # Print summary
        self.get_logger().info("")
        self.get_logger().info("DEMO SUMMARY")
        self.get_logger().info("-" * 70)
        self.get_logger().info(f"Duration: {duration:.2f} seconds")
        self.get_logger().info(f"Inspections: {self.inspection_count}")
        self.get_logger().info(f"Overall Status: {overall_status}")
        self.get_logger().info(f"Total Issues: {total_issues}")
        self.get_logger().info(f"  - Critical: {critical_count}")
        self.get_logger().info(f"  - High: {high_count}")
        self.get_logger().info(f"Reports saved to: {report_dir}")


def main():
    """Main entry point."""
    rclpy.init()

    try:
        node = GazeboDemoNode()

        # Give ROS2 time to initialize
        time.sleep(2)

        # Run demo
        success = node.run_demo()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
