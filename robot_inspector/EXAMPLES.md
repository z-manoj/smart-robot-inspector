# Smart Robot Inspector - Usage Examples

## Example 1: Simple Image Analysis

Analyze a single image and get defect detection results.

```python
from robot_inspector import CameraProcessor
import json

# Initialize processor
processor = CameraProcessor(region_name="us-east-1")

# Load image
with open("warehouse_scan.png", "rb") as f:
    image_bytes = f.read()

# Analyze
analysis = processor.process_image_with_claude(
    image_bytes,
    context="Warehouse inventory inspection",
    include_severity=True
)

# Display results
print(f"Overall Status: {analysis['overall_status']}")
print(f"\nDetected Objects:")
for obj in analysis['objects']:
    print(f"  - {obj['name']}: {obj['count']} units")

print(f"\nIssues Found:")
for issue in analysis['detected_issues']:
    print(f"  - [{issue['severity']}] {issue['issue']}")
    print(f"    Location: {issue['location']}")
    print(f"    Recommendation: {issue['recommendation']}")

print(f"\nConfidence Score: {analysis['confidence_score']:.2%}")
```

### Output
```
Overall Status: REVIEW_REQUIRED

Detected Objects:
  - Shelf: 3 units
  - Item: 8 units

Issues Found:
  - [HIGH] Shelf damage detected
    Location: Shelf 2, left section
    Recommendation: Repair or replace damaged shelf

Confidence Score: 92.50%
```

---

## Example 2: Multi-Point Inspection with Report

Perform inspection at multiple waypoints and generate a comprehensive report.

```python
from robot_inspector import CameraProcessor, ReportGenerator
from datetime import datetime

# Setup
processor = CameraProcessor()
report_gen = ReportGenerator(output_dir="./inspection_reports")

# Inspection waypoints with images
inspection_points = []
robot_path = [{"x": 0, "y": 0}]

waypoints = [
    {"id": 1, "image": "shelf_area_1.png", "x": 1.5, "y": 0},
    {"id": 2, "image": "shelf_area_2.png", "x": 3.0, "y": 0},
    {"id": 3, "image": "floor_area.png", "x": 4.5, "y": 0},
]

# Analyze each waypoint
for wp in waypoints:
    with open(wp["image"], "rb") as f:
        image_bytes = f.read()
    
    analysis = processor.process_image_with_claude(
        image_bytes,
        context=f"Warehouse area {wp['id']}"
    )
    
    inspection_points.append({
        "waypoint_id": wp["id"],
        "position": {"x": wp["x"], "y": wp["y"]},
        "image_analysis": analysis
    })
    
    robot_path.append({"x": wp["x"], "y": wp["y"]})
    print(f"✓ Waypoint {wp['id']}: {analysis['overall_status']}")

# Generate comprehensive report
report = report_gen.create_inspection_report(
    inspection_id=f"INS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    robot_path=robot_path,
    inspection_points=inspection_points
)

# Export in multiple formats
json_file = report_gen.export_json(report)
md_file = report_gen.export_markdown(report)
html_file = report_gen.export_html(report)

print(f"\nReports generated:")
print(f"  JSON: {json_file}")
print(f"  Markdown: {md_file}")
print(f"  HTML: {html_file}")
```

---

## Example 3: Before & After Comparison

Compare two inspection rounds to detect changes.

```python
from robot_inspector import CameraProcessor
import json

processor = CameraProcessor()

# First inspection
with open("area_before.png", "rb") as f:
    before_bytes = f.read()
analysis_before = processor.process_image_with_claude(
    before_bytes,
    context="Quality control inspection"
)

# Second inspection (same area after maintenance)
with open("area_after.png", "rb") as f:
    after_bytes = f.read()
analysis_after = processor.process_image_with_claude(
    after_bytes,
    context="Quality control inspection"
)

# Compare
comparison = processor.compare_analyses(analysis_before, analysis_after)

print("Comparison Report")
print("=" * 50)

if comparison['objects_changed']:
    print("\n🔄 Objects Changed:")
    for change in comparison['objects_changed']:
        delta = "+" if change['delta'] > 0 else ""
        print(f"  {change['object']}: {change['before']} → {change['after']} ({delta}{change['delta']})")

if comparison['new_issues']:
    print("\n⚠️ New Issues:")
    for issue in comparison['new_issues']:
        print(f"  - {issue}")

if comparison['resolved_issues']:
    print("\n✅ Resolved Issues:")
    for issue in comparison['resolved_issues']:
        print(f"  - {issue}")

print("\n" + "=" * 50)
```

