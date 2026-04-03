# Setup Guide - Smart Robot Inspector

Complete setup instructions for the Smart Robot Inspector system.

## Prerequisites

- **Python**: 3.8 or higher
- **AWS Account**: With Bedrock access enabled
- **Operating System**: Linux, macOS, or Windows

## Step 1: Clone/Download Repository

```bash
cd /path/to/your/workspace
git clone <repo-url>  # or download ZIP
cd robot_inspector
```

## Step 2: Python Environment Setup

### Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Verify Installation

```bash
python3 -c "import robot_inspector; print(robot_inspector.__version__)"
```

## Step 3: AWS Configuration

### Setup AWS Credentials

```bash
# Configure AWS
aws configure

# You'll be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region
# - Default output format (json)
```

**Region recommendation**: Use a region with Bedrock Claude models:
- `us-east-1` (US East)
- `us-west-2` (US West)
- `eu-west-1` (EU Ireland)

### Verify AWS Setup

```bash
# Check credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### Enable Claude Models

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Click "Model access" in left sidebar
3. Search for "Claude"
4. Click "Request access" for desired Claude model
5. Wait for activation (usually instant)

### Verify Model Access

```bash
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query 'modelSummaries[?contains(modelName, `Claude`)].{Name:modelName,Id:modelId}'
```

## Step 4: Verify Installation

### Run Demo

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
✓ Analysis 1 complete. Status: ...

[Step 3] Generating inspection report...
Exporting reports...
✓ JSON report: reports/inspection_demo_2026_04_03_001.json
✓ Markdown report: reports/inspection_demo_2026_04_03_001.md
✓ HTML report: reports/inspection_demo_2026_04_03_001.html

✓ Demo completed successfully!
Reports saved to: reports/
```

### Check Generated Reports

```bash
ls -la reports/
```

You should see:
- `inspection_demo_2026_04_03_001.json`
- `inspection_demo_2026_04_03_001.md`
- `inspection_demo_2026_04_03_001.html`
- `sample_warehouse.png`
- `sample_defect.png`

## Step 5: Test Custom Image

```python
from robot_inspector import CameraProcessor
import json

# Initialize
processor = CameraProcessor(region_name="us-east-1")

# Load your image
with open("your_image.png", "rb") as f:
    image_bytes = f.read()

# Analyze
analysis = processor.process_image_with_claude(
    image_bytes,
    context="Custom inspection"
)

# Display results
print(json.dumps(analysis, indent=2))
```

## Step 6: Install Package (Optional)

For development:

```bash
# Install in editable mode
pip install -e .

# Now you can import from anywhere
python3 -c "from robot_inspector import CameraProcessor; print('OK')"
```

## Troubleshooting

### Issue: AWS Credentials Not Found

**Error**:
```
NoCredentialsError: Unable to locate credentials
```

**Solution**:
```bash
# Configure credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### Issue: Model Not Available

**Error**:
```
ResourceNotFoundException: This model version has reached the end of its life
```

**Solution**:
```bash
# Check available models
aws bedrock list-foundation-models --region us-east-1

# Update model_id in code
processor = CameraProcessor(
    model_id="anthropic.claude-opus-4-1-20250805-v1:0"
)
```

### Issue: Bedrock Access Not Granted

**Error**:
```
AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel
```

**Solution**:
1. Go to AWS Bedrock console
2. Click "Model access"
3. Request access to Claude model
4. Wait for activation email
5. Retry after activation

### Issue: Wrong AWS Region

**Error**:
```
ValidationException: Model ID not available in this region
```

**Solution**:
```bash
# Check available regions
aws ec2 describe-regions

# Update region
processor = CameraProcessor(region_name="us-west-2")
```

### Issue: Python Version Mismatch

**Error**:
```
error: Microsoft Visual C++ 14.0 is required
```

**Solution**:
- Install Python 3.8+
- Use `python3` instead of `python`

## Docker Setup (Optional)

For containerized deployment:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set AWS credentials as environment variables
ENV AWS_DEFAULT_REGION=us-east-1

ENTRYPOINT ["python3", "demo_standalone.py"]
```

Build and run:
```bash
docker build -t robot-inspector .
docker run \
  -e AWS_ACCESS_KEY_ID="your-key" \
  -e AWS_SECRET_ACCESS_KEY="your-secret" \
  -v $(pwd)/reports:/app/reports \
  robot-inspector
```

## Development Setup

### Install Dev Dependencies

```bash
pip install pytest black pylint mypy
```

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black robot_inspector/
```

### Type Checking

```bash
mypy robot_inspector/
```

## System Requirements

### Minimum

- Python 3.8+
- 2 GB RAM
- 100 MB disk space
- Internet connection for AWS Bedrock API

### Recommended

- Python 3.11+
- 4 GB RAM
- 500 MB disk space
- SSD for faster image I/O

## Environment Variables

Optional configuration via environment variables:

```bash
# AWS Configuration
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Application Configuration
export ROBOT_INSPECTOR_BEDROCK_REGION="us-east-1"
export ROBOT_INSPECTOR_MODEL_ID="anthropic.claude-opus-4-1-20250805-v1:0"
export ROBOT_INSPECTOR_OUTPUT_DIR="./reports"
```

Use in code:

```python
import os
from robot_inspector import CameraProcessor

region = os.getenv("ROBOT_INSPECTOR_BEDROCK_REGION", "us-east-1")
model_id = os.getenv("ROBOT_INSPECTOR_MODEL_ID", "anthropic.claude-opus-4-1-20250805-v1:0")

processor = CameraProcessor(
    region_name=region,
    model_id=model_id
)
```

## Next Steps

1. **Read Documentation**: See [README.md](README.md)
2. **Explore Examples**: See [EXAMPLES.md](EXAMPLES.md)
3. **Try Custom Images**: Process your own images
4. **Integrate with ROS2**: (Future)
5. **Deploy to Production**: Container or cloud setup

## Support

- **AWS Bedrock Docs**: https://docs.aws.amazon.com/bedrock/
- **Claude API Docs**: https://docs.anthropic.com/
- **Python Docs**: https://docs.python.org/3/
- **GitHub Issues**: Submit bugs and feature requests

---

**Last Updated**: April 2026
