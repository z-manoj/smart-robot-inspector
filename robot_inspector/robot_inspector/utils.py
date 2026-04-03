"""
Utility functions for image processing, file handling, and data conversion.
"""

import logging
from typing import Tuple
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def resize_image(image_bytes: bytes, max_width: int = 1024, max_height: int = 768) -> bytes:
    """
    Resize image to reduce token usage while maintaining quality.

    Args:
        image_bytes: Original image bytes
        max_width: Maximum width
        max_height: Maximum height

    Returns:
        Resized image bytes
    """
    try:
        img = Image.open(BytesIO(image_bytes))

        # Calculate aspect ratio
        aspect_ratio = img.width / img.height

        # Calculate new dimensions
        if img.width > max_width or img.height > max_height:
            if aspect_ratio > max_width / max_height:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save as PNG
        output = BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()

    except Exception as e:
        logger.warning(f"Error resizing image: {e}. Returning original.")
        return image_bytes


def convert_cv_to_png(cv_image: np.ndarray) -> bytes:
    """
    Convert OpenCV image to PNG bytes.

    Args:
        cv_image: OpenCV image (BGR format)

    Returns:
        PNG image bytes
    """
    # Convert BGR to RGB for PIL
    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)

    output = BytesIO()
    pil_image.save(output, format="PNG")
    return output.getvalue()


def convert_png_to_cv(image_bytes: bytes) -> np.ndarray:
    """
    Convert PNG bytes to OpenCV image.

    Args:
        image_bytes: PNG image bytes

    Returns:
        OpenCV image (BGR format)
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return cv_image


def add_text_overlay(image_bytes: bytes, text: str, position: Tuple[int, int] = (10, 30)) -> bytes:
    """
    Add text overlay to image.

    Args:
        image_bytes: Image bytes
        text: Text to overlay
        position: (x, y) position for text

    Returns:
        Image with overlay
    """
    cv_image = convert_png_to_cv(image_bytes)
    cv2.putText(
        cv_image,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )
    return convert_cv_to_png(cv_image)


def add_bounding_box(
    image_bytes: bytes,
    bbox: Tuple[int, int, int, int],
    label: str = "",
    color: Tuple[int, int, int] = (0, 255, 0),
) -> bytes:
    """
    Add bounding box to image.

    Args:
        image_bytes: Image bytes
        bbox: (x1, y1, x2, y2) coordinates
        label: Text label
        color: BGR color tuple

    Returns:
        Image with bounding box
    """
    cv_image = convert_png_to_cv(image_bytes)
    x1, y1, x2, y2 = bbox
    cv2.rectangle(cv_image, (x1, y1), (x2, y2), color, 2)

    if label:
        cv2.putText(cv_image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    return convert_cv_to_png(cv_image)


def save_image(image_bytes: bytes, filepath: str):
    """Save image bytes to file."""
    img = Image.open(BytesIO(image_bytes))
    img.save(filepath)
    logger.info(f"Image saved to {filepath}")


def load_image(filepath: str) -> bytes:
    """Load image from file and return as bytes."""
    with open(filepath, "rb") as f:
        return f.read()


def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    """
    Get image width and height.

    Args:
        image_bytes: Image bytes

    Returns:
        (width, height) tuple
    """
    img = Image.open(BytesIO(image_bytes))
    return img.width, img.height
