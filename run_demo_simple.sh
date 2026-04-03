#!/bin/bash
# Simple demo launcher - runs Python demo directly without ROS2 bridge

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Smart Robot Inspector - Gazebo Warehouse Demo             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Source ROS2
source /opt/ros/jazzy/setup.bash

# Activate venv
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# Install robot_inspector if not already done
if ! python3 -c "import robot_inspector" 2>/dev/null; then
    echo "Installing robot_inspector..."
    cd robot_inspector
    pip install -e . -q
    cd ..
fi

echo ""
echo "🚀 Starting Gazebo warehouse simulation..."
echo ""
echo "Components:"
echo "  1. Gazebo (warehouse world)"
echo "  2. Demo script (autonomous inspection)"
echo ""
echo "Note: ROS2 bridge not required for this demo"
echo "The demo uses direct Python + Gazebo integration"
echo ""

# Start Gazebo in background
echo "Starting Gazebo..."
gz sim --verbose "$SCRIPT_DIR/robot_inspector/worlds/warehouse.world" &
GAZEBO_PID=$!
sleep 3

# Run demo script
echo ""
echo "Starting demo script..."
python3 "$SCRIPT_DIR/robot_inspector/scripts/run_gazebo_demo.py"
DEMO_EXIT=$?

# Cleanup
echo ""
echo "Cleaning up..."
kill $GAZEBO_PID 2>/dev/null || true

if [ $DEMO_EXIT -eq 0 ]; then
    echo ""
    echo "✅ Demo completed successfully!"
    echo ""
    echo "Reports saved to: $(pwd)/gazebo_demo_reports/"
    echo "  - gazebo_demo_*.json (structured data)"
    echo "  - gazebo_demo_*.md (human-readable report)"
else
    echo ""
    echo "⚠️  Demo ended (interrupted or error)"
fi
