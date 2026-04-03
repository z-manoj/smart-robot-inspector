# Quick Start - Smart Robot Inspector

Clone and run the complete defect detection system in 5 minutes.

## Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS CLI configured: `aws configure`

## Setup (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/z-manoj/smart-robot-inspector.git
cd smart-robot-inspector
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AWS (if not already done)
```bash
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output format (json)
```

### 5. Run Demo
```bash
cd robot_inspector
python3 demo_standalone.py
```

### 6. View Reports
```bash
cat reports/inspection_demo_2026_04_03_001.md
```

## What You Get

✅ **Warehouse Inspection Analysis** - 3 shelves analyzed, damage detected
✅ **Defective Part Detection** - Structural cracks identified with severity
✅ **5 Issues Found** - 2 CRITICAL, 1 HIGH, 1 MEDIUM, 1 LOW
✅ **Reports Generated** - JSON, Markdown, and HTML formats

## Architecture

```
Sampled Images
    ↓
AWS Bedrock + Claude AI
    ↓
Defect Detection & Classification
    ↓
JSON/Markdown/HTML Reports
```

## Next Steps

- 📚 Read: `GETTING_STARTED.md` - 5-minute overview
- 📖 Read: `robot_inspector/README.md` - Full documentation
- 💡 Learn: `robot_inspector/EXAMPLES.md` - 7+ code examples
- 🚀 Phase 2: ROS2 Integration (coming soon)

## Project Structure

```
smart-robot-inspector/
├── robot_inspector/              # Main package
│   ├── robot_inspector/
│   │   ├── camera_processor.py  # AWS Bedrock + Claude
│   │   ├── report_generator.py  # Report generation
│   │   └── utils.py             # Image utilities
│   ├── demo_standalone.py       # Demo application
│   ├── README.md                # Full documentation
│   ├── EXAMPLES.md              # Code examples
│   └── SETUP_GUIDE.md           # Detailed setup
├── requirements.txt             # Python dependencies
├── requirements-ros2.txt        # ROS2 dependencies (Phase 2)
└── README_FIRST.txt            # Project overview
```

## Troubleshooting

### AWS Credentials Error
```bash
aws configure  # Re-enter your credentials
aws sts get-caller-identity  # Verify setup
```

### Python Version Error
```bash
python3 --version  # Must be 3.8+
# If needed, install: python3.11 or later
```

### Installation Issues
```bash
pip install --upgrade pip
pip install -r requirements.txt  # Try again
```

## Features

✨ **Vision-based Analysis** - Claude AI understands industrial scenes
✨ **Severity Classification** - CRITICAL/HIGH/MEDIUM/LOW
✨ **Multi-format Reports** - JSON, Markdown, HTML
✨ **Automated Recommendations** - Actionable insights
✨ **Before/After Comparison** - Track changes over time
✨ **Batch Processing** - Analyze multiple images

## GitHub

Repository: https://github.com/z-manoj/smart-robot-inspector

## License

MIT License

---

**Ready?** Just run: `python3 robot_inspector/demo_standalone.py`

For full documentation, see `GETTING_STARTED.md` or `robot_inspector/README.md`
