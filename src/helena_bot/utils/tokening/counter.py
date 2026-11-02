"""
Module: helena_bot.utils.tokening.counter

Provides token estimation logic for text strings in HelenaBot.

This module defines a lightweight utility to estimate token count from raw text.
It is used for enforcing model constraints, deciding when to summarize, and managing
prompt context size.

The estimation is based on a heuristic of ~0.75 tokens per word, which aligns
reasonably with tokenization in GPT-family and BART-family models.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import Optional


def count_tokens(text: Optional[str]) -> int:
    """
    Estimate the approximate number of tokens in a given text.

    Assumes that one token corresponds to approximately 0.75 words,
    which works well for OpenAI and Hugging Face transformer models.

    Args:
        text (Optional[str]): The text string to evaluate.

    Returns:
        int: Estimated number of tokens in the text.
    """
    if not text or not isinstance(text, str):
        return 0
    return int(len(text.split()) * 0.75)
