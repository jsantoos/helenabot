"""
Module: helena_bot.utils.chroma.validate

Contains validation utilities for ChromaDB operations such as
checking for duplicate embeddings by ID (embedding_hash).

This module is intended to be used by the embedding pipeline
to prevent redundant entries in the vector store.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def embedding_already_exists(vector_store: Any, embedding_hash: str) -> bool:
    """
    Checks whether an embedding with the given hash already exists in ChromaDB.

    Args:
        vector_store (Any): Chroma vector store instance.
        embedding_hash (str): Hash to check (used as ID in vector store).

    Returns:
        bool: True if already indexed, False otherwise.
    """
    # pylint: disable=protected-access
    try:
        result = vector_store._collection.get(ids=[embedding_hash])
        return bool(result.get("ids"))
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Erro ao verificar duplicação no ChromaDB: %s", e)
        return False
