"""
tests/pipeline/test_controller.py

Unit tests for helena_bot.pipeline.controller module.

Validates:
- Filtering and processing of PDF files
- Safe handling of processing errors
- Metric initialization and persistence
- Proper function call orchestration

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from unittest.mock import MagicMock, patch

import pytest
from helena_bot import app_state
from helena_bot.pipeline.controller import render_and_index_pdfs


@patch("helena_bot.pipeline.controller.process_pdf_document")
@patch("helena_bot.pipeline.controller.os.listdir")
@patch("helena_bot.pipeline.controller.save_metrics")
def test_only_pdfs_are_processed(
    mock_save_metrics: MagicMock,
    mock_listdir: MagicMock,
    mock_process_pdf_document: MagicMock,
    fake_indexing_context: dict,
) -> None:
    """
    Test that only files with a .pdf extension are processed.

    Ensures non-PDF files are ignored during the ingestion pipeline.
    """
    mock_listdir.return_value = ["doc1.pdf", "doc2.PDF", "image.png", "notes.txt"]

    render_and_index_pdfs(fake_indexing_context)

    assert mock_process_pdf_document.call_count == 2
    calls = [
        call_args[0][0]["filename"]
        for call_args in mock_process_pdf_document.call_args_list
    ]
    assert "doc1.pdf" in calls
    assert "doc2.PDF" in calls
    mock_save_metrics.assert_called_once()


@patch(
    "helena_bot.pipeline.controller.process_pdf_document",
    side_effect=Exception("Mock processing failure"),
)
@patch("helena_bot.pipeline.controller.os.listdir")
@patch("helena_bot.pipeline.controller.save_metrics")
def test_processing_exceptions_are_handled(
    mock_save_metrics: MagicMock,
    mock_listdir: MagicMock,
    mock_process_pdf_document: MagicMock,
    fake_indexing_context: dict,
) -> None:
    """
    Test that the ingestion pipeline continues even if a PDF processing raises an exception.
    """
    mock_listdir.return_value = ["error_doc.pdf"]

    render_and_index_pdfs(fake_indexing_context)

    mock_process_pdf_document.assert_called_once()
    mock_save_metrics.assert_called_once()


@patch("helena_bot.pipeline.controller.process_pdf_document")
@patch("helena_bot.pipeline.controller.os.listdir")
@patch("helena_bot.pipeline.controller.save_metrics")
def test_save_metrics_called_after_processing(
    mock_save_metrics: MagicMock,
    mock_listdir: MagicMock,
    mock_process_pdf_document: MagicMock,
    fake_indexing_context: dict,
) -> None:
    """
    Test that save_metrics is called after processing all documents.

    Ensures metrics are persisted even if no exceptions occur.
    """
    mock_listdir.return_value = ["doc1.pdf"]

    render_and_index_pdfs(fake_indexing_context)

    mock_process_pdf_document.assert_called()
    mock_save_metrics.assert_called_once()


@patch("helena_bot.pipeline.controller.process_pdf_document")
@patch("helena_bot.pipeline.controller.os.listdir")
@patch("helena_bot.pipeline.controller.save_metrics")
def test_metrics_initialized_if_not_exists(
    mock_save_metrics: MagicMock,
    mock_listdir: MagicMock,
    mock_process_pdf_document: MagicMock,
    fake_indexing_context: dict,
) -> None:
    """
    Test that a default metrics structure is initialized if the client does not already exist.
    """
    app_state.metrics["per_client"].pop("test_client", None)

    mock_listdir.return_value = ["doc1.pdf"]

    render_and_index_pdfs(fake_indexing_context)

    assert "test_client" in app_state.metrics["per_client"]
    mock_process_pdf_document.assert_called()
    mock_save_metrics.assert_called_once()


@pytest.mark.usefixtures("caplog")
@patch("helena_bot.pipeline.controller.process_pdf_document")
@patch("helena_bot.pipeline.controller.os.listdir")
@patch("helena_bot.pipeline.controller.save_metrics")
def test_logs_start_and_end_of_processing(
    mock_save_metrics: MagicMock,
    mock_listdir: MagicMock,
    mock_process_pdf_document: MagicMock,
    fake_indexing_context: dict,
    caplog,
) -> None:
    """
    Test that the ingestion pipeline logs both the start and end of processing for a client.
    """
    mock_listdir.return_value = ["doc1.pdf"]

    with caplog.at_level("INFO"):
        render_and_index_pdfs(fake_indexing_context)

    assert any(
        "Iniciando processamento de PDFs" in message for message in caplog.messages
    )
    assert any(
        "Finalizado o processamento dos PDFs" in message for message in caplog.messages
    )

    mock_process_pdf_document.assert_called()
    mock_save_metrics.assert_called_once()
