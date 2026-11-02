"""
Module: helena_bot.pipeline.controller

Coordinates the ingestion pipeline for a given client's PDF directory.
Builds embedding vectors, stores metadata, and indexes documents in ChromaDB and MongoDB.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
import os

from helena_bot import app_state
from helena_bot.pipeline.image_embedding import process_pdf_document
from helena_bot.utils.storage import save_metrics
from helena_bot.utils.types import PdfDocumentContext, PDFIndexingContext

logger = logging.getLogger(__name__)


def render_and_index_pdfs(ctx: PDFIndexingContext) -> None:
    """
    Triggers the full indexing process for all PDFs in a client's folder.

    Args:
        ctx (PDFIndexingContext): Structured indexing configuration.
    """
    logger.info(
        "📂 Iniciando processamento de PDFs para cliente: %s", ctx["client_name"]
    )

    default_metrics = {
        "connected_users": set(),
        "messages_sent": 0,
        "images_sent": 0,
        "interactions": 0,
        "embeddings_total": 0,
        "images_saved": 0,
        "pdfs_processed": 0,
    }
    app_state.metrics["per_client"].setdefault(
        ctx["client_name"], default_metrics.copy()
    )

    for filename in os.listdir(ctx["documents_path"]):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_ctx: PdfDocumentContext = {
            "filename": filename,
            "client_name": ctx["client_name"],
            "embed_model": ctx["embed_model"],
            "vector_store": ctx["vector_store"],
            "mongo_collection": ctx["mongo_collection"],
            "pdf_folder": ctx["documents_path"],
            "dpi": ctx["dpi"],
            "max_pages": ctx["max_pages"],
        }

        try:
            process_pdf_document(pdf_ctx)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("❌ Falha ao processar %s: %s", filename, e)

    logger.info("📁 Finalizado o processamento dos PDFs de %s", ctx["client_name"])

    save_metrics(app_state.metrics, ctx["mongo_collection"])
