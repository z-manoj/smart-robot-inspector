"""
Launch file for Gazebo warehouse simulation with RViz visualization.

Starts:
- Gazebo server and GUI with warehouse world
- ROS2 bridge for topic remapping
- Inspector node for AI analysis
- RViz for visualization
- Demo orchestration script
"""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    LogInfo,
)
from launch.substitutions import LaunchConfiguration, FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for Gazebo warehouse with visualization."""

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
        description='Run Gazebo in headless mode (no GUI)'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz visualization'
    )

    run_demo_arg = DeclareLaunchArgument(
        'run_demo',
        default_value='true',
        description='Run automated demo script'
    )

    bedrock_region_arg = DeclareLaunchArgument(
        'bedrock_region',
        default_value='us-east-1',
        description='AWS Bedrock region'
    )

    model_id_arg = DeclareLaunchArgument(
        'model_id',
        default_value='us.anthropic.claude-opus-4-6-v1',
        description='Claude model ID from Bedrock'
    )

    # Get world file path
    world_file = LaunchConfiguration('world')
    pkg_worlds = FindPackageShare('robot_inspector', 'worlds', world_file)

    # Start Gazebo server
    gazebo_server = ExecuteProcess(
        cmd=['gazebo', '--verbose', pkg_worlds],
        output='screen'
    )

    # Start Gazebo client (GUI) if not headless
    gazebo_client = ExecuteProcess(
        cmd=['gazebo_gui'],
        output='screen',
        condition=lambda context: LaunchConfiguration('headless').perform(context) != 'true'
    )

    # ROS 2 Gazebo bridge for topic remapping
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
        ],
        output='screen',
        remappings=[
            ('/cmd_vel', '/robot/cmd_vel'),
        ]
    )

    # Inspector node (AI analysis)
    inspector_node = Node(
        package='robot_inspector',
        executable='inspector_node',
        output='screen',
        parameters=[
            {'bedrock_region': LaunchConfiguration('bedrock_region')},
            {'model_id': LaunchConfiguration('model_id')},
            {'image_topic': '/camera/image_raw'},
            {'analysis_topic': '/robot_inspector/analysis'},
            {'report_output_dir': './gazebo_reports'},
            {'inspection_interval_ms': 2000},
            {'max_queue_size': 10},
            {'confidence_threshold': 0.70},
            {'enable_visualization': True},
        ]
    )

    # RViz visualization (optional)
    rviz_config = os.path.join(
        os.path.dirname(__file__),
        '..',
        'config',
        'gazebo_warehouse.rviz'
    )
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
        condition=lambda context: LaunchConfiguration('use_rviz').perform(context) == 'true'
    )

    # Demo orchestration script (optional)
    demo_script = ExecuteProcess(
        cmd=['ros2', 'run', 'robot_inspector', 'run_gazebo_demo'],
        output='screen',
        condition=lambda context: LaunchConfiguration('run_demo').perform(context) == 'true'
    )

    # Startup messages
    startup_msg = LogInfo(msg="Starting Gazebo warehouse simulation with ROS2 bridge and visualization")

    return LaunchDescription([
        startup_msg,
        world_arg,
        headless_arg,
        use_rviz_arg,
        run_demo_arg,
        bedrock_region_arg,
        model_id_arg,
        gazebo_server,
        gazebo_client,
        ros_gz_bridge,
        inspector_node,
        rviz,
        demo_script,
    ])
