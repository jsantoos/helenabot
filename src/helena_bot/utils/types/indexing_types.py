"""
Module: helena_bot.utils.types.indexing_types

Defines structured context for orchestrating multi-document PDF indexing.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import Any, Optional, TypedDict

from pymongo.collection import Collection


class PDFIndexingContext(TypedDict):
    """
    Represents the full context required for processing a batch of PDFs for a client.

    Attributes:
        client_name (str): Client identifier.
        embed_model (Any): Embedding model instance.
        vector_store (Any): Chroma vector store.
        mongo_collection (Collection): MongoDB collection.
        documents_path (str): Path to folder containing PDFs.
        dpi (int): PDF rendering resolution.
        max_pages (int): Max number of pages to read per PDF.
    """

    client_name: str
    embed_model: Any
    vector_store: Any
    mongo_collection: Collection
    documents_path: str
    dpi: int
    max_pages: Optional[int]
