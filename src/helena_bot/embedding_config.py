"""
Module: helena_bot.embedding_config

Centralizes configuration for the embedding model used across HelenaBot's pipeline,
including retrieval and storage systems (MongoDB and ChromaDB).

This module ensures consistency of model identifiers and versioning between
embedding generation and comparison.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    """
    Configuration holder for embedding-related constants.

    Attributes:
        model_name (str): Identifier of the HuggingFace model used to generate embeddings.
        version (str): Version tag used to separate embedding generations across versions.
                       Must be changed manually when switching models to avoid mixing vectors.
    """

    model_name: str = "intfloat/multilingual-e5-large"
    version: str = "v1-e5-large"


# Global constant for access throughout the system
EMBEDDING_CONFIG = EmbeddingConfig()

__all__ = ["EMBEDDING_CONFIG"]
