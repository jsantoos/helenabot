"""
Package: helena_bot.utils.summarization

Contains summarization utilities using Hugging Face models for HelenaBot.

Exposed:
- summarize_text: Generates summaries using DistilBART or equivalent models.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .hf_summarizer import summarize_text

__all__ = ["summarize_text"]
