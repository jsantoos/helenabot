"""
Module: helena_bot.utils.types.mongo_types

Defines structured and strongly-typed data schemas for MongoDB persistence within
the HelenaBot architecture. These types enable clear contracts between subsystems
involving image embedding storage and user interaction tracking.

This module introduces:
- `ImageMetadata`: Captures all information needed to persist an image and its
  embedding vector, extracted from client PDFs or rendered visual sources.
- `InteractionData`: Represents the minimal unit of user interaction (Q&A) stored
  for context reconstruction, analytics, or memory augmentation.

Context:
- Used by `utils.mongo_utils.save_image_with_metadata` and
  `utils.mongo_utils.save_interaction`.
- Enables safe, predictable integration across components such as:
    • `embedding_pipeline`
    • `telegram_handlers`
    • `vector_store`
    • `app_state` metrics logic

Structure:
- Fields in `ImageMetadata` include image bytes, page text, and model metadata.
- Fields in `InteractionData` capture the user query and assistant response pair.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import List, TypedDict


class ImageMetadata(TypedDict, total=False):
    """
    Flexible metadata structure for images embedded from various document types.

    Attributes:
        name (str): Unique name or identifier of the image.
        doc (str): Source filename.
        page (int, optional): Page number, if applicable (e.g., PDFs).
        section (str, optional): Named section or header (e.g., DOCX heading).
        row (int, optional): Row index if from a table or CSV.
        page_text (str, optional): Full text context of the image.
        image_bytes (bytes): Binary representation of the image (e.g., PNG).
        embedding (List[float]): Vector embedding for retrieval.
        embedding_hash (str): Unique hash of the embedding to detect duplicates.
        source_type (str): Type of document (e.g., "pdf", "docx", "csv").
    """

    name: str
    doc: str
    image_bytes: bytes
    embedding: List[float]
    embedding_hash: str
    source_type: str

    # Optional fields depending on document type
    page: int
    section: str
    row: int
    page_text: str


class InteractionData(TypedDict):
    """
    Represents a user interaction for logging into MongoDB.

    Attributes:
        token (str): Telegram bot token identifying the client.
        chat_id (int): Unique Telegram chat ID.
        question (str): User question or message text.
        answer (str): Bot-generated response to the user.
    """

    token: str
    chat_id: int
    question: str
    answer: str
