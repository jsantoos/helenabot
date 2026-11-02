"""
Module: helena_bot.utils.types.document_types

Defines structured types for document segment processing in HelenaBot.

This module provides the `DocumentPageContext` TypedDict, which represents the
metadata and inputs required to process a segment (page, section, or row) of
a document (PDF, DOCX, CSV). This context is used to generate embeddings,
store image artifacts, and perform vector-based indexing.

Context includes:
- File identifiers and segment references
- Rendering and text context
- References to embedding models, MongoDB, and ChromaDB

Applies:
- PEP 8: Style Guide for Python Code
- PEP 20: The Zen of Python
- PEP 257: Docstring Conventions
- PEP 484: Type Hints
"""

from typing import Any, TypedDict

from pymongo.collection import Collection


class DocumentPageContext(TypedDict, total=False):
    """
    Represents the contextual inputs needed to process a page/segment from a document.

    Attributes:
        filename (str): Name of the source document.
        page_number (int, optional): Page number (for PDFs).
        section_title (str, optional): Section header (for DOCX).
        row_index (int, optional): Row index (for CSV).
        page_text (str, optional): Contextual text content.
        image_cv (Any): OpenCV image (NumPy array) of the content segment.
        client_name (str): Client identifier.
        embed_model (Any): Embedding model instance.
        vector_store (Any): Vector store interface.
        mongo_collection (Collection): MongoDB collection reference.
        source_type (str): Document type: "pdf", "docx", "csv".
    """

    filename: str
    image_cv: Any
    client_name: str
    embed_model: Any
    vector_store: Any
    mongo_collection: Collection
    source_type: str

    # Optional fields depending on document type
    page_number: int
    section_title: str
    row_index: int
    page_text: str
