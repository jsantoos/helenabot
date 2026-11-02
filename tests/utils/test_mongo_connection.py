"""
tests/utils/test_mongo_connection.py

Unit tests for helena_bot.utils.mongo.connection module.

Validates:
- MongoDB socket availability checks and timeouts
- Robust connection initialization with retries
- Successful and failed MongoDB client connections
- Collection retrieval with and without unique indexing

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from unittest.mock import MagicMock, patch

import pytest
from helena_bot.utils.db.mongo_connection import (
    connect_to_mongo,
    get_collection,
    wait_for_mongo_socket,
)
from pymongo.errors import ServerSelectionTimeoutError

# ==== Tests for wait_for_mongo_socket ====


@patch("socket.create_connection")
def test_wait_for_mongo_socket_success(mock_create_connection: MagicMock) -> None:
    """
    Test that wait_for_mongo_socket returns immediately when the socket is available.
    """
    wait_for_mongo_socket(host="localhost", port=27017, timeout=5)
    mock_create_connection.assert_called()


@patch("socket.create_connection", side_effect=OSError)
def test_wait_for_mongo_socket_timeout(mock_create_connection: MagicMock) -> None:
    """
    Test that wait_for_mongo_socket raises TimeoutError if the socket never becomes available.
    """
    with pytest.raises(TimeoutError):
        wait_for_mongo_socket(host="localhost", port=27017, timeout=2)

    mock_create_connection.assert_called()


# ==== Tests for connect_to_mongo ====


@patch("helena_bot.utils.db.mongo_connection.wait_for_mongo_socket")
@patch("helena_bot.utils.db.mongo_connection.MongoClient")
def test_connect_to_mongo_success(
    mock_mongo_client: MagicMock, mock_wait_socket: MagicMock
) -> None:
    """
    Test that connect_to_mongo succeeds when MongoDB is reachable immediately.
    """
    mock_client_instance = mock_mongo_client.return_value
    mock_client_instance.admin.command.return_value = {"ok": 1.0}

    client = connect_to_mongo(url="mongodb://localhost:27017", retries=2, delay=1)

    mock_mongo_client.assert_called_once()
    mock_client_instance.admin.command.assert_called_once_with("ping")
    mock_wait_socket.assert_called()
    assert client is mock_client_instance


@patch("helena_bot.utils.db.mongo_connection.wait_for_mongo_socket")
@patch(
    "helena_bot.utils.db.mongo_connection.MongoClient",
    side_effect=ServerSelectionTimeoutError("Failed to connect"),
)
def test_connect_to_mongo_failure(
    mock_mongo_client: MagicMock, mock_wait_socket: MagicMock
) -> None:
    """
    Test that connect_to_mongo raises ConnectionError after retrying and failing.
    """
    with pytest.raises(ConnectionError):
        connect_to_mongo(url="mongodb://localhost:27017", retries=2, delay=1)

    mock_wait_socket.assert_called()
    mock_mongo_client.assert_called()


# ==== Tests for get_collection ====


def test_get_collection_with_index() -> None:
    """
    Test that get_collection retrieves a collection and creates a unique index on 'name'.
    """
    mock_client = MagicMock()
    mock_collection = mock_client["test_db"]["test_collection"]

    collection = get_collection(
        mock_client, "test_db", "test_collection", ensure_index=True
    )

    mock_collection.create_index.assert_called_once_with("name", unique=True)
    assert collection == mock_collection


def test_get_collection_without_index() -> None:
    """
    Test that get_collection retrieves a collection without creating an index if disabled.
    """
    mock_client = MagicMock()
    mock_collection = mock_client["test_db"]["test_collection"]

    collection = get_collection(
        mock_client, "test_db", "test_collection", ensure_index=False
    )

    mock_collection.create_index.assert_not_called()
    assert collection == mock_collection
