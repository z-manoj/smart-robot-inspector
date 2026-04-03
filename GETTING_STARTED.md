# 🚀 Getting Started - Smart Robot Inspector

**5-minute quickstart to get the Smart Robot Inspector running!**

## ⚡ TL;DR (30 seconds)

```bash
cd robot_inspector
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
aws configure  # Use us-east-1 region
python3 demo_standalone.py
```

Then open: `robot_inspector/reports/inspection_demo_2026_04_03_001.md`

## 📋 Prerequisites Check

Before starting, verify you have:

- ✅ Python 3.8+ installed: `python3 --version`
- ✅ AWS account with Bedrock access
- ✅ AWS credentials configured or ready to set up
- ✅ ~500MB disk space available
- ✅ Internet connection

## 🎯 Step-by-Step Setup (5 minutes)

### Step 1: Navigate to Project (30 seconds)

```bash
cd /home/manojk/physical_ai_ryzen/robot_inspector
```

### Step 2: Create Python Environment (1 minute)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies (2 minutes)

```bash
# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### Step 4: Configure AWS (1 minute)

```bash
aws configure
```

When prompted, enter:
- **AWS Access Key ID**: Your access key
- **AWS Secret Access Key**: Your secret key
- **Default region**: `us-east-1` (or your region with Claude)
- **Default output format**: `json`

### Step 5: Run the Demo (1 minute)

```bash
python3 demo_standalone.py
```

Expected output:
```
============================================================
Smart Robot Inspector - Standalone Demo
============================================================

[Step 1] Creating sample inspection images...
✓ Sample images saved to reports/

[Step 2] Analyzing images with Claude via AWS Bedrock...
Analyzing warehouse image...
✓ Analysis 1 complete...

[Step 3] Generating inspection report...
✓ JSON report: reports/inspection_demo_2026_04_03_001.json
✓ Markdown report: reports/inspection_demo_2026_04_03_001.md
✓ HTML report: reports/inspection_demo_2026_04_03_001.html

✓ Demo completed successfully!
```

## 📊 View Your Reports

### Option 1: View Markdown Report (Human-readable)

```bash
cat reports/inspection_demo_2026_04_03_001.md
```

### Option 2: View JSON Report (Machine-readable)

```bash
cat reports/inspection_demo_2026_04_03_001.json
```

### Option 3: Open HTML Report (Interactive)

```bash
# macOS
open reports/inspection_demo_2026_04_03_001.html

# Linux
xdg-open reports/inspection_demo_2026_04_03_001.html

# Windows
start reports/inspection_demo_2026_04_03_001.html
```

### Option 4: List All Generated Files

```bash
ls -lah reports/
```

## 🔍 What Just Happened?

The demo created:

1. **Sample Images**
   - `sample_warehouse.png` - Warehouse inventory scene
   - `sample_defect.png` - Part with defect

2. **Analysis with Claude**
   - Used Claude via AWS Bedrock
   - Detected objects (shelves, items)
   - Identified defects with severity
   - Generated confidence scores

3. **Reports in 3 Formats**
   - JSON for machines
   - Markdown for reading
   - HTML for viewing

## ✅ Troubleshooting

### ❌ AWS Credentials Error

**Error**:
```
NoCredentialsError: Unable to locate credentials
```

**Fix**:
```bash
aws configure
# Enter your AWS access key and secret key
```

### ❌ Model Not Available

**Error**:
```
ResourceNotFoundException: This model version has reached the end of its life
```

**Fix**:
Check available models and update code:
```bash
aws bedrock list-foundation-models --region us-east-1
```

Then edit and update the model ID in code.

### ❌ Python Version Error

**Error**:
```
Error: Python 3.8+ required
```

**Fix**:
```bash
# Check version
python3 --version

# Use python3.11 or later
python3.11 -m venv venv
```

### ❌ AWS Bedrock Access Not Granted

**Error**:
```
AccessDeniedException: User is not authorized
```

**Fix**:
1. Go to AWS Bedrock console
2. Click "Model access"
3. Request access to Claude
4. Wait for activation (instant)
5. Retry

## 🎓 Next Steps

### 1. Read Documentation (10 minutes)

```bash
# Main guide
cat README.md

# Setup details
cat SETUP_GUIDE.md

