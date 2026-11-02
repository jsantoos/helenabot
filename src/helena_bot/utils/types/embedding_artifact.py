"""
Module: helena_bot.utils.types.embedding_artifact

Defines a structure to encapsulate all fields required to construct
embedding metadata for MongoDB and ChromaDB in HelenaBot's pipeline.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import List, NamedTuple


class EmbeddingArtifact(NamedTuple):
    """
    Groups embedding-related content for a single image or text region.

    Attributes:
        name (str): Unique identifier (e.g. filename_p3_b1.png or p3_noimage).
        context_text (str): Textual context for the embedding, often includes page excerpt and identifiers.
        embedding (List[float]): Vector embedding to be stored.
        image_bytes (bytes): PNG-encoded image bytes (empty in text-only fallback).
        embedding_hash (str): SHA-256 hash representing the embedding.
    """

    name: str
    context_text: str
    embedding: List[float]
    image_bytes: bytes
    embedding_hash: str
