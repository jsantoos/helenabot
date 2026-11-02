"""
Module: helena_bot.utils.hash_utils

Provides hashing utilities for embedding vectors used in HelenaBot.

The primary purpose of this module is to convert high-dimensional float vectors
into compact SHA-256 hashes, which are used as unique identifiers within
embedding-based storage systems like ChromaDB and MongoDB. These hashes help
detect and prevent duplicate vector insertions across the pipeline.

Usage:
- Commonly invoked by `embedding_pipeline.py` and `mongo_utils.py` for deduplication.
- Integrates seamlessly into document processing and embedding registration workflows.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import hashlib
from typing import List


def generate_embedding_hash(embedding: List[float]) -> str:
    """
    Generate a SHA-256 hexadecimal hash from a float embedding vector.

    This function serializes the embedding into a UTF-8 encoded string and then
    applies SHA-256 to create a compact, deterministic identifier. It is used
    primarily to deduplicate embeddings in vector databases and content stores.

    Args:
        embedding (List[float]): Embedding vector generated from a sentence or diagram context.

    Returns:
        str: A SHA-256 hexadecimal hash string uniquely representing the vector.
    """
    embedding_str = str(embedding).encode("utf-8")
    return hashlib.sha256(embedding_str).hexdigest()
