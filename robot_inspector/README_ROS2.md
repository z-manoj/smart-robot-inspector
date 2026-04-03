# ROS2 Integration Guide - Smart Robot Inspector

Complete guide for using the Smart Robot Inspector with ROS2.

## Overview

The Robot Inspector ROS2 node provides real-time defect detection and analysis for robot inspection systems. It subscribes to camera feeds and publishes analysis results with severity classification.

## Architecture

```
ROS2 Topics
    ↓
Gazebo Camera / Real Robot Camera
    ↓
/camera/image_raw (sensor_msgs/Image)
    ↓
InspectorNode
  ├─ Convert image with cv_bridge
  ├─ Analyze with Claude AI
  ├─ Classify by severity
  └─ Generate reports
    ↓
/robot_inspector/analysis (std_msgs/String - JSON)
    ↓
Downstream Processing
  (Logging, visualization, decision-making)
```

## Installation

### Prerequisites

- Ubuntu 20.04+ or 22.04
- ROS2 Humble, Iron, or Jazzy
- Python 3.8+
- AWS Account with Bedrock access

### 1. Install ROS2

Follow the official [ROS2 Installation Guide](https://docs.ros.org/en/humble/Installation.html)

```bash
# For Ubuntu 22.04 (Humble)
sudo apt update
sudo apt install ros-humble-desktop
source /opt/ros/humble/setup.bash
```

### 2. Create ROS2 Workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

### 3. Clone Repository

```bash
git clone https://github.com/z-manoj/smart-robot-inspector.git
cd smart-robot-inspector
git checkout phase2-ros2-integration
```

### 4. Install Dependencies

```bash
# Core dependencies
cd ~/ros2_ws
pip install -r src/smart-robot-inspector/requirements.txt

# ROS2 dependencies
pip install -r src/smart-robot-inspector/requirements-ros2.txt

# System packages
sudo apt install -y python3-rosdep ros-humble-image-transport
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

### 5. Build Package

```bash
cd ~/ros2_ws
colcon build --packages-select robot_inspector
source install/setup.bash
```

### 6. Configure AWS

```bash
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output format (json)
```

## Running the Node

### Method 1: Using Launch File

```bash
# Default configuration
ros2 launch robot_inspector inspector.launch.py

# With custom parameters
ros2 launch robot_inspector inspector.launch.py \
  bedrock_region:=us-west-2 \
  inspection_interval_ms:=2000 \
  confidence_threshold:=0.80
```

### Method 2: Direct Node Launch

```bash
ros2 run robot_inspector inspector_node
```

### Method 3: Standalone Script (Development)

```bash
python3 scripts/run_ros_node.py --region us-east-1 --interval 1000
```

## Topics and Messages

### Subscribed Topics

**Topic**: `/camera/image_raw`
- **Type**: `sensor_msgs/Image`
- **Description**: Camera feed from Gazebo or real robot
- **Frequency**: Typically 10-30 Hz

### Published Topics

**Topic**: `/robot_inspector/analysis`
- **Type**: `std_msgs/String` (JSON content)
- **Description**: Analysis results for each image
- **Frequency**: Based on `inspection_interval_ms`

**Message Format**:
```json
{
    "timestamp": "2026-04-03T18:30:00.123456",
    "inspection_id": "ros2_20260403_183000_001",
    "waypoint": 1,
    "analysis": {
        "objects": [
            {"name": "Shelf", "count": 3, "description": "..."}
        ],
        "detected_issues": [
            {
                "issue": "Damage detected",
                "severity": "HIGH",
                "location": "Shelf 2",
                "recommendation": "Repair shelf"
            }
        ],
        "scene_description": "...",
        "confidence_score": 0.92,
        "overall_status": "FAIL"
    }
}
```

## Parameters

Set parameters at launch or runtime:

### Launch-time Parameters

```bash
ros2 launch robot_inspector inspector.launch.py \
  bedrock_region:=us-east-1 \
  model_id:=us.anthropic.claude-opus-4-6-v1 \
  image_topic:=/camera/image_raw \
  analysis_topic:=/robot_inspector/analysis \
  report_output_dir:=./reports \
  inspection_interval_ms:=1000 \
  max_queue_size:=10 \
  confidence_threshold:=0.70 \
  enable_visualization:=true
```

### Runtime Parameter Changes

```bash
# View current parameters
ros2 param list /robot_inspector
ros2 param get /robot_inspector inspection_interval_ms

# Change parameters
ros2 param set /robot_inspector confidence_threshold 0.80
ros2 param set /robot_inspector inspection_interval_ms 2000
```

### Parameter Descriptions

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `bedrock_region` | string | us-east-1 | AWS Bedrock region |
| `model_id` | string | us.anthropic.claude-opus-4-6-v1 | Claude model ID |
| `image_topic` | string | /camera/image_raw | Input camera topic |
| `analysis_topic` | string | /robot_inspector/analysis | Output analysis topic |
| `report_output_dir` | string | ./reports | Report output directory |
| `inspection_interval_ms` | integer | 1000 | Milliseconds between inspections |
| `max_queue_size` | integer | 10 | Maximum buffered images |
| `confidence_threshold` | double | 0.70 | Minimum confidence to publish |
| `enable_visualization` | bool | true | Generate reports |

## Monitoring the Node

### View Live Analysis

```bash
# In a new terminal
ros2 topic echo /robot_inspector/analysis

# With formatted output
ros2 topic echo /robot_inspector/analysis --truncate-length 200
```

### Monitor Node Status

```bash
# Node info
ros2 node info /robot_inspector

# Topic info
ros2 topic info /robot_inspector/analysis
```

### View Node Logs

```bash
# Real-time logs
ros2 run rqt_console rqt_console

# Or terminal output (running with output='screen' in launch)
```

## Testing with Gazebo

### Prerequisites

```bash
sudo apt install ros-humble-gazebo-* ros-humble-gazebo-ros-pkgs
```

### Launch Gazebo with Camera

```bash
# In one terminal
ros2 launch gazebo_ros gazebo.launch.py

# In another terminal, add robot with camera
# (Gazebo models available in standard packages)
```

### Publish Test Images

```bash
# Using image_publisher
ros2 run image_publisher image_publisher node \
  --ros-args \
  -r image_raw:=/camera/image_raw \
  -p image_path:=/path/to/image.png
```

### Monitor Results

```bash
ros2 topic echo /robot_inspector/analysis
```

## Configuration Examples

### Example 1: Real-time Processing

```yaml
# config/inspector_config.yaml
robot_inspector:
  inspection_interval_ms: 100      # 10 Hz
  max_queue_size: 5
  confidence_threshold: 0.50       # Lower threshold for real-time
  bedrock_region: us-east-1
```

### Example 2: High-Quality Analysis

```yaml
robot_inspector:
  inspection_interval_ms: 3000     # ~0.3 Hz
  max_queue_size: 20
  confidence_threshold: 0.85       # Higher threshold
  bedrock_region: us-east-1
```

### Example 3: Multi-Region Deployment

```yaml
# For US-East region
robot_inspector:
  bedrock_region: us-east-1
  
# For US-West region
robot_inspector:
  bedrock_region: us-west-2
```

## Troubleshooting

### Node Fails to Start

```bash
# Check ROS2 environment
echo $ROS_DOMAIN_ID
source /opt/ros/humble/setup.bash

# Verify dependencies
ros2 pkg list | grep robot_inspector

# Try verbose startup
ros2 run robot_inspector inspector_node --ros-args --log-level DEBUG
```

### AWS Bedrock Errors

```bash
# Verify credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1 | grep Claude

# Reconfigure if needed
aws configure
```

### No Images Received

```bash
# Check camera topic
ros2 topic list | grep camera
ros2 topic info /camera/image_raw

# Monitor with rqt_image_view
ros2 run rqt_image_view rqt_image_view
```

### Low Confidence Scores

Adjust the confidence threshold:
```bash
ros2 param set /robot_inspector confidence_threshold 0.60
```

Or check that camera images are clear and well-lit.

## Advanced Usage

### Custom Topic Names

```bash
ros2 launch robot_inspector inspector.launch.py \
  image_topic:=/my_robot/camera/image \
  analysis_topic:=/my_robot/quality_check/results
```

### Batch Processing

Use the Python API directly:

```python
from robot_inspector import CameraProcessor, ReportGenerator

processor = CameraProcessor()
report_gen = ReportGenerator()

# Process multiple images
for image_path in image_paths:
    with open(image_path, 'rb') as f:
        analysis = processor.process_image_with_claude(f.read())
    # Publish to ROS2 or process further
```

### Performance Tuning

- Increase `inspection_interval_ms` for slower processing
- Decrease `max_queue_size` to reduce memory usage
- Adjust `confidence_threshold` to filter low-quality results
- Use smaller image sizes to reduce API costs

## Integration with Gazebo (Phase 3)

The node is designed to work seamlessly with Gazebo:

1. Gazebo publishes camera images to `/camera/image_raw`
2. Inspector node subscribes and analyzes
3. Results published for logging and visualization

See Phase 3 documentation for Gazebo integration.

## Performance Metrics

- **Image Processing Time**: 2-5 seconds per image (Bedrock API latency)
- **Queue Processing**: Non-blocking, async
- **Memory Usage**: ~200-300 MB base + image buffers
- **CPU Usage**: Low (mostly waiting for API)

## Security Considerations

- AWS credentials should be configured securely (IAM roles recommended)
- ROS2 domain ID should be restricted if running on shared networks
- Use appropriate ROS2 Security Extensions in production
- Restrict access to analysis results if sensitive

## Contributing

Found an issue? Have improvements?

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes
4. Push and create a Pull Request

## Support

- **Documentation**: See README.md and EXAMPLES.md
- **Issues**: GitHub repository issues
- **ROS2 Help**: https://docs.ros.org/
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/

---

**Version**: 0.2.0 (Phase 2 - ROS2 Integration)  
**Status**: ✅ Complete and Tested  
**Last Updated**: April 2026
