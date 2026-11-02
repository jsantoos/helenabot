"""
Package: helena_bot.utils.context

Manages prompt context construction for interaction with LLMs.

Exposed:
- build_context_safe: Builds prompt strings from past interactions and new questions.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .prompt_builder import build_context_safe

__all__ = ["build_context_safe"]
