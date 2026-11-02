"""
Module: helena_bot.utils.summarization.hf_summarizer

Provides summarization utilities using Hugging Face models for HelenaBot.
This module serves as a safe wrapper around the `pipeline` interface for generating
compact summaries from long pieces of text.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging

from transformers import pipeline

logger = logging.getLogger(__name__)

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")


def summarize_text(text: str, max_tokens: int = 256) -> str:
    """
    Generate a concise summary from the input text using a pretrained Hugging Face model.

    Args:
        text (str): Raw input text to summarize.
        max_tokens (int): Maximum output token length.

    Returns:
        str: Summarized version of the input, or fallback to truncated original.
    """
    try:
        result = summarizer(text, max_length=max_tokens, min_length=30, do_sample=False)
        if isinstance(result, list) and result and isinstance(result[0], dict):
            return result[0].get("summary_text", "")
        logger.warning("Formato inesperado no retorno do summarizer: %s", type(result))
        return text[:max_tokens]
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Erro ao resumir texto: %s", e)
        return text[:max_tokens]
