"""Robot Inspector - ROS2 package for intelligent robot inspection with Claude."""

from .camera_processor import CameraProcessor
from .report_generator import ReportGenerator
from .inspection_message import AnalysisMessageConverter, InspectionSummary
from .utils import (
    resize_image,
    convert_cv_to_png,
    convert_png_to_cv,
    add_text_overlay,
    add_bounding_box,
    save_image,
    load_image,
    get_image_dimensions,
)

# ROS2 node (only imported if ROS2 is available)
try:
    from .ros_node import InspectorNode
    __all_ros2__ = ["InspectorNode"]
except ImportError:
    __all_ros2__ = []

__version__ = "0.2.0"
__all__ = [
    "CameraProcessor",
    "ReportGenerator",
    "AnalysisMessageConverter",
    "InspectionSummary",
    "resize_image",
    "convert_cv_to_png",
    "convert_png_to_cv",
    "add_text_overlay",
    "add_bounding_box",
    "save_image",
    "load_image",
    "get_image_dimensions",
] + __all_ros2__
