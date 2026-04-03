# Gazebo Warehouse Simulation Setup Guide

This guide covers setting up and running the Gazebo warehouse simulation with the Smart Robot Inspector system.

## Prerequisites

- Ubuntu 22.04 LTS
- ROS2 Humble with Gazebo Garden
- Python 3.10+
- AWS credentials configured for Bedrock
- robot_inspector package installed

### System Requirements

```bash
# Install Gazebo (if not already installed with ROS2)
sudo apt-get install gazebo

# Install ROS2 Gazebo bridge
sudo apt-get install ros-humble-ros-gz-bridge

# Install RViz2 (for visualization)
sudo apt-get install ros-humble-rviz2

# Install trajectory and control packages
sudo apt-get install ros-humble-tf-transformations
```

## Project Structure

```
robot_inspector/
├── worlds/
│   └── warehouse.world              # Gazebo world with shelves and lighting
├── models/
│   └── mobile_robot/
│       └── model.sdf               # Robot URDF with wheels and camera
├── launch/
│   ├── gazebo_warehouse.launch.py  # Basic Gazebo launch
│   └── gazebo_warehouse_with_viz.launch.py  # Full system with RViz
├── config/
│   ├── gazebo_params.yaml          # Simulation parameters
│   └── gazebo_warehouse.rviz       # RViz visualization config
├── scripts/
│   ├── gazebo_utils.py             # RobotController utility class
│   └── run_gazebo_demo.py          # Demo orchestration script
└── docs/
    └── GAZEBO_SETUP.md             # This file
```

## Quick Start

### 1. Basic Setup

```bash
# Navigate to workspace
cd ~/ros2_ws

# Source ROS2 setup
source /opt/ros/humble/setup.bash
source install/setup.bash

# Source environment for AWS credentials
export AWS_REGION=us-east-1
export AWS_PROFILE=default  # or your profile name
```

### 2. Launch Gazebo Simulation Only

```bash
# Terminal 1: Launch Gazebo with warehouse world
ros2 launch robot_inspector gazebo_warehouse.launch.py

# This starts:
# - Gazebo server and GUI
# - Warehouse world with 3 shelves
# - Mobile robot with camera
```

### 3. Full System Launch (Recommended)

```bash
# Terminal: Launch full system with visualization and demo
ros2 launch robot_inspector gazebo_warehouse_with_viz.launch.py

# This starts:
# - Gazebo server and GUI
# - ROS2 Gazebo bridge for topic mapping
# - Inspector node (AI analysis via Bedrock)
# - RViz visualization
# - Automated demo script
```

## Launch Arguments

### gazebo_warehouse.launch.py

```bash
ros2 launch robot_inspector gazebo_warehouse.launch.py \
  world:=warehouse.world \
  headless:=false \
  verbose:=true \
  gui:=true
```

**Arguments:**
- `world` - Gazebo world file (default: warehouse.world)
- `headless` - Run without GUI (default: false)
- `verbose` - Enable verbose output (default: false)
- `gui` - Show Gazebo GUI (default: true)

### gazebo_warehouse_with_viz.launch.py

```bash
ros2 launch robot_inspector gazebo_warehouse_with_viz.launch.py \
  world:=warehouse.world \
  headless:=false \
  use_rviz:=true \
  run_demo:=true \
  bedrock_region:=us-east-1 \
  model_id:=us.anthropic.claude-opus-4-6-v1
```

**Arguments:**
- `world` - Gazebo world file (default: warehouse.world)
- `headless` - Run Gazebo without GUI (default: false)
- `use_rviz` - Launch RViz visualization (default: true)
- `run_demo` - Run automated demo script (default: true)
- `bedrock_region` - AWS Bedrock region (default: us-east-1)
- `model_id` - Claude model ID (default: us.anthropic.claude-opus-4-6-v1)

## Running the Demo

### Automated Demo

The full system launch includes an automated inspection demo:

```bash
ros2 launch robot_inspector gazebo_warehouse_with_viz.launch.py
```

The demo will:
1. Navigate to Shelf 1 (2.0, -1.0)
2. Inspect for 5 seconds (camera analysis via Claude)
3. Navigate to Shelf 2 (2.0, 1.25) - intentionally has damage
4. Inspect for 5 seconds
5. Navigate to Shelf 3 (2.0, 3.5)
6. Inspect for 5 seconds
7. Generate comprehensive reports (JSON + Markdown)
8. Save reports to `gazebo_demo_reports/` directory

### Manual Control

To control the robot manually while the system is running:

```bash
# In another terminal
ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3, y: 0, z: 0}, angular: {x: 0, y: 0, z: 0}}"
```

### Monitor Topics

```bash
# Monitor camera images
ros2 topic echo /camera/image_raw

# Monitor odometry (position/orientation)
ros2 topic echo /odom

# Monitor analysis results
ros2 topic echo /robot_inspector/analysis

# List all active topics
ros2 topic list
```

## System Components

### Gazebo World (warehouse.world)

- **Size:** 100m x 100m ground plane
- **Lighting:** Directional sun with shadows
- **Shelves:** 3 warehouse shelves at different Y positions
  - Shelf 1 @ (2.0, -1.0): Normal items (red, green, blue)
  - Shelf 2 @ (2.0, 1.25): Contains damaged (dark) item for defect detection
  - Shelf 3 @ (2.0, 3.5): Normal items (red, green, blue)

