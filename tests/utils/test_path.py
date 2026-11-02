"""
tests/utils/test_path.py

Unit tests for helena_bot.utils.path.path module.

Validates:
- Path construction for client-specific documents folders
- Path construction for ChromaDB persistence directories
- Retrieval of system prompt file paths
- Retrieval of .env configuration file paths

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import os

import pytest
from helena_bot.utils.path.path import (
    CLIENTS_DIR,
    get_chroma_dir,
    get_documents_dir,
    get_env_path,
    get_prompt_path,
)


@pytest.mark.parametrize("client_name", ["bible", "bio", "nutri", "instituto"])
def test_get_documents_dir(client_name: str) -> None:
    """
    Test if get_documents_dir returns the correct path for a given client.
    """
    expected_path = os.path.join(CLIENTS_DIR, client_name, "documents")
    actual_path = get_documents_dir(client_name)
    assert (
        actual_path == expected_path
    ), f"Expected {expected_path}, but got {actual_path}"


@pytest.mark.parametrize("client_name", ["bible", "bio", "nutri", "instituto"])
def test_get_chroma_dir(client_name: str) -> None:
    """
    Test if get_chroma_dir returns the correct path to chroma_db for a given client.
    """
    expected_path = os.path.join(CLIENTS_DIR, client_name, "chroma_db")
    actual_path = get_chroma_dir(client_name)
    assert (
        actual_path == expected_path
    ), f"Expected {expected_path}, but got {actual_path}"


@pytest.mark.parametrize("client_name", ["bible", "bio", "nutri", "instituto"])
def test_get_prompt_path(client_name: str) -> None:
    """
    Test if get_prompt_path returns the correct path to system_prompt.txt for a given client.
    """
    expected_path = os.path.join(CLIENTS_DIR, client_name, "system_prompt.txt")
    actual_path = get_prompt_path(client_name)
    assert (
        actual_path == expected_path
    ), f"Expected {expected_path}, but got {actual_path}"


@pytest.mark.parametrize("client_name", ["bible", "bio", "nutri", "instituto"])
def test_get_env_path(client_name: str) -> None:
    """
    Test if get_env_path returns the correct path to .env file for a given client.
    """
    expected_path = os.path.join(CLIENTS_DIR, client_name, ".env")
    actual_path = get_env_path(client_name)
    assert (
        actual_path == expected_path
    ), f"Expected {expected_path}, but got {actual_path}"
