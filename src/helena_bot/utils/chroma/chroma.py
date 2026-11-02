"""
Module: helena_bot.utils.chroma_utils

Utility functions to manage vector storage operations using ChromaDB
in HelenaBot's embedding pipeline.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from helena_bot import app_state
from helena_bot.embedding_config import EMBEDDING_CONFIG
from helena_bot.utils.metrics import safe_increment
from helena_bot.utils.types import ChromaEmbeddingMetadata
from llama_index.core.schema import TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore


def add_embedding_to_chroma(
    vector_store: ChromaVectorStore,
    metadata: ChromaEmbeddingMetadata,
) -> None:
    """
    Add a vector embedding and its associated metadata to ChromaDB.

    This function wraps a `TextNode` with all necessary identification and retrieval
    metadata and persists it in the Chroma vector store. It also increments global
    and per-client embedding counters in the runtime metrics store.

    Args:
        vector_store (ChromaVectorStore): ChromaDB-compatible vector store instance.
        metadata (ChromaEmbeddingMetadata): Full metadata and vector payload to register.
    """
    node = TextNode(
        id_=metadata["embedding_hash"],
        text=metadata["context_text"],
        embedding=metadata["embedding"],
    )
    node.metadata = {
        "name": metadata["image_name"],
        "documento": metadata["document_name"],
        "page": metadata["page_number"],
        "embedding_version": EMBEDDING_CONFIG.version,
    }

    vector_store.add([node])

    safe_increment(app_state.metrics, metadata["client_name"], "embeddings_total")
