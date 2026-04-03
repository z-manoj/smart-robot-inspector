"""
ROS2 Inspector Node - Real-time defect detection with Claude AI.

Subscribes to camera feeds and publishes analysis results.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String
import json
import logging
from datetime import datetime
from threading import Thread
from collections import deque
import numpy as np
import cv2
HAS_CV_BRIDGE = False  # Disabled - cv_bridge incompatible with NumPy 2.x

from .camera_processor import CameraProcessor
from .llm_provider import create_provider
from .report_generator import ReportGenerator
from . import utils

logger = logging.getLogger(__name__)


class InspectorNode(Node):
    """
    ROS2 node for real-time robot inspection using Claude AI vision.

    Subscribes to: /camera/image_raw (sensor_msgs/Image)
    Publishes to: /robot_inspector/analysis (std_msgs/String - JSON)

    Parameters:
        bedrock_region: AWS region for Bedrock
        model_id: Bedrock Claude model ID
        image_topic: Input camera topic
        analysis_topic: Output analysis topic
        inspection_interval_ms: Milliseconds between inspections
        max_queue_size: Maximum buffered images
        confidence_threshold: Minimum confidence score to publish
        enable_visualization: Enable visualization markers
    """

    def __init__(self):
        super().__init__('robot_inspector')

        # Declare parameters
        self.declare_parameter('llm_provider', 'bedrock')
        self.declare_parameter('bedrock_region', 'us-east-1')
        self.declare_parameter('model_id', 'us.anthropic.claude-opus-4-6-v1')
        self.declare_parameter('image_topic', '/camera/image_raw')
        self.declare_parameter('analysis_topic', '/robot_inspector/analysis')
        self.declare_parameter('report_output_dir', './reports')
        self.declare_parameter('inspection_interval_ms', 1000)
        self.declare_parameter('max_queue_size', 10)
        self.declare_parameter('confidence_threshold', 0.30)
        self.declare_parameter('enable_visualization', True)

        # Get parameters
        self.llm_provider_name = self.get_parameter('llm_provider').value
        self.bedrock_region = self.get_parameter('bedrock_region').value
        self.model_id = self.get_parameter('model_id').value
        image_topic = self.get_parameter('image_topic').value
        analysis_topic = self.get_parameter('analysis_topic').value
        self.report_output_dir = self.get_parameter('report_output_dir').value
        self.inspection_interval = self.get_parameter('inspection_interval_ms').value / 1000.0
        self.max_queue_size = self.get_parameter('max_queue_size').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value
        self.enable_visualization = self.get_parameter('enable_visualization').value

        # Initialize processors
        try:
            provider = create_provider(
                provider_name=self.llm_provider_name,
                region_name=self.bedrock_region,
                model_id=self.model_id,
            )
            self.processor = CameraProcessor(provider=provider)
            self.report_gen = ReportGenerator(output_dir=self.report_output_dir)
            self.get_logger().info(
                f"✓ Initialized with LLM provider: {self.llm_provider_name}, "
                f"model: {self.model_id}"
            )
        except Exception as e:
            self.get_logger().error(f"Failed to initialize processors: {e}")
            raise

        # Image handling
        if HAS_CV_BRIDGE:
            self.cv_bridge = CvBridge()
        else:
            self.cv_bridge = None
            self.get_logger().warn("cv_bridge not available, using manual image conversion")
        self.image_queue = deque(maxlen=self.max_queue_size)

        # ROS2 subscribers and publishers
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )

        self.camera_sub = self.create_subscription(
            Image,
            image_topic,
            self.camera_callback,
            qos_profile
        )

        self.analysis_pub = self.create_publisher(
            String,
            analysis_topic,
            10
        )

        # Inspection state
        self.inspection_id_base = f"ros2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.inspection_count = 0
        self.waypoint_count = 0
        self.robot_path = [{"x": 0.0, "y": 0.0}]  # Start at origin
        self.inspection_points = []

        # Processing thread
        self.processing_thread = Thread(target=self.processing_loop, daemon=True)
        self.processing_thread.start()

        self.get_logger().info(
            f"✓ Inspector node initialized. Subscribing to: {image_topic}"
        )
        self.get_logger().info(f"✓ Publishing analysis to: {analysis_topic}")

    def camera_callback(self, msg: Image):
        """
        Callback for incoming camera images.
        Buffers images for async processing.

        Args:
            msg: sensor_msgs/Image message
        """
        try:
            # Convert ROS image to OpenCV format
            if self.cv_bridge:
                cv_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            else:
                # Manual conversion: ROS Image -> numpy -> OpenCV
                img_array = np.frombuffer(msg.data, dtype=np.uint8)
                cv_image = img_array.reshape((msg.height, msg.width, 3))
                if msg.encoding == 'rgb8':
                    cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)

            # Convert to PNG bytes
            image_bytes = utils.convert_cv_to_png(cv_image)

            # Add to queue for processing
            self.image_queue.append({
                'data': image_bytes,
                'timestamp': msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9,
                'frame_id': msg.header.frame_id
            })

            self.get_logger().debug(
                f"Queued image from {msg.header.frame_id} "
                f"(queue size: {len(self.image_queue)})"
            )

        except Exception as e:
            self.get_logger().error(f"Error processing camera message: {e}")

    def processing_loop(self):
        """
        Background thread for image processing.
        Analyzes images at specified intervals.
        """
        self.get_logger().info(
            f"Processing loop started. Interval: {self.inspection_interval}s"
        )

        import time as _time
        while rclpy.ok():
            try:
                # Process one image from queue
                if len(self.image_queue) > 0:
                    image_data = self.image_queue.popleft()
                    self.analyze_and_publish(image_data)

                _time.sleep(self.inspection_interval)

            except Exception as e:
                self.get_logger().error(f"Error in processing loop: {e}")

    def analyze_and_publish(self, image_data: dict):
        """
        Analyze image and publish results.

        Args:
            image_data: Dict with 'data', 'timestamp', 'frame_id'
        """
        try:
            self.get_logger().info("Starting image analysis...")

            # Analyze with Claude
            analysis = self.processor.process_image_with_claude(
                image_data['data'],
                context="Warehouse shelf inspection. You are a robot inspector examining products on warehouse shelves. Look for: damaged items, fallen/tilted products, missing items, stains, structural damage to shelves, improper stacking. The colored boxes are products/packages stored on brown wooden shelves.",
                include_severity=True
            )

            # Check confidence threshold
            confidence = analysis.get('confidence_score', 0.0)
            if confidence < self.confidence_threshold:
                self.get_logger().warn(
                    f"Confidence {confidence:.2%} below threshold "
                    f"{self.confidence_threshold:.2%}. Skipping publication."
                )
                return

            # Create inspection point
            self.inspection_count += 1
            self.waypoint_count += 1

            inspection_point = {
                'waypoint_id': self.waypoint_count,
                'position': {
                    'x': float(self.waypoint_count * 1.5),
                    'y': 0.0
                },
                'image_analysis': analysis
            }

            self.inspection_points.append(inspection_point)
            self.robot_path.append(inspection_point['position'])

            # Prepare result message
            result = {
                'timestamp': datetime.now().isoformat(),
                'inspection_id': f"{self.inspection_id_base}_{self.inspection_count:03d}",
                'waypoint': self.waypoint_count,
                'analysis': analysis
            }

            # Publish result
            msg = String()
            msg.data = json.dumps(result)
            self.analysis_pub.publish(msg)

            self.get_logger().info(
                f"✓ Analysis {self.inspection_count} published. "
                f"Status: {analysis['overall_status']}, "
                f"Issues: {len(analysis.get('detected_issues', []))}"
            )

            # Generate report if enabled
            if self.enable_visualization:
                self.generate_report()

        except Exception as e:
            self.get_logger().error(f"Error analyzing image: {e}")

    def generate_report(self):
        """
        Generate inspection report for accumulated data.
        Called periodically during operation.
        """
        try:
            if len(self.inspection_points) == 0:
                return

            # Create aggregated report
            report = self.report_gen.create_inspection_report(
                inspection_id=f"{self.inspection_id_base}_aggregated",
                robot_path=self.robot_path,
                inspection_points=self.inspection_points
            )

            # Export in all formats
            self.report_gen.export_json(report)
            self.report_gen.export_markdown(report)
            self.report_gen.export_html(report)

            self.get_logger().debug(
                f"Report generated with {len(self.inspection_points)} points"
            )

        except Exception as e:
            self.get_logger().error(f"Error generating report: {e}")

    def get_inspection_summary(self) -> dict:
        """
        Get current inspection summary.

        Returns:
            Dict with inspection statistics
        """
        total_issues = 0
        critical_count = 0
        high_count = 0

        for point in self.inspection_points:
            issues = point.get('image_analysis', {}).get('detected_issues', [])
            total_issues += len(issues)
            for issue in issues:
                severity = issue.get('severity', '').upper()
                if severity == 'CRITICAL':
                    critical_count += 1
                elif severity == 'HIGH':
                    high_count += 1

        return {
            'inspection_id': self.inspection_id_base,
            'inspection_count': self.inspection_count,
            'waypoint_count': self.waypoint_count,
            'total_issues': total_issues,
            'critical_issues': critical_count,
            'high_issues': high_count,
            'inspection_points': len(self.inspection_points),
            'status': 'FAIL' if critical_count > 0 else 'REVIEW_REQUIRED' if high_count > 0 else 'PASS'
        }


def main(args=None):
    """Main entry point for ROS2 node."""
    rclpy.init(args=args)

    try:
        node = InspectorNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down inspector node...")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
