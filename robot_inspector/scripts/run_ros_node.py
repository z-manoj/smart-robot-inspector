#!/usr/bin/env python3
"""
Standalone ROS2 Node Launcher for Robot Inspector.

Run without colcon build for quick testing and development.

Usage:
    python3 run_ros_node.py                 # Default parameters
    python3 run_ros_node.py --region us-west-2  # Custom region
"""

import sys
import argparse
import os

# Add parent directory to path to import robot_inspector package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import rclpy
from robot_inspector.ros_node import InspectorNode


def main():
    """Parse arguments and run the inspector node."""
    parser = argparse.ArgumentParser(
        description='ROS2 Inspector Node - Real-time defect detection'
    )

    parser.add_argument(
        '--region',
        type=str,
        default='us-east-1',
        help='AWS Bedrock region (default: us-east-1)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='us.anthropic.claude-opus-4-6-v1',
        help='Bedrock Claude model ID'
    )

    parser.add_argument(
        '--image-topic',
        type=str,
        default='/camera/image_raw',
        help='Input camera topic (default: /camera/image_raw)'
    )

    parser.add_argument(
        '--analysis-topic',
        type=str,
        default='/robot_inspector/analysis',
        help='Output analysis topic'
    )

    parser.add_argument(
        '--report-dir',
        type=str,
        default='./reports',
        help='Report output directory'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=1000,
        help='Inspection interval in milliseconds (default: 1000)'
    )

    parser.add_argument(
        '--queue-size',
        type=int,
        default=10,
        help='Maximum image queue size (default: 10)'
    )

    parser.add_argument(
        '--confidence',
        type=float,
        default=0.70,
        help='Confidence threshold (default: 0.70)'
    )

    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Disable visualization and report generation'
    )

    args = parser.parse_args()

    # Initialize ROS2
    rclpy.init(args=None)

    # Create node with custom parameters
    node = InspectorNode()

    # Override parameters from command line
    node.set_parameters([
        rclpy.parameter.Parameter(
            'bedrock_region',
            rclpy.Parameter.Type.STRING,
            args.region
        ),
        rclpy.parameter.Parameter(
            'model_id',
            rclpy.Parameter.Type.STRING,
            args.model
        ),
        rclpy.parameter.Parameter(
            'image_topic',
            rclpy.Parameter.Type.STRING,
            args.image_topic
        ),
        rclpy.parameter.Parameter(
            'analysis_topic',
            rclpy.Parameter.Type.STRING,
            args.analysis_topic
        ),
        rclpy.parameter.Parameter(
            'report_output_dir',
            rclpy.Parameter.Type.STRING,
            args.report_dir
        ),
        rclpy.parameter.Parameter(
            'inspection_interval_ms',
            rclpy.Parameter.Type.INTEGER,
            args.interval
        ),
        rclpy.parameter.Parameter(
            'max_queue_size',
            rclpy.Parameter.Type.INTEGER,
            args.queue_size
        ),
        rclpy.parameter.Parameter(
            'confidence_threshold',
            rclpy.Parameter.Type.DOUBLE,
            args.confidence
        ),
        rclpy.parameter.Parameter(
            'enable_visualization',
            rclpy.Parameter.Type.BOOL,
            not args.no_viz
        ),
    ])

    node.get_logger().info('Robot Inspector Node starting...')
    node.get_logger().info(f'  Region: {args.region}')
    node.get_logger().info(f'  Model: {args.model}')
    node.get_logger().info(f'  Image Topic: {args.image_topic}')
    node.get_logger().info(f'  Analysis Topic: {args.analysis_topic}')

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
