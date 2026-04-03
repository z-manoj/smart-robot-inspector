"""Robot Inspector - ROS2 package for intelligent robot inspection with Claude."""

from .camera_processor import CameraProcessor
from .report_generator import ReportGenerator
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

__version__ = "0.1.0"
__all__ = [
    "CameraProcessor",
    "ReportGenerator",
    "resize_image",
    "convert_cv_to_png",
    "convert_png_to_cv",
    "add_text_overlay",
    "add_bounding_box",
    "save_image",
    "load_image",
    "get_image_dimensions",
]
