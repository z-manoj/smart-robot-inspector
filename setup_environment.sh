#!/bin/bash
# Setup script for Smart Robot Inspector

set -e

echo "Setting up Smart Robot Inspector environment..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Source ROS2
echo "Sourcing ROS2 Jazzy..."
source /opt/ros/jazzy/setup.bash

# Activate Python venv if it exists, otherwise create it
if [ -d "venv" ]; then
    echo "Activating Python virtual environment..."
    source venv/bin/activate
else
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel -q
fi

# Install dependencies
echo "Installing Python dependencies..."
pip install -q boto3 pillow opencv-python pyyaml numpy 2>/dev/null || true

# Add robot_inspector to PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
echo "Added robot_inspector to PYTHONPATH"

# Set ROS2 parameters
export ROS_DISTRO=jazzy

# Make sure robot_inspector is in ROS_PACKAGE_PATH
export ROS_PACKAGE_PATH="${SCRIPT_DIR}:${ROS_PACKAGE_PATH}"

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "To launch Gazebo warehouse with visualization, choose:"
echo ""
echo "Option 1 (Recommended - One Command):"
echo "  $SCRIPT_DIR/run_gazebo_demo.sh"
echo ""
echo "Option 2 (Manual - Multiple Terminals):"
echo "  See $SCRIPT_DIR/GAZEBO_QUICKSTART.md for step-by-step instructions"
echo ""
echo "In another terminal, activate the same environment with:"
echo "  source $SCRIPT_DIR/setup_environment.sh"
echo ""
