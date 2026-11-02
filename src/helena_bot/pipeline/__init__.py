"""
Package: helena_bot.pipeline

Coordinates the document ingestion pipeline for HelenaBot.

This package contains all the components needed to:
- Parse and render PDF content
- Detect and extract diagrams or fallback to text
- Generate embeddings using transformer models
- Persist image and vector data into MongoDB and ChromaDB
- Track indexing metrics per client

Modules:
- controller: Orchestrates full ingestion from folder to storage
- image_embedding: Processes a single PDF (page-wise)
- pdf_extractor (future): Abstracts rendering and OpenCV operations

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .controller import render_and_index_pdfs
from .image_embedding import process_pdf_document, process_pdf_page

__all__ = ["render_and_index_pdfs", "process_pdf_document", "process_pdf_page"]
