"""
Package: helena_bot.utils.hash

Provides hashing utilities for deterministic identification of embeddings and documents.

This package offers functionality to generate SHA-256 hashes from embedding vectors,
allowing for deduplication, traceability, and stable references in vector storage systems
such as MongoDB and ChromaDB.

Exposed:
- generate_embedding_hash: Computes a SHA-256 hash from a list of floats (embedding vector).

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .hash import generate_embedding_hash

__all__ = ["generate_embedding_hash"]
