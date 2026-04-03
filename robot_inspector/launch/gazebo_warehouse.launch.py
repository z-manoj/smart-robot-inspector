"""
Launch file for Gazebo warehouse simulation with inspector node.
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for Gazebo warehouse."""

    pkg_share = FindPackageShare('robot_inspector')

    # Launch arguments
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='warehouse.world',
        description='Gazebo world file'
    )

    headless_arg = DeclareLaunchArgument(
        'headless',
        default_value='false',
        description='Run Gazebo in headless mode'
    )

    verbose_arg = DeclareLaunchArgument(
        'verbose',
        default_value='false',
        description='Enable verbose output'
    )

    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Run Gazebo GUI'
    )

    # Get world file path
    world_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'worlds',
        LaunchConfiguration('world')
    )

    # Start Gazebo server
    gazebo_server = ExecuteProcess(
        cmd=['gazebo', '--verbose', world_path],
        output='screen'
    )

    # Start Gazebo client (GUI) if not headless
    gazebo_client = ExecuteProcess(
        cmd=['gazebo_gui'],
        output='screen',
        condition=lambda context: LaunchConfiguration('headless') != 'true'
    )

    # ROS 2 bridge (if available)
    ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        output='screen'
    )

    # Inspector node
    inspector_node = Node(
        package='robot_inspector',
        executable='inspector_node',
        output='screen',
        parameters=[
            {'bedrock_region': 'us-east-1'},
            {'model_id': 'us.anthropic.claude-opus-4-6-v1'},
            {'image_topic': '/camera/image_raw'},
            {'analysis_topic': '/robot_inspector/analysis'},
            {'report_output_dir': './gazebo_reports'},
            {'inspection_interval_ms': 2000},
            {'confidence_threshold': 0.70},
            {'enable_visualization': True},
        ]
    )

    return LaunchDescription([
        world_arg,
        headless_arg,
        verbose_arg,
        gui_arg,
        gazebo_server,
        gazebo_client,
        ros_bridge,
        inspector_node,
    ])
