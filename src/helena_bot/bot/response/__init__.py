"""
Module: helena_bot.bot.response

Handles all response-related logic, such as sending images or messages
through the Telegram bot in the HelenaBot system.

Exposes:
- send_relevant_images: Public function for replying with relevant images.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .image_sender import send_relevant_images

__all__ = ["send_relevant_images"]
