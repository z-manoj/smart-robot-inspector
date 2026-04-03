# 🤖 Smart Robot Inspector

An intelligent robot inspection system that combines **ROS2**, **Gazebo simulation**, and **Claude AI via AWS Bedrock** to analyze industrial environments and generate comprehensive inspection reports.

## Overview

Smart Robot Inspector is a Python-based system that:
- 📷 Captures images from simulated robot cameras (Gazebo)
- 🧠 Analyzes images using Claude 3's vision capabilities via AWS Bedrock
- 🔍 Detects defects and anomalies with severity scoring
- 📊 Generates structured inspection reports (JSON, Markdown, HTML)
- 🗺️ Compares multi-point inspections to track changes
- 📈 Provides actionable recommendations

## Features

### Core Capabilities
- **Vision-Based Inspection**: Claude analyzes camera feeds for defects, objects, and anomalies
- **Severity Scoring**: Classifies issues as CRITICAL, HIGH, MEDIUM, or LOW
- **Multi-Point Inspection**: Track robot path and aggregate findings across waypoints
- **Before/After Comparison**: Detect changes between inspection rounds
- **Structured Reports**: JSON, Markdown, and HTML output formats
- **AWS Bedrock Integration**: Use latest Claude models without managing API keys

### Report Features
- Executive summary with overall status (PASS/FAIL/REVIEW_REQUIRED)
- Issue breakdown by severity
- Robot navigation path tracking
- Confidence scores for each analysis
- Actionable recommendations
- Critical finding highlights

## Quick Start

### Prerequisites

```bash
# Python 3.8+
python3 --version

# AWS Account with Bedrock access
aws configure
```

### Installation

```bash
cd robot_inspector

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Demo

```bash
python3 demo_standalone.py
```

This creates:
- Sample warehouse and part images
- Analyzes with Claude via Bedrock (requires AWS credentials)
- Generates inspection reports in `reports/` directory

### Generated Outputs

```
reports/
├── inspection_demo_2026_04_03_001.json    # Machine-readable report
├── inspection_demo_2026_04_03_001.md      # Markdown report
├── inspection_demo_2026_04_03_001.html    # HTML report
├── sample_warehouse.png                   # Sample image 1
└── sample_defect.png                      # Sample image 2
```

## Usage

### 1. Image Processing & Analysis

```python
from robot_inspector import CameraProcessor

# Initialize processor
processor = CameraProcessor(region_name="us-east-1")

# Load image (PNG/JPEG bytes)
with open("image.png", "rb") as f:
    image_bytes = f.read()

# Analyze with Claude
analysis = processor.process_image_with_claude(
    image_bytes,
    context="Factory inspection scene",
    include_severity=True
)

print(f"Status: {analysis['overall_status']}")
print(f"Issues: {analysis['detected_issues']}")
print(f"Confidence: {analysis['confidence_score']}")
```

### 2. Report Generation

```python
from robot_inspector import ReportGenerator

report_gen = ReportGenerator(output_dir="./reports")

# Create report
report = report_gen.create_inspection_report(
    inspection_id="INS_2026_04_03_001",
    robot_path=[
        {"x": 0, "y": 0},
        {"x": 1.5, "y": 2.0},
        {"x": 3.0, "y": 2.0},
    ],
    inspection_points=[
        {
            "waypoint_id": 1,
            "position": {"x": 1.5, "y": 2.0},
            "image_analysis": analysis_1,
        },
        {
            "waypoint_id": 2,
            "position": {"x": 3.0, "y": 2.0},
            "image_analysis": analysis_2,
        }
    ]
)

# Export in multiple formats
report_gen.export_json(report)
report_gen.export_markdown(report)
report_gen.export_html(report)
```

### 3. Before/After Comparison

```python
# Compare two inspections
comparison = processor.compare_analyses(analysis_1, analysis_2)

print("Objects changed:", comparison['objects_changed'])
print("New issues:", comparison['new_issues'])
print("Resolved issues:", comparison['resolved_issues'])
```

### 4. Image Utilities

```python
from robot_inspector import (
    resize_image,
    convert_cv_to_png,
    add_text_overlay,
    add_bounding_box,
    save_image,
    load_image
)

# Resize for API efficiency
resized = resize_image(image_bytes, max_width=1024, max_height=768)

# Add annotations
annotated = add_text_overlay(image_bytes, "Inspection Point 1")
annotated = add_bounding_box(annotated, (100, 100, 200, 200), "DEFECT")

# Save/load
save_image(annotated, "output.png")
loaded = load_image("output.png")
```

## Architecture

```
┌─────────────────┐
│  Gazebo Sim     │
│  (Camera Feed)  │
└────────┬────────┘
         │
    ┌────▼─────────┐
    │  ROS2 Node   │
    │  (Future)    │
    └────┬─────────┘
         │
    ┌────▼──────────────────┐
    │ CameraProcessor       │
    │ (Vision Analysis)     │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │ AWS Bedrock + Claude  │
    │ (Image Understanding) │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │ ReportGenerator       │
    │ (JSON/MD/HTML)        │
    └───────────────────────┘
