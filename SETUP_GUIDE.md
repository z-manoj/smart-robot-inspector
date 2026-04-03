# Complete Setup Guide for Smart Robot Inspector

## Quick Setup (5 minutes)

### Step 1: Install System Dependencies

```bash
cd /home/manojk/physical_ai_ryzen
sudo bash INSTALL_DEPENDENCIES.sh
```

**Prerequisites:**
- ROS2 Jazzy (in `/opt/ros/jazzy/`)
- Gazebo Harmonic (https://gazebosim.org/docs/harmonic/install_ubuntu/)

The script installs:
- ROS2-Gazebo bridge (ros_gz_bridge)
- RViz2 visualization
- Required ROS2 message packages

### Step 2: Create Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### Step 3: Install Python Packages

```bash
# Install core dependencies
pip install boto3 pillow opencv-python pyyaml numpy

# Install robot_inspector in editable mode
cd robot_inspector
pip install -e .
cd ..
```

### Step 4: Verify AWS Credentials

```bash
# Configure AWS if not already done
aws configure

# Verify Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### Step 5: Run the Demo

```bash
source venv/bin/activate
./run_gazebo_demo.sh
```

---

## Manual Multi-Terminal Setup (If Script Fails)

If the auto-launcher fails, run these in separate terminals:

### Terminal 1: Gazebo
```bash
source /opt/ros/jazzy/setup.bash
gazebo --verbose ~/physical_ai_ryzen/robot_inspector/worlds/warehouse.world
```

### Terminal 2: ROS2 Bridge
```bash
source /opt/ros/jazzy/setup.bash
source ~/physical_ai_ryzen/venv/bin/activate
ros2 run ros_gz_bridge parameter_bridge \
  '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image' \
  '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist' \
  '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'
```

### Terminal 3: Inspector Node
```bash
source /opt/ros/jazzy/setup.bash
source ~/physical_ai_ryzen/venv/bin/activate
cd ~/physical_ai_ryzen
python3 -m robot_inspector.ros_node
```

### Terminal 4: Demo Script
```bash
source /opt/ros/jazzy/setup.bash
source ~/physical_ai_ryzen/venv/bin/activate
cd ~/physical_ai_ryzen
python3 robot_inspector/scripts/run_gazebo_demo.py
```

### Terminal 5: RViz (Optional)
```bash
source /opt/ros/jazzy/setup.bash
rviz2 -d ~/physical_ai_ryzen/robot_inspector/config/gazebo_warehouse.rviz
```

---

## What Each Component Does

### Gazebo
Simulates the warehouse with:
- 3 shelves with colored items
- Mobile robot with camera
- Physics simulation
- Publishes: `/camera/image_raw`, `/odom`
- Subscribes to: `/cmd_vel`

### ROS2 Bridge
Connects Gazebo ↔ ROS2:
- Remaps Gazebo topics to standard ROS2 messages
- Makes camera images available to ROS2 nodes
- Converts velocity commands from ROS2 to Gazebo

### Inspector Node
Claude AI analysis:
- Subscribes to camera feed
- Sends images to AWS Bedrock
- Gets Claude's analysis of shelf items
- Publishes results to `/robot_inspector/analysis`

### Demo Script
Orchestrates the inspection:
- Navigates robot to waypoints
- Waits for Claude analysis at each location
- Collects results
- Generates JSON and Markdown reports

### RViz
3D visualization:
- Shows robot position and orientation
- Displays transforms
- Shows grid and coordinate system
- Optional (demo works without it)

---

## Troubleshooting

### gazebo: command not found
**Solution:** Install Gazebo
```bash
sudo apt-get install gazebo gazebo-dev -y
```

### Package 'ros_gz_bridge' not found
**Solution:** Install ROS2 Gazebo bridge
```bash
sudo apt-get install ros-jazzy-ros-gz-bridge -y
```

### Package 'robot_inspector' not found
**Solution:** Activate venv and install package
```bash
source venv/bin/activate
cd robot_inspector
pip install -e .
cd ..
```

### AWS Bedrock errors
**Solution:** Check credentials
```bash
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-east-1
```

### RViz won't start
**Solution:** Install RViz2
```bash
sudo apt-get install ros-jazzy-rviz2 -y
```

---

## One-Time Setup Checklist

- [ ] Run `sudo bash INSTALL_DEPENDENCIES.sh`
- [ ] Create Python venv: `python3 -m venv venv`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Install Python deps: `pip install boto3 pillow opencv-python pyyaml numpy`
- [ ] Install robot_inspector: `cd robot_inspector && pip install -e . && cd ..`
- [ ] Configure AWS: `aws configure`
- [ ] Verify Bedrock: `aws bedrock list-foundation-models --region us-east-1`

## Every Session

```bash
cd /home/manojk/physical_ai_ryzen
source venv/bin/activate
./run_gazebo_demo.sh
```

Or for manual setup, run the 4-5 terminal commands above.

---

## Expected Output

When running successfully, you should see:

```
🚀 Launching Gazebo warehouse with visualization...

Starting components:
  1. Gazebo warehouse simulation
  2. ROS2-Gazebo bridge (topic remapping)
  3. Inspector node (Claude AI analysis)
  4. RViz visualization
  5. Demo script (autonomous inspection)

[Gazebo opens with warehouse scene]
[RViz opens with 3D visualization]

[INFO] [gazebo_demo]: Gazebo Demo Node initialized
[INFO] [gazebo_demo]: GAZEBO WAREHOUSE INSPECTION DEMO
[INFO] [gazebo_demo]: Starting demo at 2026-04-03T...
[INFO] [gazebo_demo]: Moving to Shelf 1 (2.00, -1.00)
...
[INFO] [gazebo_demo]: DEMO COMPLETE
```

Reports saved to: `gazebo_demo_reports/`

---

## Getting Help

1. **Full documentation:** `robot_inspector/docs/GAZEBO_SETUP.md`
2. **ROS2 guide:** `robot_inspector/README_ROS2.md`
3. **Project overview:** `robot_inspector/README.md`
4. **GitHub:** https://github.com/z-manoj/smart-robot-inspector