# Usage examples
cat EXAMPLES.md
```

### 2. Try Example 1: Simple Analysis (5 minutes)

```python
from robot_inspector import CameraProcessor

processor = CameraProcessor()

# Load image
with open("reports/sample_warehouse.png", "rb") as f:
    image_bytes = f.read()

# Analyze
analysis = processor.process_image_with_claude(
    image_bytes,
    context="Warehouse inspection"
)

print(f"Status: {analysis['overall_status']}")
print(f"Issues: {len(analysis['detected_issues'])}")
```

Run it:
```bash
python3 << 'EOF'
from robot_inspector import CameraProcessor
processor = CameraProcessor()
with open("reports/sample_warehouse.png", "rb") as f:
    analysis = processor.process_image_with_claude(f.read())
print("Status:", analysis['overall_status'])
EOF
```

### 3. Try Example 2: Analyze Your Own Image (5 minutes)

```python
from robot_inspector import CameraProcessor, ReportGenerator

processor = CameraProcessor()
report_gen = ReportGenerator()

# Analyze your image
with open("your_image.png", "rb") as f:
    analysis = processor.process_image_with_claude(
        f.read(),
        context="Custom inspection"
    )

# Generate report
report = report_gen.create_inspection_report(
    inspection_id="CUSTOM_001",
    robot_path=[{"x": 0, "y": 0}],
    inspection_points=[{
        "waypoint_id": 1,
        "position": {"x": 0, "y": 0},
        "image_analysis": analysis
    }]
)

report_gen.export_json(report)
print("✓ Report generated!")
```

### 4. Read Full Examples (15 minutes)

See [EXAMPLES.md](EXAMPLES.md) for:
- Multi-point inspections
- Before/after comparisons
- Batch processing
- Custom workflows
- QC automation
- ROS2 integration (preview)

## 📚 Documentation Map

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **GETTING_STARTED.md** | 5-min quickstart (you are here) | 5 min |
| [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) | Project overview & architecture | 10 min |
| [README.md](README.md) | Full feature documentation | 15 min |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Detailed setup & troubleshooting | 10 min |
| [EXAMPLES.md](EXAMPLES.md) | Practical code examples | 20 min |

**Total**: ~60 minutes to fully understand the system

## 🎯 What You Can Do Now

✅ Analyze images with Claude AI  
✅ Detect defects automatically  
✅ Generate inspection reports  
✅ Export JSON/Markdown/HTML  
✅ Compare before/after states  
✅ Process multiple images  
✅ Create custom workflows  

## 🚀 Ready for Next Phase?

After mastering the basics, the next phase includes:
- ROS2 node integration
- Gazebo simulation
- Real robot communication
- Live visualization
- Video recording
- Web dashboard

## 💡 Pro Tips

1. **Use AWS CLI** to check your setup:
   ```bash
   aws sts get-caller-identity
   aws bedrock list-foundation-models
   ```

2. **Create Alias** for quick startup:
   ```bash
   alias ri='cd /home/manojk/physical_ai_ryzen/robot_inspector && source venv/bin/activate'
   ```

3. **Keep Reports Organized**:
   ```bash
   mkdir -p reports/2026_04_03
   mv reports/*.json reports/2026_04_03/
   ```

4. **Test with Real Images**:
   - Use `camera_processor.resize_image()` for large images
   - Reduces API costs

## 📞 Need Help?

1. **Check Troubleshooting**: [SETUP_GUIDE.md Troubleshooting](SETUP_GUIDE.md#troubleshooting)
2. **Read Examples**: [EXAMPLES.md](EXAMPLES.md)
3. **Check AWS Docs**: https://docs.aws.amazon.com/bedrock/
4. **Check Claude Docs**: https://docs.anthropic.com/

## 🎉 Success Indicators

You're all set if you see:

✅ `demo_standalone.py` completes without errors  
✅ Reports generated in `reports/` directory  
✅ `inspection_demo_2026_04_03_001.md` has content  
✅ JSON report contains analysis results  
✅ HTML report opens in browser  
✅ No AWS credentials errors  

---

**You're Ready!** 🎊

Next: Read [README.md](README.md) for full documentation.

Questions? Check [EXAMPLES.md](EXAMPLES.md) or [SETUP_GUIDE.md](SETUP_GUIDE.md).

Happy Inspecting! 🤖📊
