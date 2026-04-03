#!/bin/bash
# Quick launcher for Gazebo warehouse demo

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Source ROS2
source /opt/ros/jazzy/setup.bash

# Activate venv
source venv/bin/activate

# Install robot_inspector in editable mode if not already done
if ! python3 -c "import robot_inspector" 2>/dev/null; then
    echo "Installing robot_inspector..."
    cd robot_inspector
    pip install -e . -q
    cd ..
fi

# Add package to ROS_PACKAGE_PATH
export ROS_PACKAGE_PATH="$SCRIPT_DIR/robot_inspector:$ROS_PACKAGE_PATH"

echo "🚀 Launching Gazebo warehouse with visualization..."
echo ""
echo "Starting components:"
echo "  1. Gazebo warehouse simulation"
echo "  2. ROS2-Gazebo bridge (topic remapping)"
echo "  3. Inspector node (Claude AI analysis)"
echo "  4. RViz visualization"
echo "  5. Demo script (autonomous inspection)"
echo ""

# Try to run via ros2 launch if available, otherwise run directly
if ros2 launch robot_inspector gazebo_warehouse_with_viz.launch.py 2>/dev/null; then
    exit $?
else
    echo "Note: ros2 launch couldn't find the package."
    echo "Running components individually..."
    echo ""

    # Start Gazebo (try both old and new command names)
    echo "Starting Gazebo..."
    # Set Gazebo model path so it can find our robot model
    export GZ_SIM_RESOURCE_PATH="$SCRIPT_DIR/robot_inspector/models:$GZ_SIM_RESOURCE_PATH"
    if command -v gz &> /dev/null; then
        # Start server with auto-run (-r), then GUI separately
        gz sim -s -r "$SCRIPT_DIR/robot_inspector/worlds/warehouse.world" &
        SERVER_PID=$!
        sleep 3
        gz sim -g &
        GUI_PID=$!
    else
        echo "❌ Gazebo not found in PATH"
        echo "Install from: https://gazebosim.org/docs/harmonic/install_ubuntu/"
        exit 1
    fi
    GAZEBO_PID=$SERVER_PID
    sleep 3
    echo "✅ Gazebo started with warehouse world and robot"

    # Start ROS2 bridge
    echo "Starting ROS2 bridge..."
    ros2 run ros_gz_bridge parameter_bridge \
        '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image' \
        '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist' \
        '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry' &
    BRIDGE_PID=$!
    sleep 2

    # Start inspector node
    echo "Starting inspector node..."
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    export AWS_PROFILE=${AWS_PROFILE:-claude}
    export AWS_REGION=${AWS_REGION:-us-east-1}
    cd "$SCRIPT_DIR/robot_inspector"
    python3 -m robot_inspector.ros_node &
    NODE_PID=$!
    cd "$SCRIPT_DIR"
    sleep 2

    # Start RViz
    echo "Starting RViz..."
    rviz2 -d "$SCRIPT_DIR/robot_inspector/config/gazebo_warehouse.rviz" &
    RVIZ_PID=$!
    sleep 2

    # Start demo
    echo "Starting demo..."
    python3 "$SCRIPT_DIR/robot_inspector/scripts/run_gazebo_demo.py"

    # Cleanup
    kill $NODE_PID $BRIDGE_PID $RVIZ_PID $GAZEBO_PID $GUI_PID 2>/dev/null || true
fi
