"""
Package: helena_bot.utils.tokening

Provides utilities related to token counting and limits for HelenaBot.

Exposed:
- count_tokens: Estimates token usage based on text length.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .counter import count_tokens

__all__ = ["count_tokens"]
