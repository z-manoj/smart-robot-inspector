#!/usr/bin/env python3
"""
Standalone demo for robot inspector without ROS2 dependency.
Creates sample images and demonstrates image analysis with Claude via Bedrock.
"""

import sys
import json
import logging
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

from robot_inspector import CameraProcessor, ReportGenerator, save_image, load_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_warehouse_image(filename: str = "warehouse_scan_1.png") -> bytes:
    """
    Create a sample warehouse image with various objects.

    Returns:
        Image bytes in PNG format
    """
    logger.info("Creating sample warehouse image...")

    # Create image with warehouse theme
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)

    # Draw warehouse floor
    draw.rectangle([0, height // 2, width, height], fill=(139, 90, 43))

    # Draw some shelves/objects
    # Shelf 1 - good condition
    draw.rectangle([50, 200, 200, 400], outline="black", width=3)
    draw.text((70, 210), "SHELF-01", fill="black")
    draw.rectangle([60, 250, 90, 350], fill="brown")  # Item 1
    draw.rectangle([110, 250, 140, 350], fill="brown")  # Item 2
    draw.rectangle([160, 250, 190, 350], fill="brown")  # Item 3

    # Shelf 2 - with defect
    draw.rectangle([250, 200, 400, 400], outline="black", width=3)
    draw.text((270, 210), "SHELF-02", fill="black")
    draw.rectangle([260, 250, 290, 350], fill="darkred")  # Damaged item
    draw.rectangle([310, 250, 340, 350], fill="brown")  # Good item
    draw.rectangle([360, 250, 390, 350], fill="brown")  # Good item

    # Add warning indicator
    draw.text((270, 370), "DAMAGE DETECTED", fill="red")

    # Shelf 3 - good
    draw.rectangle([450, 200, 600, 400], outline="black", width=3)
    draw.text((470, 210), "SHELF-03", fill="black")
    draw.rectangle([460, 250, 490, 350], fill="brown")
    draw.rectangle([510, 250, 540, 350], fill="brown")
    draw.rectangle([560, 250, 590, 350], fill="brown")

    # Add floor details
    draw.text((width // 2 - 50, height - 50), "Warehouse Area", fill="white")

    # Save to bytes
    import io
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def create_sample_defective_part_image(filename: str = "defective_part.png") -> bytes:
    """
    Create a sample image showing a defective part.

    Returns:
        Image bytes in PNG format
    """
    logger.info("Creating sample defective part image...")

    width, height = 600, 400
    img = Image.new("RGB", (width, height), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)

    # Draw a part with defect
    # Main part body
    draw.ellipse([150, 100, 450, 300], outline="black", width=3, fill="lightblue")
    draw.text((250, 150), "PART-12345", fill="black")

    # Draw defect (crack)
    draw.line([(200, 200), (300, 250)], fill="red", width=4)
    draw.text((210, 260), "CRACK DETECTED", fill="red")

    # Quality stamp
    draw.text((350, 350), "QC STATUS: REJECT", fill="red")

    # Save to bytes
    import io
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def main():
    """Run demo inspection workflow."""
    logger.info("=" * 60)
    logger.info("Smart Robot Inspector - Standalone Demo")
    logger.info("=" * 60)

    # Check AWS credentials
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
            logger.warning("AWS credentials not found. Demo will fail on Bedrock calls.")
            logger.info("To use Bedrock:")
            logger.info("1. Configure AWS credentials: aws configure")
            logger.info("2. Ensure you have Bedrock access in your AWS account")
            logger.info("3. Select a region with Claude models available")
            logger.info("\nProceeding with demo (image analysis will fail)...")
    except Exception as e:
        logger.warning(f"Could not check AWS credentials: {e}")

    # Create output directory
    output_dir = Path("./reports")
    output_dir.mkdir(exist_ok=True)

    # Initialize components
    processor = CameraProcessor(region_name="us-east-1")
    report_gen = ReportGenerator(output_dir=str(output_dir))

    # Create sample images
    logger.info("\n[Step 1] Creating sample inspection images...")
    image_1 = create_sample_warehouse_image()
    image_2 = create_sample_defective_part_image()

    # Save samples
    save_image(image_1, str(output_dir / "sample_warehouse.png"))
    save_image(image_2, str(output_dir / "sample_defect.png"))
    logger.info(f"✓ Sample images saved to {output_dir}/")

    # Analyze images with Claude
    logger.info("\n[Step 2] Analyzing images with Claude via AWS Bedrock...")
    logger.info("Note: This requires AWS credentials with Bedrock access")

    try:
        logger.info("Analyzing warehouse image...")
        analysis_1 = processor.process_image_with_claude(
            image_1,
            context="Industrial warehouse inspection with shelves and inventory items",
            include_severity=True,
        )

        logger.info(f"✓ Analysis 1 complete. Status: {analysis_1.get('overall_status', 'UNKNOWN')}")
        logger.info(f"  Issues found: {len(analysis_1.get('detected_issues', []))}")

        logger.info("\nAnalyzing defective part image...")
        analysis_2 = processor.process_image_with_claude(
            image_2,
            context="Quality control inspection of manufactured part",
            include_severity=True,
        )

        logger.info(f"✓ Analysis 2 complete. Status: {analysis_2.get('overall_status', 'UNKNOWN')}")
        logger.info(f"  Issues found: {len(analysis_2.get('detected_issues', []))}")

    except Exception as e:
        logger.error(f"Error during image analysis: {e}")
        logger.info("This is expected if AWS credentials are not configured.")
        logger.info("\nCreating demo report with mock data...")

        # Create mock analyses for demo
        analysis_1 = {
            "objects": [
                {"name": "Shelf", "count": 3, "description": "Metal storage shelves"},
                {"name": "Item", "count": 8, "description": "Packaged items on shelves"},
            ],
            "detected_issues": [
                {
                    "issue": "Shelf damage detected",
                    "severity": "HIGH",
                    "location": "Shelf 2, left section",
                    "recommendation": "Repair or replace damaged shelf",
                }
            ],
            "scene_description": "Warehouse with 3 shelves, 8 items total. One shelf shows visible damage.",
            "confidence_score": 0.85,
            "overall_status": "REVIEW_REQUIRED",
        }

        analysis_2 = {
            "objects": [
                {"name": "Part", "count": 1, "description": "Industrial component"},
            ],
            "detected_issues": [
                {
                    "issue": "Surface crack detected",
                    "severity": "CRITICAL",
                    "location": "Center-left of part",
                    "recommendation": "REJECT part - do not use in production",
                }
            ],
            "scene_description": "Quality control scan shows a critical defect - crack in part material.",
            "confidence_score": 0.92,
            "overall_status": "FAIL",
        }

    # Create inspection report
    logger.info("\n[Step 3] Generating inspection report...")

    inspection_points = [
        {
            "waypoint_id": 1,
            "position": {"x": 1.5, "y": 2.0},
            "image_analysis": analysis_1,
        },
        {
            "waypoint_id": 2,
            "position": {"x": 3.0, "y": 2.0},
            "image_analysis": analysis_2,
        },
    ]

    robot_path = [
        {"x": 0, "y": 0},
        {"x": 1.5, "y": 2.0},
        {"x": 3.0, "y": 2.0},
        {"x": 3.0, "y": 0},
    ]

    report = report_gen.create_inspection_report(
        inspection_id="demo_2026_04_03_001",
        robot_path=robot_path,
        inspection_points=inspection_points,
    )

    # Export reports in multiple formats
    logger.info("Exporting reports...")
    json_path = report_gen.export_json(report)
    md_path = report_gen.export_markdown(report)
    html_path = report_gen.export_html(report)

    logger.info(f"✓ JSON report: {json_path}")
    logger.info(f"✓ Markdown report: {md_path}")
    logger.info(f"✓ HTML report: {html_path}")

    # Display summary
    logger.info("\n" + "=" * 60)
    logger.info("Inspection Summary")
    logger.info("=" * 60)
    logger.info(f"Inspection ID: {report['inspection_id']}")
    logger.info(f"Overall Status: {report['summary']['overall_status']}")
    logger.info(f"Total Issues: {report['summary']['total_issues']}")
    logger.info(f"  - Critical: {report['summary']['issues_by_severity'].get('CRITICAL', 0)}")
    logger.info(f"  - High: {report['summary']['issues_by_severity'].get('HIGH', 0)}")
    logger.info(f"  - Medium: {report['summary']['issues_by_severity'].get('MEDIUM', 0)}")
    logger.info(f"  - Low: {report['summary']['issues_by_severity'].get('LOW', 0)}")

    logger.info("\nRecommendations:")
    for rec in report["recommendations"]:
        logger.info(f"  • {rec}")

    logger.info("\n" + "=" * 60)
    logger.info("✓ Demo completed successfully!")
    logger.info(f"Reports saved to: {output_dir}/")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
