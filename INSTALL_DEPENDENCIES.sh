#!/bin/bash
# Install all dependencies for Smart Robot Inspector

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Smart Robot Inspector - Dependency Installation              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script requires sudo privileges"
    echo "Run with: sudo bash INSTALL_DEPENDENCIES.sh"
    exit 1
fi

echo "Updating package lists..."
apt-get update -qq

# Add Gazebo repository
echo "Adding Gazebo repository..."
apt-get install -y lsb-release wget -qq
wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
apt-get update -qq

# Gazebo Harmonic should already be installed
echo "Checking Gazebo installation..."
which gz > /dev/null && echo "✅ Gazebo Harmonic found" || echo "⚠️  Gazebo not in PATH - install from https://gazebosim.org/docs/harmonic/install_ubuntu/"

# Install ROS2-Gazebo bridge
echo "Installing ROS2-Gazebo bridge..."
apt-get install -y ros-jazzy-ros-gz-bridge -qq 2>/dev/null || \
apt-get install -y ros-jazzy-ros-gz -qq 2>/dev/null || \
echo "⚠️  ROS2-Gazebo bridge installation skipped"

# Install RViz2
echo "Installing RViz2..."
apt-get install -y ros-jazzy-rviz2 -qq

# Install nav_msgs and other ROS2 packages
echo "Installing ROS2 message packages..."
apt-get install -y \
    ros-jazzy-geometry-msgs \
    ros-jazzy-sensor-msgs \
    ros-jazzy-std-msgs \
    ros-jazzy-nav-msgs \
    ros-jazzy-cv-bridge \
    ros-jazzy-image-transport \
    -qq

# Install Python development tools
echo "Installing Python tools..."
apt-get install -y python3-dev python3-pip -qq

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "Next steps:"
echo "1. Create Python environment:"
echo "   cd /home/manojk/physical_ai_ryzen"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo ""
echo "2. Install Python packages:"
echo "   pip install boto3 pillow opencv-python pyyaml numpy"
echo "   cd robot_inspector && pip install -e . && cd .."
echo ""
echo "3. Run the demo:"
echo "   source venv/bin/activate"
echo "   ./run_gazebo_demo.sh"
echo ""
