"""
Package: helena_bot.utils.types

Defines and exposes reusable type aliases and structured schemas used throughout
HelenaBot for static typing, data validation, and inter-module communication.

This package centralizes TypedDicts and type definitions for:
- Embedding pipelines (document/page context, chunking artifacts)
- MongoDB persistence (image metadata, user interactions)
- ChromaDB indexing and retrieval schemas
- Telegram session and handler contexts

These definitions enforce strong typing and increase maintainability across:
- Bot event handling (message/voice commands)
- PDF embedding workflows
- Vector store interactions (Chroma)
- Internal metrics and caching strategies

Exposed types:
- ImageMetadata: MongoDB schema for storing embedded image metadata
- InteractionData: User interaction history format for dialogue tracking
- ChromaEmbeddingMetadata: Metadata structure stored alongside embeddings in ChromaDB
- PdfPageContext / PdfDocumentContext: Page-level and document-level context for PDF indexing
- EmbeddingArtifact: Transport structure for grouped embedding + image payload
- PDFIndexingContext: Full configuration for batch PDF processing during pipeline execution

Applies:
- PEP 8: Code Style Guide
- PEP 20: The Zen of Python
- PEP 257: Docstring Conventions
- PEP 484: Type Hints
"""

from .chroma_types import ChromaEmbeddingMetadata
from .document_types import DocumentPageContext
from .embedding_artifact import EmbeddingArtifact
from .indexing_types import PDFIndexingContext
from .mongo_types import ImageMetadata, InteractionData
from .pdf_document_types import PdfDocumentContext

__all__ = [
    "ChromaEmbeddingMetadata",
    "EmbeddingArtifact",
    "ImageMetadata",
    "PDFIndexingContext",
    "InteractionData",
    "DocumentPageContext",
    "PdfDocumentContext",
]
