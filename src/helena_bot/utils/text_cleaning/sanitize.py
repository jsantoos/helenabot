"""
Module: helena_bot.utils.text_cleaning.sanitize

Provides text cleaning and normalization utilities for HelenaBot.

This module includes helper functions to sanitize strings before passing them
to the LLM or embedding engines. These utilities remove redundant lines,
trim whitespace, and enforce token limits using fallback summarization logic.

Used during:
- Prompt preparation
- Embedding context cleaning
- Resposta final gerada pelo modelo

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
from typing import Optional

from helena_bot.utils.summarization import summarize_text
from helena_bot.utils.tokening import count_tokens

logger = logging.getLogger(__name__)

MAX_TOTAL_TOKENS = 3072


def sanitize_text(value: Optional[str], fallback: str = "") -> str:
    """
    Return a cleaned string, handling None or empty cases safely.

    Args:
        value (Optional[str]): Raw input value to clean.
        fallback (str): Value to return if input is None or invalid.

    Returns:
        str: Sanitized string.
    """
    if not isinstance(value, str):
        return fallback
    return value.strip() or fallback


def sanitize_prompt(prompt: str) -> str:
    """
    Clean and deduplicate a multi-line prompt, applying fallback summarization if needed.

    - Removes empty and repeated lines.
    - Trims surrounding whitespace.
    - If prompt exceeds token threshold, applies `summarize_text`.

    Args:
        prompt (str): Raw prompt to be cleaned.

    Returns:
        str: Sanitized and optionally summarized prompt.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        return ""

    seen = set()
    cleaned_lines = []
    for line in prompt.splitlines():
        stripped = line.strip()
        if stripped and stripped not in seen:
            cleaned_lines.append(stripped)
            seen.add(stripped)

    cleaned_prompt = "\n".join(cleaned_lines)

    if count_tokens(cleaned_prompt) > MAX_TOTAL_TOKENS:
        logger.warning("Prompt sanitizado com excesso de tokens. Aplicando resumo.")
        return summarize_text(cleaned_prompt)

    return cleaned_prompt
