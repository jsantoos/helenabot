"""
tests/conftest.py

Global fixtures for HelenaBot unit tests.

Provides reusable fixtures for PDF contexts, Mongo simulation,
embedding mocks, and external service mocks.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from unittest.mock import MagicMock

import numpy as np
import pytest

# === Basic fixtures ===


@pytest.fixture
def sample_client_name() -> str:
    """
    Provide a sample client name.
    """
    return "bible"


@pytest.fixture
def fake_mongo_url() -> str:
    """
    Provide a fake MongoDB URL.
    """
    return "mongodb://localhost:27018"


@pytest.fixture
def fake_indexing_context() -> dict:
    """
    Provide a fake PDFIndexingContext for pipeline tests.
    """
    return {
        "client_name": "test_client",
        "documents_path": "fake/documents",
        "embed_model": MagicMock(),
        "vector_store": MagicMock(),
        "mongo_collection": MagicMock(),
        "dpi": 300,
        "max_pages": 10,
    }


@pytest.fixture
def fake_pdf_document_context(mocker) -> dict:
    """
    Provide a sample PdfDocumentContext with mock Fitz document.
    """
    document_mock = MagicMock()
    document_mock.__len__.return_value = 1
    page_mock = MagicMock()
    page_mock.get_text.return_value = "Sample text for embedding."
    page_mock.get_pixmap.return_value = MagicMock(
        width=100, height=100, samples=b"fake"
    )
    document_mock.__getitem__.return_value = page_mock
    document_mock.close.return_value = None

    mocker.patch(
        "helena_bot.pipeline.image_embedding.fitz.open", return_value=document_mock
    )

    return {
        "filename": "test_document.pdf",
        "client_name": "test_client",
        "embed_model": MagicMock(),
        "vector_store": MagicMock(),
        "mongo_collection": MagicMock(),
        "pdf_folder": "fake/documents",
        "dpi": 200,
        "max_pages": 5,
    }


@pytest.fixture
def fake_pdf_page_context() -> dict:
    """
    Provide a sample PdfPageContext for page-level processing tests.
    """
    return {
        "filename": "test_document.pdf",
        "page_number": 1,
        "page_text": "This is a page text with enough words for embedding generation.",
        "image_cv": np.ones((500, 500, 3), dtype=np.uint8),
        "client_name": "test_client",
        "embed_model": MagicMock(),
        "vector_store": MagicMock(),
        "mongo_collection": MagicMock(),
    }


# === Mocks for pipeline dependencies ===


@pytest.fixture
def mock_safe_get_embedding(mocker):
    """
    Mock safe_get_embedding always returning a sample embedding.
    """
    return mocker.patch(
        "helena_bot.pipeline.image_embedding.safe_get_embedding",
        return_value=[0.1, 0.2, 0.3],
    )


@pytest.fixture
def mock_save_image_with_metadata(mocker):
    """
    Mock save_image_with_metadata always succeeding.
    """
    return mocker.patch(
        "helena_bot.pipeline.image_embedding.save_image_with_metadata",
        return_value=True,
    )


@pytest.fixture
def mock_is_blank_image_from_bytes(mocker):
    """
    Mock is_blank_image_from_bytes always returning False.
    """
    return mocker.patch(
        "helena_bot.pipeline.image_embedding.is_blank_image_from_bytes",
        return_value=False,
    )


@pytest.fixture
def mock_add_embedding_to_chroma(mocker):
    """
    Mock add_embedding_to_chroma as noop.
    """
    return mocker.patch("helena_bot.pipeline.image_embedding.add_embedding_to_chroma")


@pytest.fixture
def mock_embedding_already_exists(mocker):
    """
    Mock embedding_already_exists always returning False.
    """
    return mocker.patch(
        "helena_bot.pipeline.image_embedding.embedding_already_exists",
        return_value=False,
    )


@pytest.fixture
def mock_fitz_open(mocker):
    """
    Mock fitz.open for tests that simulate errors.
    """
    return mocker.patch("helena_bot.pipeline.image_embedding.fitz.open")