```

## Components

### `CameraProcessor`
Handles image processing and Claude API integration via Bedrock.
- `process_image_with_claude()` - Analyze image with severity scoring
- `compare_analyses()` - Compare two inspection results
- `get_analysis_history()` - Retrieve stored analyses

### `ReportGenerator`
Creates structured inspection reports.
- `create_inspection_report()` - Build complete report
- `export_json()` - Save machine-readable report
- `export_markdown()` - Save human-readable summary
- `export_html()` - Save interactive HTML report

### `Utils`
Image processing and file utilities.
- `resize_image()` - Optimize for API usage
- `convert_cv_to_png()` - OpenCV to PNG conversion
- `add_text_overlay()` - Annotate images
- `add_bounding_box()` - Draw detection boxes

## AWS Bedrock Configuration

### Setup

1. **Configure AWS credentials**:
```bash
aws configure
# Enter Access Key, Secret Key, Region, Output format
```

2. **Enable Claude models in Bedrock**:
   - Go to AWS Bedrock console
   - Request access to Claude model
   - Wait for activation (usually instant)

3. **Check available models**:
```bash
aws bedrock list-foundation-models
```

### Model IDs

Update the `model_id` parameter in `CameraProcessor`:

```python
# Latest Claude models
processor = CameraProcessor(
    model_id="anthropic.claude-opus-4-1-20250805-v1:0"  # Latest
)
```

Check Bedrock documentation for current model IDs.

## Report Schema

### JSON Report Structure

```json
{
    "inspection_id": "demo_2026_04_03_001",
    "timestamp": {
        "start": "2026-04-03T18:13:17.930837",
        "end": "2026-04-03T18:13:17.930861",
        "generated": "2026-04-03T18:13:17.930868"
    },
    "summary": {
        "total_inspection_points": 2,
        "waypoints_visited": 4,
        "overall_status": "PASS",
        "total_issues": 0,
        "issues_by_severity": {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
    },
    "robot_path": [...],
    "inspection_points": [...],
    "critical_findings": [],
    "recommendations": ["Inspection passed all checks - continue normal operations"]
}
```

## Phase 3: Gazebo Simulation

Smart Robot Inspector now includes **full Gazebo simulation** with autonomous warehouse inspection.

### Quick Start

```bash
# Launch complete system with visualization and automated demo
ros2 launch robot_inspector gazebo_warehouse_with_viz.launch.py

# This runs:
# - Gazebo warehouse with 3 shelves
# - Mobile robot with differential drive
# - Camera publishing at 30Hz
# - Inspector node analyzing in real-time
# - RViz visualization
# - Automated demo visiting all waypoints
```

### What Happens

1. Robot navigates to 3 shelves (Shelf 1, Shelf 2 with damage, Shelf 3)
2. Captures images at each location
3. Claude analyzes images for defects via Bedrock
4. Generates comprehensive JSON + Markdown reports
5. Reports saved to `gazebo_demo_reports/`

### Key Files

- **worlds/warehouse.world** - Gazebo world with shelves and items
- **models/mobile_robot/model.sdf** - 2-wheel differential drive robot
- **scripts/run_gazebo_demo.py** - Orchestration and navigation
- **config/gazebo_params.yaml** - Simulation parameters
- **launch/gazebo_warehouse_with_viz.launch.py** - Complete system launch

### Full Documentation

See [docs/GAZEBO_SETUP.md](docs/GAZEBO_SETUP.md) for:
- Detailed setup instructions
- Launch argument reference
- System components explained
- Troubleshooting guide
- Performance tuning
- Custom world creation

## Future Enhancements

- [ ] Video recording of inspection playback
- [ ] Database integration for inspection history
- [ ] Web dashboard for report viewing
- [ ] Integration with MQTT for IoT systems
- [ ] Defect tracking and trending analysis
- [ ] Multiple robot swarm coordination
- [ ] Nav2 autonomous path planning integration

## File Structure

```
robot_inspector/
├── robot_inspector/              # Main package
│   ├── __init__.py
│   ├── camera_processor.py       # Claude + Bedrock integration
│   ├── report_generator.py       # Report generation
│   └── utils.py                  # Image utilities
├── demo_standalone.py            # Standalone demo
├── setup.py                      # Package setup
├── requirements.txt              # Dependencies
├── reports/                      # Generated reports
├── launch/                       # ROS2 launch files (future)
├── worlds/                       # Gazebo worlds (future)
├── models/                       # Robot/object models (future)
├── scripts/                      # Helper scripts (future)
└── config/                       # Configuration files (future)
```

## Troubleshooting

### AWS Credentials Not Found
```bash
# Configure AWS
aws configure

# Verify credentials
aws sts get-caller-identity
```

### Model Not Available
```bash
# Check available models
aws bedrock list-foundation-models --region us-east-1

# Update model_id in code
processor = CameraProcessor(model_id="<available_model_id>")
```

### Image Analysis Fails
- Check image format (PNG/JPEG)
- Verify Bedrock access in AWS console
- Check region has Claude models enabled
- Verify IAM permissions for bedrock:InvokeModel

### Report Generation Issues
- Ensure output directory exists or is writable
- Check disk space for large analysis batches
- Verify JSON is valid (use `json.dumps()` for debugging)

## Development

```bash
# Install in development mode
pip install -e .

# Run tests (future)
pytest

# Code formatting
black robot_inspector/

# Linting
pylint robot_inspector/
```

## Contributing

Contributions welcome! Areas for development:
- ROS2 node implementation
- Gazebo world creation
- Additional report formats
- Performance optimizations
- Automated testing

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review AWS Bedrock documentation
3. Check Claude API documentation
4. Open an issue on GitHub

---

**Created**: April 2026  
**Status**: Active Development  
**Version**: 0.3.0  

### Phase Progression
- **Phase 1** ✅ - Core analysis system (CameraProcessor, ReportGenerator)
- **Phase 2** ✅ - ROS2 integration (InspectorNode, message conversion)
- **Phase 3** ✅ - Gazebo simulation (warehouse world, mobile robot, demo)
