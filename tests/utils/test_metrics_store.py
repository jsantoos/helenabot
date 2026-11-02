"""
Tests for helena_bot.utils.mongo.metrics_store module.

Validates:
- Successful persistence of runtime metrics to MongoDB
- Error handling during metric persistence
- Initialization and protection of per-client metric structures

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from unittest.mock import MagicMock, patch

import pytest
from helena_bot.utils.storage.metrics_store import save_metrics, ensure_client_metrics
from pymongo.errors import PyMongoError


# ==== Tests for save_metrics ==== #

def test_save_metrics_successful() -> None:
    """Test that save_metrics correctly serializes sets and inserts into MongoDB."""
    mock_collection = MagicMock()
    metrics = {
        "global": {"connected_users": {"user1", "user2"}, "messages_sent": 10},
        "per_client": {
            "client1": {"connected_users": {"user3"}, "messages_sent": 5}
        },
    }

    save_metrics(metrics, mock_collection)

    assert mock_collection.insert_one.called
    inserted_doc = mock_collection.insert_one.call_args[0][0]
    assert isinstance(inserted_doc["global"]["connected_users"], list)
    assert isinstance(inserted_doc["per_client"]["client1"]["connected_users"], list)


@patch("helena_bot.utils.storage.metrics_store.logger")
def test_save_metrics_handles_pymongo_error(mock_logger: MagicMock) -> None:
    """Test that save_metrics logs errors without raising when MongoDB insertion fails."""
    mock_collection = MagicMock()
    mock_collection.insert_one.side_effect = PyMongoError("Insertion error")

    metrics = {"global": {}, "per_client": {}}

    save_metrics(metrics, mock_collection)

    mock_logger.error.assert_called()


# ==== Tests for ensure_client_metrics ==== #

def test_ensure_client_metrics_creates_default() -> None:
    """Test that ensure_client_metrics initializes metrics for a new client."""
    metrics = {"per_client": {}}

    ensure_client_metrics("new_client", metrics)

    assert "new_client" in metrics["per_client"]
    assert "messages_sent" in metrics["per_client"]["new_client"]
    assert metrics["per_client"]["new_client"]["messages_sent"] == 0


def test_ensure_client_metrics_does_not_overwrite_existing() -> None:
    """Test that ensure_client_metrics does not overwrite metrics for existing clients."""
    metrics = {"per_client": {"existing_client": {"messages_sent": 42}}}

    ensure_client_metrics("existing_client", metrics)

    assert metrics["per_client"]["existing_client"]["messages_sent"] == 42