---

## Example 4: Batch Processing Multiple Images

Process multiple images in a batch operation.

```python
from robot_inspector import CameraProcessor
from pathlib import Path
import json

processor = CameraProcessor()

# Collect all PNG files
image_dir = Path("./images")
image_files = sorted(image_dir.glob("*.png"))

results = []

for img_file in image_files:
    print(f"Processing {img_file.name}...", end=" ")
    
    with open(img_file, "rb") as f:
        image_bytes = f.read()
    
    analysis = processor.process_image_with_claude(
        image_bytes,
        context="Batch quality control scan"
    )
    
    results.append({
        "file": img_file.name,
        "status": analysis['overall_status'],
        "issues": len(analysis['detected_issues']),
        "confidence": analysis['confidence_score'],
        "analysis": analysis
    })
    
    print(f"✓ {analysis['overall_status']}")

# Summary
print("\n" + "=" * 50)
print("Batch Processing Summary")
print("=" * 50)
print(f"Total images: {len(results)}")
print(f"Passed: {sum(1 for r in results if r['status'] == 'PASS')}")
print(f"Review needed: {sum(1 for r in results if r['status'] == 'REVIEW_REQUIRED')}")
print(f"Failed: {sum(1 for r in results if r['status'] == 'FAIL')}")

# Save results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## Example 5: Custom Analysis Workflow

Implement custom inspection logic with image annotations.

```python
from robot_inspector import (
    CameraProcessor, ReportGenerator, 
    add_text_overlay, add_bounding_box, 
    save_image, get_image_dimensions
)
from PIL import Image
import json

processor = CameraProcessor()
report_gen = ReportGenerator()

# Load inspection image
image_path = "production_line.png"
with open(image_path, "rb") as f:
    image_bytes = f.read()

# Analyze
analysis = processor.process_image_with_claude(
    image_bytes,
    context="Production line quality control"
)

# Annotate image with findings
annotated = image_bytes

# Add overall status
status_text = f"Status: {analysis['overall_status']}"
annotated = add_text_overlay(
    annotated, 
    status_text, 
    position=(20, 40)
)

# Add issue count
issues_text = f"Issues: {len(analysis['detected_issues'])}"
annotated = add_text_overlay(
    annotated,
    issues_text,
    position=(20, 80)
)

# Add severity breakdown
severity_text = f"Critical: {sum(1 for i in analysis['detected_issues'] if i['severity'] == 'CRITICAL')}"
annotated = add_text_overlay(
    annotated,
    severity_text,
    position=(20, 120)
)

# Save annotated image
save_image(annotated, f"annotated_{image_path}")

# Create report with additional metadata
report = report_gen.create_inspection_report(
    inspection_id="PROD_2026_04_03_001",
    robot_path=[{"x": 0, "y": 0}, {"x": 5, "y": 0}],
    inspection_points=[{
        "waypoint_id": 1,
        "position": {"x": 2.5, "y": 0},
        "image_analysis": analysis,
        "image_file": image_path,
        "annotated_file": f"annotated_{image_path}"
    }]
)

# Export
report_gen.export_json(report)
print(f"✓ Inspection complete: {analysis['overall_status']}")
```

---

## Example 6: Quality Control Automation

Automated quality control pipeline with decision logic.

```python
from robot_inspector import CameraProcessor, ReportGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

processor = CameraProcessor()

