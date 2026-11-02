"""
Module: helena_bot.pipeline.image_embedding

Processes a single PDF document for HelenaBot:
- Extracts diagrams from rendered pages
- Generates image or fallback text embeddings
- Stores metadata and vectors into MongoDB and ChromaDB
- Applies deduplication and content quality filters

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import io
import logging
import os
from typing import Any

import cv2
import fitz
import numpy as np
from helena_bot import app_state
from helena_bot.utils.chroma import add_embedding_to_chroma, embedding_already_exists
from helena_bot.utils.embedding import safe_get_embedding
from helena_bot.utils.hash import generate_embedding_hash
from helena_bot.utils.image import is_blank_image_from_bytes
from helena_bot.utils.metrics import safe_increment
from helena_bot.utils.storage import ensure_client_metrics, save_image_with_metadata
from helena_bot.utils.types import (
    ChromaEmbeddingMetadata,
    DocumentPageContext,
    EmbeddingArtifact,
    ImageMetadata,
    PdfDocumentContext,
)
from PIL import Image

logger = logging.getLogger(__name__)

# CV2 binding stubs for lint compatibility
# These aliases prevent Pyright/Pylint from reporting "no-member"
cv2.boundingRect = cv2.boundingRect  # type: ignore
cv2.cvtColor = cv2.cvtColor  # type: ignore
cv2.error = cv2.error  # type: ignore
cv2.findContours = cv2.findContours  # type: ignore
cv2.threshold = cv2.threshold  # type: ignore
cv2.CHAIN_APPROX_SIMPLE = cv2.CHAIN_APPROX_SIMPLE  # type: ignore
cv2.COLOR_RGB2GRAY = cv2.COLOR_RGB2GRAY  # type: ignore
cv2.RETR_EXTERNAL = cv2.RETR_EXTERNAL  # type: ignore
cv2.THRESH_BINARY_INV = cv2.THRESH_BINARY_INV  # type: ignore


def process_pdf_page(context: DocumentPageContext) -> bool:
    """
    Processes a single PDF page by extracting image regions or fallback text embeddings.

    Args:
        context (DocumentPageContext): Structured page metadata and model references.

    Returns:
        bool: True if at least one embedding was generated and stored.
    """
    page_text = context["page_text"]
    page_number = context["page_number"]
    filename = context["filename"]
    img_cv = context["image_cv"]

    if not page_text or len(page_text.split()) < 0:
        logger.warning(
            "⚠️ Texto insuficiente para gerar embedding textual: %s (p%d de %s)",
            filename,
            context["page_number"],
            context["filename"],
        )
        return False

    has_embedding = False

    try:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
    except (cv2.error, ValueError) as e:
        logger.warning("Erro ao extrair contornos da página %d: %s", page_number, e)
        contours = []

    for i, cnt in enumerate(contours):
        has_embedding |= _process_diagram_region(context, cnt, i)

    if not has_embedding:
        has_embedding |= _process_textual_embedding(context)

    return has_embedding


def process_pdf_document(ctx: PdfDocumentContext) -> bool:
    """
    Processes a single PDF file: renders pages, builds context, and delegates to page processor.

    Args:
        ctx (PdfDocumentContext): Structured document-level configuration.

    Returns:
        bool: True if at least one embedding was stored; False otherwise.
    """
    ensure_client_metrics(ctx["client_name"], app_state.metrics)

    path = os.path.join(ctx["pdf_folder"], ctx["filename"])
    doc = fitz.open(path)
    processed_pdf = False

    for page_idx in range(min(len(doc), ctx["max_pages"])):
        try:
            page = doc[page_idx]
            page_text = page.get_text().strip()  # type: ignore[attr-defined]

            if not page_text or len(page_text.split()) == 0:
                logger.info(
                    "📄 Página ignorada (pouco texto): %s p%d",
                    ctx["filename"],
                    page_idx + 1,
                )
                continue

            pix = page.get_pixmap(dpi=ctx["dpi"])  # type: ignore[attr-defined]
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img_cv = np.array(img)

            page_context: DocumentPageContext = {
                "filename": ctx["filename"],
                "page_number": page_idx + 1,
                "page_text": page_text,
                "image_cv": img_cv,
                "client_name": ctx["client_name"],
                "embed_model": ctx["embed_model"],
                "vector_store": ctx["vector_store"],
                "mongo_collection": ctx["mongo_collection"],
                "source_type": ctx.get("source_type", "unknown"),
            }

            if process_pdf_page(page_context):
                processed_pdf = True
        except (ValueError, OSError, cv2.error) as e:
            logger.warning(
                "Erro ao processar página %d de %s: %s",
                page_idx + 1,
                ctx["filename"],
                e,
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning(
                "Erro ao processar página %d de %s: %s",
                page_idx + 1,
                ctx["filename"],
                e,
            )

    doc.close()

    if processed_pdf:
        safe_increment(app_state.metrics, ctx["client_name"], "pdfs_processed")

    logger.info("✅ Processamento finalizado para: %s", ctx["filename"])
    return processed_pdf


def _process_diagram_region(
    context: DocumentPageContext, contour: Any, index: int
) -> bool:
    """
    Processes a diagram region (OpenCV contour) and stores its embedding.

    Args:
        context (DocumentPageContext): Page-level context with image and metadata.
        contour (Any): OpenCV contour data.
        index (int): Bounding box index (e.g. b1, b2...).

    Returns:
        bool: True if embedding was successfully saved, False otherwise.
    """
    _, _, w, h = cv2.boundingRect(contour)
    if w < 100 or h < 100:
        return False

    image_bytes = _generate_diagram_bytes(context, contour)
    name = f"{context['filename']}_p{context['page_number']}_b{index + 1}.png"

    if is_blank_image_from_bytes(image_bytes) or context["mongo_collection"].find_one(
        {"name": name}
    ):
        logger.info(
            "Imagem ignorada (branca ou duplicada): %s (p%d de %s)",
            name,
            context["page_number"],
            context["filename"],
        )

        return False

    context_text = f"{context['page_text']}\n{name}\nPage {context['page_number']} of {context['filename']}"
    embedding = safe_get_embedding(
        context["embed_model"], context_text, identifier=name
    )

    if not embedding:
        logger.warning("Embedding falhou para imagem: %s", name)
        return False

    emb_hash = generate_embedding_hash(embedding)

    if embedding_already_exists(context["vector_store"], emb_hash):
        logger.info("Embedding já existente no ChromaDB: %s", emb_hash)
        return False

    artifact = EmbeddingArtifact(
        name=name,
        context_text=context_text,
        embedding=embedding,
        image_bytes=image_bytes,
        embedding_hash=emb_hash,
    )

    img_meta, chroma_meta = _build_mongo_and_chroma_metadata(context, artifact)

    success = save_image_with_metadata(
        img_meta, context["mongo_collection"], context["client_name"]
    )

    if success:
        add_embedding_to_chroma(context["vector_store"], chroma_meta)
        safe_increment(app_state.metrics, context["client_name"], "embeddings_total")
        safe_increment(app_state.metrics, context["client_name"], "images_saved")

    return success


def _build_mongo_and_chroma_metadata(
    context: DocumentPageContext,
    artifact: EmbeddingArtifact,
) -> tuple[ImageMetadata, ChromaEmbeddingMetadata]:
    """
    Builds metadata entries for MongoDB and ChromaDB from an embedding artifact.

    Args:
        context (DocumentPageContext): Contextual page data.
        artifact (EmbeddingArtifact): Embedding-related content.

    Returns:
        Tuple[ImageMetadata, ChromaEmbeddingMetadata]: Metadata entries for Mongo and Chroma.
    """
    mongo_meta: ImageMetadata = {
        "name": artifact.name,
        "doc": context["filename"],
        "page": context.get("page_number"),
        "page_text": context.get("page_text"),
        "image_bytes": artifact.image_bytes,
        "embedding": artifact.embedding,
        "embedding_hash": artifact.embedding_hash,
        "source_type": context.get("source_type", "pdf"),
        "section": context.get("section_title"),
        "row": context.get("row_index"),
    }

    chroma_meta: ChromaEmbeddingMetadata = {
        "embedding": artifact.embedding,
        "embedding_hash": artifact.embedding_hash,
        "context_text": artifact.context_text,
        "image_name": artifact.name,
        "document_name": context["filename"],
        "page_number": context["page_number"],
        "client_name": context["client_name"],
    }

    return mongo_meta, chroma_meta


def _generate_diagram_bytes(context: DocumentPageContext, contour: Any) -> bytes:
    """
    Renders and crops a region from the PDF page image and returns its byte representation.

    Args:
        context (DocumentPageContext): Page context.
        contour (Any): OpenCV contour.

    Returns:
        bytes: Cropped image in PNG format.
    """
    rect = cv2.boundingRect(contour)
    cropped = context["image_cv"][
        rect[1] : rect[1] + rect[3], rect[0] : rect[0] + rect[2]
    ]
    image_pil = Image.fromarray(cropped)
    buf = io.BytesIO()
    image_pil.save(buf, format="PNG")
    return buf.getvalue()


def _process_textual_embedding(context: DocumentPageContext) -> bool:
    identifier = f"{context['filename']}_p{context['page_number']}_noimage"
    context_text = f"{context['page_text']}\nPage {context['page_number']} of {context['filename']}"

    if not context["page_text"] or len(context["page_text"].split()) == 0:
        logger.warning(
            "⚠️ Texto insuficiente para gerar embedding textual: %s (p%d de %s)",
            identifier,
            context["page_number"],
            context["filename"],
        )
        return False

    try:
        embedding = safe_get_embedding(
            context["embed_model"], context["page_text"], identifier
        )
    except IndexError as e:
        logger.critical(
            "🚨 Erro de indexação ao gerar embedding textual (%s): %s",
            identifier,
            e,
        )
        return False

    if not embedding:
        logger.warning("❌ Falha ao gerar embedding textual: %s", identifier)
        return False

    emb_hash = generate_embedding_hash(embedding)

    if embedding_already_exists(context["vector_store"], emb_hash):
        logger.info("Embedding textual já existe no ChromaDB: %s", emb_hash)
        return False

    chroma_meta: ChromaEmbeddingMetadata = {
        "embedding": embedding,
        "embedding_hash": emb_hash,
        "context_text": context_text,
        "image_name": identifier,
        "document_name": context["filename"],
        "page_number": context["page_number"],
        "client_name": context["client_name"],
    }

    add_embedding_to_chroma(context["vector_store"], chroma_meta)
    safe_increment(app_state.metrics, context["client_name"], "embeddings_total")

    logger.info("✅ Embedding textual salvo: %s", identifier)
    return True
