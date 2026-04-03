"""
ROS2 Launch file for Robot Inspector node.

Usage:
    ros2 launch robot_inspector inspector.launch.py

With parameters:
    ros2 launch robot_inspector inspector.launch.py bedrock_region:=us-west-2
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, FindPackageShare
from launch_ros.actions import Node
from pathlib import Path


def generate_launch_description():
    """Generate ROS2 launch description."""

    # Package share directory
    pkg_share = FindPackageShare('robot_inspector')

    # Launch arguments
    bedrock_region_arg = DeclareLaunchArgument(
        'bedrock_region',
        default_value='us-east-1',
        description='AWS Bedrock region'
    )

    model_id_arg = DeclareLaunchArgument(
        'model_id',
        default_value='us.anthropic.claude-opus-4-6-v1',
        description='Bedrock Claude model ID'
    )

    image_topic_arg = DeclareLaunchArgument(
        'image_topic',
        default_value='/camera/image_raw',
        description='Input camera image topic'
    )

    analysis_topic_arg = DeclareLaunchArgument(
        'analysis_topic',
        default_value='/robot_inspector/analysis',
        description='Output analysis topic'
    )

    report_dir_arg = DeclareLaunchArgument(
        'report_output_dir',
        default_value='./reports',
        description='Directory for report output'
    )

    interval_arg = DeclareLaunchArgument(
        'inspection_interval_ms',
        default_value='1000',
        description='Inspection interval in milliseconds'
    )

    queue_size_arg = DeclareLaunchArgument(
        'max_queue_size',
        default_value='10',
        description='Maximum image queue size'
    )

    confidence_arg = DeclareLaunchArgument(
        'confidence_threshold',
        default_value='0.70',
        description='Minimum confidence score threshold'
    )

    visualization_arg = DeclareLaunchArgument(
        'enable_visualization',
        default_value='true',
        description='Enable report generation and visualization'
    )

    # Launch info message
    launch_info = LogInfo(
        msg=[
            'Starting Robot Inspector Node',
            '\n  Bedrock Region: ', LaunchConfiguration('bedrock_region'),
            '\n  Model ID: ', LaunchConfiguration('model_id'),
            '\n  Image Topic: ', LaunchConfiguration('image_topic'),
            '\n  Analysis Topic: ', LaunchConfiguration('analysis_topic'),
        ]
    )

    # Inspector node
    inspector_node = Node(
        package='robot_inspector',
        executable='inspector_node',
        name='robot_inspector',
        output='screen',
        parameters=[
            {
                'bedrock_region': LaunchConfiguration('bedrock_region'),
                'model_id': LaunchConfiguration('model_id'),
                'image_topic': LaunchConfiguration('image_topic'),
                'analysis_topic': LaunchConfiguration('analysis_topic'),
                'report_output_dir': LaunchConfiguration('report_output_dir'),
                'inspection_interval_ms': LaunchConfiguration('inspection_interval_ms'),
                'max_queue_size': LaunchConfiguration('max_queue_size'),
                'confidence_threshold': LaunchConfiguration('confidence_threshold'),
                'enable_visualization': LaunchConfiguration('enable_visualization'),
            }
        ],
        remappings=[
            # Can remap topics at launch time if needed
            # ('/camera/image_raw', '/my_camera/image'),
        ]
    )

    # Return launch description with all components
    return LaunchDescription([
        bedrock_region_arg,
        model_id_arg,
        image_topic_arg,
        analysis_topic_arg,
        report_dir_arg,
        interval_arg,
        queue_size_arg,
        confidence_arg,
        visualization_arg,
        launch_info,
        inspector_node,
    ])
