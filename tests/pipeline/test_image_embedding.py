"""
tests/pipeline/test_image_embedding.py

Unit tests for helena_bot.pipeline.image_embedding module.

Validates:
- Full document processing and page iteration
- Diagram extraction and embedding generation
- Textual embedding fallback and deduplication
- Metadata creation for MongoDB and ChromaDB
- Handling of blank images, small diagrams, and errors

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from unittest.mock import MagicMock

import numpy as np
from helena_bot.pipeline.image_embedding import (
    _build_mongo_and_chroma_metadata,
    _generate_diagram_bytes,
    _process_diagram_region,
    _process_textual_embedding,
    process_pdf_document,
    process_pdf_page,
)


def test_process_pdf_document_success(
    fake_pdf_document_context,
    mocker,
) -> None:
    """
    Test processing a PDF document successfully.
    """
    # Mocka process_pdf_page
    mock_process_pdf_page = mocker.patch(
        "helena_bot.pipeline.image_embedding.process_pdf_page",
        return_value=True,
        autospec=True,
    )

    # Mocka fitz.open
    mock_fitz_open = mocker.patch("helena_bot.pipeline.image_embedding.fitz.open")
    fake_doc = MagicMock()
    fake_doc.__len__.return_value = 1
    fake_page = MagicMock()

    # ❗ Corrige para texto longo suficiente (mínimo 10 palavras)
    fake_page.get_text.return_value = (
        "This is a simulated text with enough words to pass the minimum word "
        "requirement for processing the page."
    )

    fake_pixmap = MagicMock()
    fake_pixmap.width = 100
    fake_pixmap.height = 100
    fake_img = np.ones((100, 100, 3), dtype=np.uint8)
    fake_pixmap.samples = fake_img.tobytes()
    fake_page.get_pixmap.return_value = fake_pixmap
    fake_doc.__getitem__.return_value = fake_page
    fake_doc.close.return_value = None
    mock_fitz_open.return_value = fake_doc

    # Mocka Image.frombytes
    mocker.patch(
        "helena_bot.pipeline.image_embedding.Image.frombytes",
        return_value=fake_img,
    )

    # Mocka safe_increment
    mocker.patch("helena_bot.pipeline.image_embedding.safe_increment")

    result = process_pdf_document(fake_pdf_document_context)

    assert result is True
    mock_process_pdf_page.assert_called_once()


def test_process_pdf_document_handles_page_errors(
    fake_pdf_document_context,
    mock_fitz_open,
) -> None:
    """
    Test that processing continues even if a page causes an error.
    """
    mock_fitz_open.return_value.__getitem__.side_effect = ValueError("Simulated error")
    result = process_pdf_document(fake_pdf_document_context)
    assert result is False


def test_process_pdf_page_with_contours(
    fake_pdf_page_context,
    mock_safe_get_embedding,
    mock_save_image_with_metadata,
    mock_is_blank_image_from_bytes,
    mock_embedding_already_exists,
    mock_add_embedding_to_chroma,
    mocker,
) -> None:
    """
    Test extracting diagram embeddings when contours are found.
    """
    mocker.patch(
        "helena_bot.pipeline.image_embedding.cv2.findContours",
        return_value=(
            [np.array([[[10, 10]], [[10, 400]], [[400, 400]], [[400, 10]]])],
            None,
        ),
    )
    result = process_pdf_page(fake_pdf_page_context)
    assert result is True


def test_process_pdf_page_fallbacks_to_text_embedding(
    fake_pdf_page_context,
    mock_safe_get_embedding,
    mock_add_embedding_to_chroma,
    mock_embedding_already_exists,
    mocker,
) -> None:
    """
    Test falling back to textual embedding when no diagrams are extracted.
    """
    mocker.patch(
        "helena_bot.pipeline.image_embedding.cv2.findContours",
        return_value=([], None),
    )
    result = process_pdf_page(fake_pdf_page_context)
    assert result is True


def test_process_diagram_region_success(
    fake_pdf_page_context,
    mock_is_blank_image_from_bytes,
    mock_safe_get_embedding,
    mock_embedding_already_exists,
    mock_save_image_with_metadata,
    mock_add_embedding_to_chroma,
) -> None:
    """
    Test saving a diagram embedding successfully.
    """
    contour = np.array([[[10, 10]], [[10, 300]], [[300, 300]], [[300, 10]]])

    # Configura os retornos esperados dos mocks
    mock_is_blank_image_from_bytes.return_value = False
    mock_safe_get_embedding.return_value = [0.1, 0.2, 0.3]
    mock_embedding_already_exists.return_value = False
    mock_save_image_with_metadata.return_value = True

    # 👇 IMPORTANTE! Configura o find_one para retornar None
    fake_pdf_page_context["mongo_collection"].find_one.return_value = None

    result = _process_diagram_region(fake_pdf_page_context, contour, index=0)

    assert result is True

    mock_is_blank_image_from_bytes.assert_called()
    mock_safe_get_embedding.assert_called()
    mock_embedding_already_exists.assert_called()
    mock_save_image_with_metadata.assert_called()
    mock_add_embedding_to_chroma.assert_called()


def test_generate_diagram_bytes_returns_png(
    fake_pdf_page_context,
) -> None:
    """
    Test that diagram bytes are returned as PNG format.
    """
    contour = np.array(
        [[[0, 0]], [[0, 50]], [[50, 50]], [[50, 0]]]
    )  # Forma fechada (quadrado)

    result = _generate_diagram_bytes(fake_pdf_page_context, contour)

    assert isinstance(result, bytes)
    assert result.startswith(b"\x89PNG")


def test_build_mongo_and_chroma_metadata_structure(
    fake_pdf_page_context,
) -> None:
    """
    Test that metadata dictionaries are structured correctly.
    """
    artifact = MagicMock()
    artifact.name = "test_image.png"
    artifact.context_text = "Test context"
    artifact.embedding = [0.1, 0.2, 0.3]
    artifact.embedding_hash = "abc123"
    artifact.image_bytes = b"bytes"

    mongo_meta, chroma_meta = _build_mongo_and_chroma_metadata(
        fake_pdf_page_context, artifact
    )
    assert mongo_meta["name"] == "test_image.png"
    assert chroma_meta["embedding_hash"] == "abc123"


def test_process_textual_embedding_success(
    fake_pdf_page_context,
    mock_safe_get_embedding,
    mock_add_embedding_to_chroma,
    mock_embedding_already_exists,
) -> None:
    """
    Test saving a fallback textual embedding successfully.
    """
    result = _process_textual_embedding(fake_pdf_page_context)
    assert result is True


def test_process_textual_embedding_avoids_duplicates(
    fake_pdf_page_context,
    mock_safe_get_embedding,
    mock_embedding_already_exists,
) -> None:
    """
    Test that duplicate textual embeddings are avoided.
    """
    mock_embedding_already_exists.return_value = True
    result = _process_textual_embedding(fake_pdf_page_context)
    assert result is False
