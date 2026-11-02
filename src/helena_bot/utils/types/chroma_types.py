"""
Module: chroma_types

Defines structured metadata schema for vector storage operations using ChromaDB
within the HelenaBot embedding pipeline.

This module introduces:
- `ChromaEmbeddingMetadata`: A strongly typed schema encapsulating all relevant
  context and metadata required to register a vector embedding in a ChromaDB-compatible
  vector store. This includes both the embedding vector and associated provenance
  details such as source document, page, and image reference.

Context:
- Used by `utils.chroma_utils.add_embedding_to_chroma` to persist vectors generated
  during PDF ingestion.
- Enables typed, consistent integration between the embedding generator, vector store,
  and the runtime metrics system (`app_state.metrics`).

Structure:
- Includes embedding vector, hash ID, textual context, image label, document reference,
  page origin, and client-scoped metrics tracking.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import List, TypedDict


class ChromaEmbeddingMetadata(TypedDict):
    """
    Represents the necessary information to register a vector embedding in ChromaDB.

    Attributes:
        embedding (List[float]): Numerical vector representing the input context.
        embedding_hash (str): Unique identifier (typically SHA-256) for deduplication.
        context_text (str): Raw textual context used to generate the embedding.
        image_name (str): Reference name of the associated image.
        document_name (str): Name of the originating document (PDF).
        page_number (int): Page number from which the content was extracted.
        client_name (str): Logical name used to track per-client metrics.
    """

    embedding: List[float]
    embedding_hash: str
    context_text: str
    image_name: str
    document_name: str
    page_number: int
    client_name: str
