"""
Module: helena_bot.utils.mongo.connection

Establishes and manages MongoDB connections for HelenaBot.

This module provides reusable utilities to:
- Wait for the MongoDB socket to become available (e.g., during container startup)
- Establish a connection to the MongoDB server with retry logic
- Retrieve a named collection, optionally ensuring unique indexing

It is used across all components of the system that require direct access to
MongoDB collections, including image storage, interaction logs, and metrics.

Responsibilities:
- Safe and retryable MongoDB connection initialization
- Centralization of socket probing for service readiness
- Abstracted collection retrieval with optional index enforcement

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
import os
import socket
import time
from typing import Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")


def wait_for_mongo_socket(
    host: str = "localhost", port: int = 27017, timeout: int = 30
) -> None:
    """
    Wait until the MongoDB server's socket is available.

    This function is typically used during container startup or testing environments
    to block execution until MongoDB is ready to accept connections.

    Args:
        host (str): MongoDB hostname or IP address.
        port (int): MongoDB port (default is 27017).
        timeout (int): Max time to wait in seconds before raising a TimeoutError.

    Raises:
        TimeoutError: If the socket does not open within the specified timeout.
    """
    start = time.time()
    logger.debug("⏳ Aguardando MongoDB em %s:%d...", host, port)
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info("✅ Porta do MongoDB está aberta.")
                return
        except OSError:
            time.sleep(1)
    raise TimeoutError("A porta do MongoDB não está acessível após esperar.")


def connect_to_mongo(
    url: Optional[str] = None, retries: int = 10, delay: int = 3
) -> MongoClient:
    """
    Establish a MongoDB connection with retry logic and socket readiness check.

    This function pings the server after connection to ensure it's responsive.
    If connection fails, it will retry up to the specified number of attempts.

    Args:
        url (Optional[str]): MongoDB URI. Defaults to MONGO_URL from .env or fallback.
        retries (int): Number of retry attempts before failure.
        delay (int): Delay in seconds between retries.

    Returns:
        MongoClient: A connected PyMongo client instance.

    Raises:
        ConnectionError: If unable to connect after all attempts.
    """
    url = url or MONGO_URL
    for attempt in range(1, retries + 1):
        try:
            wait_for_mongo_socket("mongodb", 27017)
            client = MongoClient(url, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            logger.info("✅ Conectado ao MongoDB (%s) na tentativa %d", url, attempt)
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning("❌ Tentativa %d/%d falhou: %s", attempt, retries, e)
            time.sleep(delay)
    raise ConnectionError(f"MongoDB não acessível após {retries} tentativas.")


def get_collection(
    client: MongoClient, db_name: str, collection_name: str, ensure_index: bool = True
) -> Collection:
    """
    Retrieve a MongoDB collection from a connected client, optionally creating an index on `name`.

    This utility provides a standard way to retrieve collections with enforced indexing
    across HelenaBot modules that require deduplication based on object names.

    Args:
        client (MongoClient): A valid MongoDB client instance.
        db_name (str): Name of the target database.
        collection_name (str): Name of the collection to retrieve.
        ensure_index (bool): Whether to enforce a unique index on the `name` field (default: True).

    Returns:
        Collection: A MongoDB collection object ready for use.
    """
    collection = client[db_name][collection_name]
    if ensure_index:
        collection.create_index("name", unique=True)
    return collection
