"""
Package: helena_bot.utils.chroma

Handles vector storage operations using ChromaDB in HelenaBot.

This package provides utilities to persist vector embeddings into ChromaDB
along with structured metadata, enabling semantic search and retrieval over
textual and visual representations.

Exposed:
- add_embedding_to_chroma: Adds a vector embedding and associated metadata to the Chroma vector store.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .chroma import add_embedding_to_chroma
from .validate import embedding_already_exists

__all__ = ["add_embedding_to_chroma", "embedding_already_exists"]
