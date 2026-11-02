"""
Package: helena_bot.utils.embedding

Provides utilities for safely generating embeddings from long or unstructured text.

This package includes logic to:
- Split long texts into chunks using SentenceSplitter
- Apply fallback strategies to prevent token overflow
- Interface with embedding models in a robust way

Exposed:
- safe_get_embedding: Generates a single embedding from a text, with chunking and error handling.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .embedding import safe_get_embedding

__all__ = ["safe_get_embedding"]
