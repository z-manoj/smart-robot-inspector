#!/bin/bash
# Spawn robot model in Gazebo

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source /opt/ros/jazzy/setup.bash

echo "Spawning mobile_robot in Gazebo..."

# Get the path to the robot model
ROBOT_MODEL="$SCRIPT_DIR/robot_inspector/models/mobile_robot/model.sdf"

if [ ! -f "$ROBOT_MODEL" ]; then
    echo "❌ Robot model not found at: $ROBOT_MODEL"
    exit 1
fi

# Spawn the robot at origin
gz model --spawn-file "$ROBOT_MODEL" \
    --model-name mobile_robot \
    --pose "0 0 0.1 0 0 0"

if [ $? -eq 0 ]; then
    echo "✅ Robot spawned successfully"
else
    echo "⚠️  Robot spawn command sent (check Gazebo window)"
fi
