"""
Package: helena_bot.utils.path

Provides centralized access to key filesystem paths used across HelenaBot.

This package abstracts the logic for resolving absolute paths to client-specific
resources such as ChromaDB folders, prompt templates, document roots, and .env files.
By avoiding hardcoded strings and fragile relative references, it promotes portability
and maintainability across modules and environments.

Exposed:
- get_chroma_dir: Returns the path to a client's ChromaDB vector directory.
- get_documents_dir: Returns the path to a client's document folder.
- get_env_path: Returns the path to a client's .env file.
- get_prompt_path: Returns the path to a client's system prompt file.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .path import get_chroma_dir, get_documents_dir, get_env_path, get_prompt_path

__all__ = ["get_chroma_dir", "get_documents_dir", "get_prompt_path", "get_env_path"]
