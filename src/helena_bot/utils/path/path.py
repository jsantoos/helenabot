"""
Module: helena_bot.utils.path_utils

Centralized utilities for resolving absolute paths in the HelenaBot project.

This module ensures all file system interactions are based on consistent and
portable paths, avoiding hardcoded or fragile relative references. It provides
functions for locating client-specific resources like `documents`, `system_prompt.txt`,
`.env` files, and ChromaDB persistence folders.

Context:
- Used across ingestion pipelines, bot initialization, testing, and embedding indexing.
- Compatible with both containerized and local environments.

Structure:
- BASE_DIR is resolved relative to the root of the repository.
- CLIENTS_DIR provides a base for all client-specific subdirectories.
- Utility functions return full absolute paths for modular access.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import os
from pathlib import Path

BASE_DIR: str = str(Path(__file__).resolve().parents[4])

# === Main directory paths ===
CLIENTS_DIR: str = os.path.join(BASE_DIR, "clients")
DATA_DIR: str = os.path.join(BASE_DIR, "data")
SCRIPTS_DIR: str = os.path.join(BASE_DIR, "scripts")


def get_documents_dir(client: str) -> str:
    """
    Get the absolute path to the `documents/` folder for a given client.

    Args:
        client (str): The name of the client directory (e.g., 'bible', 'nutri').

    Returns:
        str: Absolute path to the documents directory.
    """
    return os.path.join(CLIENTS_DIR, client, "documents")


def get_chroma_dir(client: str) -> str:
    """
    Get the absolute path to the `chroma_db/` vector store directory for a given client.

    Args:
        client (str): The name of the client directory.

    Returns:
        str: Absolute path to the ChromaDB persistence directory.
    """
    return os.path.join(CLIENTS_DIR, client, "chroma_db")


def get_prompt_path(client: str) -> str:
    """
    Get the absolute path to a client's `.env` file.

    Args:
        client (str): The name of the client directory.

    Returns:
        str: Absolute path to the .env file.
    """
    return os.path.join(CLIENTS_DIR, client, "system_prompt.txt")


def get_env_path(client: str) -> str:
    """
    Returns the full path to a client's .env file.

    Args:
        client (str): The name of the client folder.

    Returns:
        str: Absolute path to .env
    """
    return os.path.join(CLIENTS_DIR, client, ".env")
