"""
Module: helena_bot.utils.image.analysis

Provides utilities for analyzing image content quality in HelenaBot.

Currently focuses on detecting "blank" images using statistical measures such as:
- Standard deviation (contrast)
- White pixel ratio
- Entropy

This is used to filter out uninformative diagram renderings during PDF processing.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import io
import logging

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def is_blank_image_from_bytes(
    image_bytes: bytes,
    std_threshold: float = 6.0,
    white_pixel_ratio: float = 0.99,
    entropy_threshold: float = 3.5,
) -> bool:
    """
    Determine if an image is considered blank based on its pixel distribution.

    The analysis converts the image to grayscale and applies multiple filters:
    - Very high white pixel ratio
    - Low standard deviation (low contrast)
    - Low entropy (limited diversity of information)

    Args:
        image_bytes (bytes): Image file content (typically PNG).
        std_threshold (float): Maximum std deviation for image to be considered blank.
        white_pixel_ratio (float): Maximum ratio of white pixels to consider image empty.
        entropy_threshold (float): Minimum entropy required for the image to be considered meaningful.

    Returns:
        bool: True if the image is considered blank or fails to load; False otherwise.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        arr = np.array(img)

        # Absolute white fallback
        if np.all(arr > 245):
            return True

        std = np.std(arr)
        ratio_white = np.sum(arr > 245) / arr.size

        histogram = img.histogram()
        hist_len = sum(histogram)
        probs = [float(h) / hist_len for h in histogram if h != 0]
        entropy = -sum(p * np.log2(p) for p in probs)

        logger.debug(
            "[IMG] Std: %.2f | White Ratio: %.4f | Entropy: %.2f",
            std,
            ratio_white,
            entropy,
        )

        return bool(
            std < std_threshold
            or ratio_white > white_pixel_ratio
            or entropy < entropy_threshold
        )

    except (IOError, ValueError) as err:
        logger.warning("[IMG] Failed to analyze image for blank check: %s", err)
        return True
