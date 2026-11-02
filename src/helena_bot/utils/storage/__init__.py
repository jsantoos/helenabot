"""
Package: helena_bot.utils.storage

Provides modularized access to MongoDB operations used across the HelenaBot system.

This package is split into isolated modules by domain:
- `connection`: Establishes MongoDB connections and returns collections with optional indexing.
- `image_store`: Handles storage of diagram images and embedding metadata.
- `interaction_log`: Manages chat history for context retention and auditing.
- `metrics_store`: Persists runtime performance and usage metrics.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints

Usage example:

    from helena_bot.utils.mongo import (
        connect_to_mongo,
        get_collection,
        save_image_with_metadata,
        save_interaction,
        get_last_interactions,
        save_metrics,
    )
"""

from .image_store import save_image_with_metadata
from .interaction_log import get_last_interactions, save_interaction
from .metrics_store import ensure_client_metrics, save_metrics

__all__ = [
    "ensure_client_metrics",
    "get_last_interactions",
    "save_interaction",
    "save_metrics",
    "save_image_with_metadata",
]
