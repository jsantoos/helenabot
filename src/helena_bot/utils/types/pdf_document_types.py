"""
Module: helena_bot.utils.types.pdf_document_types

Defines structured types related to full PDF document processing within HelenaBot.

Currently includes:
- PdfDocumentContext: Represents all necessary inputs for processing an entire PDF document,
  including configuration, model instances, and storage handles.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import Any, TypedDict

from pymongo.collection import Collection


class PdfDocumentContext(TypedDict):
    """
    Represents the contextual configuration for processing a PDF document.

    Attributes:
        filename (str): Name of the PDF file to be processed.
        client_name (str): Logical client identifier for namespacing and metrics.
        embed_model (Any): Instance of the embedding model to use.
        vector_store (Any): Vector store (e.g., Chroma) to persist embeddings.
        mongo_collection (Collection): MongoDB collection for storing image/embedding data.
        pdf_folder (str): Absolute or relative path to the folder containing the PDF.
        dpi (int): Resolution for rendering pages.
        max_pages (int): Maximum number of pages to process from the document.
    """

    filename: str
    client_name: str
    embed_model: Any
    vector_store: Any
    mongo_collection: Collection
    pdf_folder: str
    dpi: int
    max_pages: int