def perform_qc_inspection(image_bytes, product_id):
    """Run QC inspection and return pass/fail decision."""
    
    logger.info(f"Inspecting product {product_id}")
    
    # Analyze
    analysis = processor.process_image_with_claude(
        image_bytes,
        context=f"Product quality control: {product_id}"
    )
    
    # Get severity counts
    critical_count = sum(1 for i in analysis['detected_issues'] 
                        if i['severity'] == 'CRITICAL')
    high_count = sum(1 for i in analysis['detected_issues'] 
                     if i['severity'] == 'HIGH')
    
    # Decision logic
    if critical_count > 0:
        decision = "REJECT"
        reason = f"Found {critical_count} critical defect(s)"
    elif high_count >= 2:
        decision = "REVIEW"
        reason = f"Found {high_count} high-severity issues"
    elif analysis['confidence_score'] < 0.70:
        decision = "REVIEW"
        reason = f"Low confidence: {analysis['confidence_score']:.1%}"
    else:
        decision = "PASS"
        reason = analysis['scene_description']
    
    # Log decision
    logger.info(f"{product_id}: {decision} - {reason}")
    
    return {
        "product_id": product_id,
        "decision": decision,
        "confidence": analysis['confidence_score'],
        "analysis": analysis
    }

# Run on batch of products
import glob

products_directory = "./products_to_inspect"
results = []

for img_file in glob.glob(f"{products_directory}/*.png"):
    product_id = Path(img_file).stem
    
    with open(img_file, "rb") as f:
        image_bytes = f.read()
    
    result = perform_qc_inspection(image_bytes, product_id)
    results.append(result)

# Summary
passed = sum(1 for r in results if r['decision'] == 'PASS')
failed = sum(1 for r in results if r['decision'] == 'REJECT')
review = sum(1 for r in results if r['decision'] == 'REVIEW')

logger.info(f"\n{'='*50}")
logger.info(f"QC Summary: {passed} passed, {failed} rejected, {review} review")
logger.info(f"{'='*50}")
```

---

## Example 7: Integration with ROS2 (Future)

Preview of how to integrate with ROS2 nodes:

```python
# This is pseudocode for future ROS2 integration
import rclpy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from robot_inspector import CameraProcessor, ReportGenerator

class InspectorNode(rclpy.node.Node):
    def __init__(self):
        super().__init__('robot_inspector')
        self.processor = CameraProcessor()
        self.report_gen = ReportGenerator()
        self.bridge = CvBridge()
        
        # Subscribe to camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        # Publisher for results
        self.analysis_pub = self.create_publisher(
            # Custom message type
            AnalysisResult,
            '/robot_inspector/analysis',
            10
        )

    def image_callback(self, msg):
        # Convert ROS image to bytes
        cv_image = self.bridge.imgmsg_to_cv2(msg)
        image_bytes = # ... convert to PNG ...
        
        # Analyze
        analysis = self.processor.process_image_with_claude(image_bytes)
        
        # Publish results
        result_msg = AnalysisResult()
        result_msg.status = analysis['overall_status']
        self.analysis_pub.publish(result_msg)

if __name__ == '__main__':
    rclpy.init()
    node = InspectorNode()
    rclpy.spin(node)
```

---

## Performance Tips

1. **Image Optimization**: Resize large images to reduce API costs
   ```python
   from robot_inspector import resize_image
   optimized = resize_image(image_bytes, max_width=1024)
   ```

2. **Batch Processing**: Process multiple images efficiently
   - Use lists to collect analyses
   - Export reports in bulk
   - Minimize API calls

3. **Confidence Filtering**: Focus on high-confidence results
   ```python
   if analysis['confidence_score'] >= 0.85:
       # Use result
   ```

4. **Caching**: Store analysis history
   ```python
   history = processor.get_analysis_history()
   ```

---

## Troubleshooting Examples

### Example: Handle API Errors Gracefully

```python
from robot_inspector import CameraProcessor

processor = CameraProcessor()

try:
    analysis = processor.process_image_with_claude(image_bytes)
except Exception as e:
    print(f"Analysis failed: {e}")
    # Fallback behavior
    analysis = {
        "objects": [],
        "detected_issues": [],
        "overall_status": "ERROR",
        "confidence_score": 0.0
    }
```

### Example: Validate Image Format

```python
from PIL import Image
from io import BytesIO

def validate_image(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes))
        if img.format not in ['PNG', 'JPEG']:
            raise ValueError(f"Unsupported format: {img.format}")
        return True
    except Exception as e:
        print(f"Invalid image: {e}")
        return False
```

---

See [README.md](README.md) for full documentation.
