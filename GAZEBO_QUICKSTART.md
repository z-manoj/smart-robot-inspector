# Quick Start: Gazebo Warehouse Simulation

## Prerequisites

✅ Already installed:
- ROS2 Jazzy
- Gazebo
- Python 3.10+
- AWS CLI configured with Bedrock access

## Setup (One-Time)

### 1. Install Dependencies

```bash
cd /home/manojk/physical_ai_ryzen

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install boto3 pillow opencv-python pyyaml numpy

# Install robot_inspector in editable mode
cd robot_inspector
pip install -e .
cd ..
```

### 2. Verify Setup

```bash
source venv/bin/activate

# Test Python import
python3 -c "import robot_inspector; print('✅ OK')"

# Test ROS2
source /opt/ros/jazzy/setup.bash
ros2 --version
```

## Running the Demo

### Option 1: Using Shell Script (Easiest)

```bash
cd /home/manojk/physical_ai_ryzen
source venv/bin/activate
./run_gazebo_demo.sh
```

This will:
1. Start Gazebo with warehouse world
2. Launch ROS2 bridge
3. Start Inspector node (Claude AI)
4. Open RViz visualization
5. Run automated demo

### Option 2: Manual Steps

**Terminal 1 - Gazebo:**
```bash
cd /home/manojk/physical_ai_ryzen
source /opt/ros/jazzy/setup.bash
gazebo --verbose robot_inspector/worlds/warehouse.world
```

**Terminal 2 - ROS2 Bridge:**
```bash
cd /home/manojk/physical_ai_ryzen
source /opt/ros/jazzy/setup.bash
source venv/bin/activate
ros2 run ros_gz_bridge parameter_bridge \
  '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image' \
  '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist' \
  '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'
```

**Terminal 3 - Inspector Node:**
```bash
cd /home/manojk/physical_ai_ryzen
source /opt/ros/jazzy/setup.bash
source venv/bin/activate
python3 -m robot_inspector.ros_node
```

**Terminal 4 - RViz:**
```bash
cd /home/manojk/physical_ai_ryzen
source /opt/ros/jazzy/setup.bash
rviz2 -d robot_inspector/config/gazebo_warehouse.rviz
```

**Terminal 5 - Demo:**
```bash
cd /home/manojk/physical_ai_ryzen
source /opt/ros/jazzy/setup.bash
source venv/bin/activate
python3 robot_inspector/scripts/run_gazebo_demo.py
```

## What Happens

The demo will:

1. **Start Robot** - Spawns mobile robot with camera in Gazebo
2. **Navigate** - Robot moves to Shelf 1 (2.0, -1.0)
3. **Inspect** - Captures images, analyzes with Claude AI via Bedrock
4. **Report** - Records findings (issues, severity, confidence)
5. **Repeat** - Moves to Shelves 2 and 3
6. **Generate** - Creates JSON and Markdown inspection reports

## Output Files

After running, check:
```bash
ls -la gazebo_demo_reports/
```

You'll see:
- `gazebo_demo_YYYYMMDD_HHMMSS.json` - Structured data
- `gazebo_demo_YYYYMMDD_HHMMSS.md` - Human-readable report

## Monitoring in Real-Time

While demo runs, in another terminal:

```bash
source /opt/ros/jazzy/setup.bash
source venv/bin/activate

# Watch camera images
ros2 topic echo /camera/image_raw --once

# Watch odometry (position/heading)
ros2 topic echo /odom --once

# Watch analysis results
ros2 topic echo /robot_inspector/analysis --once

# List all active topics
ros2 topic list
```

## Troubleshooting

### Gazebo Won't Start
```bash
# Try software rendering
export LIBGL_ALWAYS_INDIRECT=1
gazebo
```

### Package Not Found
```bash
# Make sure venv is activated
source venv/bin/activate

# Check robot_inspector is installed
python3 -c "import robot_inspector; print(robot_inspector.__file__)"
```

### No Camera Images
```bash
# Check ROS2 bridge is running
pgrep -l parameter_bridge

# Verify camera topic exists
ros2 topic list | grep camera
```

### Inspector Node Not Analyzing
```bash
# Check AWS credentials
aws bedrock list-foundation-models --region us-east-1

# Verify node is running
pgrep -l inspector_node

# Check analysis topic
ros2 topic echo /robot_inspector/analysis
```

### RViz Shows Nothing
- In RViz, set Fixed Frame to `odom`
- Add displays: RobotModel, TF, Grid
- Expand the tree on the left to see transforms

## System Architecture

```
Gazebo Simulator
  ├─ Warehouse world with 3 shelves
  ├─ Mobile robot (differential drive)
  └─ Camera (320×240 @ 30Hz)
       │
       ▼ /camera/image_raw
   ROS2 Bridge
       │
       ▼
   Inspector Node
       ├─ Subscribe: /camera/image_raw
       ├─ AWS Bedrock + Claude AI
       └─ Publish: /robot_inspector/analysis
           │
           ▼
       Demo Script
           ├─ Navigate waypoints
           ├─ Collect analyses
           └─ Generate reports
```

## Configuration

Edit parameters in `robot_inspector/config/gazebo_params.yaml`:

```yaml
inspector_node:
  bedrock_region: us-east-1
  model_id: us.anthropic.claude-opus-4-6-v1
  confidence_threshold: 0.70
  inspection_interval_ms: 2000
```

## Next Steps

1. **Custom Worlds** - Create additional warehouse layouts in `worlds/`
2. **Real Robot** - Deploy same code to actual mobile robot (no Gazebo needed)
3. **Multiple Robots** - Coordinate multiple inspections
4. **Database** - Store inspection history
5. **Web Dashboard** - View reports in browser

## Documentation

- Full setup guide: `robot_inspector/docs/GAZEBO_SETUP.md`
- ROS2 integration: `robot_inspector/README_ROS2.md`
- Project overview: `robot_inspector/README.md`

---

**Version**: 0.3.0  
**Status**: Production Ready  
**Last Updated**: April 3, 2026
