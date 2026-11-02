"""
Module: helena_bot.utils.mongo.image_store

Manages the persistence of diagram images and their associated embedding metadata
into MongoDB for HelenaBot. This includes all relevant contextual information used
to enable semantic retrieval and deduplication.

The image data is stored in binary format (BSON Binary) along with the original page
text, source document metadata, and the SHA-256 hash of the embedding vector.

Responsibilities:
- Save annotated diagrams and fallback embeddings into MongoDB
- Prevent duplicates by checking for existing hashes
- Structure embedding documents with consistent metadata fields

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import datetime
import logging

from bson import Binary
from helena_bot.embedding_config import EMBEDDING_CONFIG
from helena_bot.utils.types import ImageMetadata
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


def save_image_with_metadata(
    metadata: ImageMetadata, collection: Collection, client_name: str
) -> bool:
    """
    Save a diagram image and its contextual metadata into MongoDB, avoiding duplication.

    This function checks whether the image (based on its unique `name`) already exists.
    If not, it inserts a document containing:
    - Image bytes
    - Page-level context text
    - Vector embedding
    - Embedding hash and version
    - Model metadata
    - Client and document origin

    Args:
        metadata (ImageMetadata): Fully structured embedding payload including image content and context.
        collection (Collection): MongoDB collection where the image will be persisted.

    Returns:
        bool: True if the image was successfully saved; False if it already existed or insertion failed.
    """
    try:
        collection.create_index("name", unique=True)

        if collection.find_one({"name": metadata["name"]}):
            logger.info("[SKIP] Imagem já existe no MongoDB: %s", metadata["name"])
            return False

        document = {
            "client": client_name,
            "name": metadata["name"],
            "source_file": metadata["doc"],
            "source_type": metadata.get(
                "source_type", "unknown"
            ),  # "pdf", "docx", "csv", etc.
            "embedding": metadata["embedding"],
            "embedding_hash": metadata["embedding_hash"],
            "embedding_model": EMBEDDING_CONFIG.model_name,
            "embedding_version": EMBEDDING_CONFIG.version,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "image_bytes": Binary(metadata["image_bytes"]),
            # Campos opcionais conforme o tipo do documento
            "page_number": metadata.get("page"),  # para PDFs
            "section_title": metadata.get("section"),  # para DOCX
            "row_index": metadata.get("row"),  # para CSVs
            "context_text": metadata.get("page_text"),  # texto de apoio contextual
        }

        collection.insert_one(document)
        logger.info("[OK] Imagem salva no MongoDB: %s", metadata["name"])
        return True

    except PyMongoError as e:
        logger.error("Erro ao salvar imagem '%s': %s", metadata["name"], e)
        return False
