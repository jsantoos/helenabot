"""
Package: helena_bot.utils.image

Provides image processing and analysis utilities for HelenaBot.

This package includes tools to assess image quality and content, primarily to
support PDF diagram extraction and filtering during document embedding.

Exposed:
- is_blank_image_from_bytes: Detects blank or uninformative images using entropy and pixel distribution.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .analysis import is_blank_image_from_bytes

__all__ = ["is_blank_image_from_bytes"]