### Mobile Robot (model.sdf)

- **Base:** 0.5m × 0.3m × 0.2m box
- **Wheels:** Differential drive (0.36m separation, 0.1m diameter)
- **Caster:** Front caster wheel for stability
- **Camera:** 320×240 @ 30Hz, 60° FOV, mounted on top
- **Topics:**
  - Subscribes to `/cmd_vel` for velocity commands
  - Publishes to `/odom` for odometry feedback
  - Camera publishes to `/camera/image_raw` (via bridge)

### Inspector Node (ros_node.py)

- Subscribes to `/camera/image_raw` (from Gazebo camera)
- Sends images to Claude via AWS Bedrock for analysis
- Publishes analysis results to `/robot_inspector/analysis`
- Configuration via ROS2 parameter server
- Threading for non-blocking image processing

### Demo Script (run_gazebo_demo.py)

- Orchestrates waypoint navigation
- Waits for analysis at each location
- Collects and aggregates results
- Generates final inspection report

## Configuration

### Inspector Parameters

Edit `config/gazebo_params.yaml`:

```yaml
inspector_node:
  bedrock_region: us-east-1
  model_id: us.anthropic.claude-opus-4-6-v1
  image_topic: /camera/image_raw
  analysis_topic: /robot_inspector/analysis
  inspection_interval_ms: 2000
  confidence_threshold: 0.70
  enable_visualization: true
```

### Simulation Parameters

Edit `config/gazebo_params.yaml`:

```yaml
gazebo:
  world_file: warehouse.world
  physics_engine: ode
  max_step_size: 0.001
  real_time_factor: 1.0
  
  robot:
    max_linear_velocity: 0.5  # m/s
    max_angular_velocity: 1.0  # rad/s
```

## Output Files

After running the demo, inspection reports are saved to:

```
gazebo_demo_reports/
├── gazebo_demo_YYYYMMDD_HHMMSS.json       # Structured data
├── gazebo_demo_YYYYMMDD_HHMMSS.md         # Human-readable report
└── gazebo_demo_YYYYMMDD_HHMMSS.html       # HTML visualization
```

### Report Contents

**JSON Report:**
- Report ID and timestamp
- Demo duration and inspection count
- Overall status (PASS/REVIEW_REQUIRED/FAIL)
- Summary statistics (total issues, critical, high priority)
- Detailed results per waypoint

**Markdown Report:**
- Executive summary
- Per-waypoint analysis
- Issues with severity, location, recommendations
- Formatted for easy reading

## Troubleshooting

### Gazebo Won't Start

```bash
# Check Gazebo installation
gazebo --version

# Try standalone world file
gazebo ~/ros2_ws/src/robot_inspector/robot_inspector/worlds/warehouse.world

# Check for GPU issues (try software rendering)
export LIBGL_ALWAYS_INDIRECT=1
gazebo
```

### No Camera Images

```bash
# Check if ROS2 bridge is running
ros2 node list | grep bridge

# Verify camera topic
ros2 topic list | grep camera

# Check image resolution
ros2 topic info /camera/image_raw
```

### Inspector Node Not Analyzing

```bash
# Verify node is running
ros2 node list | grep inspector

# Check parameters
ros2 param list /inspector_node
ros2 param get /inspector_node bedrock_region

# Monitor analysis topic
ros2 topic echo /robot_inspector/analysis --once

# Check AWS credentials
aws bedrock list-foundation-models --region us-east-1
```

### Demo Script Timeout

- Increase `inspection_duration` in `run_gazebo_demo.py`
- Check network connectivity to AWS
- Verify Bedrock quotas not exceeded

### RViz Displays Nothing

```bash
# Verify TF (transforms) are being published
ros2 topic echo /tf

# Set correct fixed frame in RViz (should be "odom")
# Add displays: RobotModel, TF, Grid

# Check robot description
ros2 param get /inspector_node robot_description
```

## Performance Tuning

### Reduce Inspection Interval

For faster analysis cycles:

```bash
ros2 launch robot_inspector gazebo_warehouse_with_viz.launch.py \
  gazebo_params:='{inspection_interval_ms: 1000}'
```

### Headless Mode for Server Deployment

```bash
ros2 launch robot_inspector gazebo_warehouse_with_viz.launch.py \
  headless:=true \
  use_rviz:=false \
  run_demo:=true
```

### Disable Visualization to Save CPU

```bash
ros2 launch robot_inspector gazebo_warehouse_with_viz.launch.py \
  use_rviz:=false
```

## Next Steps

1. **Custom Worlds:** Create additional warehouse layouts in `worlds/`
2. **Multiple Robots:** Add more mobile_robot instances with unique namespaces
3. **Sensor Fusion:** Integrate LiDAR or depth camera data
4. **Path Planning:** Add Nav2 stack for autonomous navigation beyond waypoints
5. **Real Hardware:** Deploy inspector node to real robot (same code, no Gazebo)

## Additional Resources

- [ROS2 Humble Documentation](https://docs.ros.org/en/humble/)
- [Gazebo Simulation](https://gazebosim.org/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude AI Documentation](https://docs.anthropic.com/)
