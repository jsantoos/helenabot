"""
Module: helena_bot.utils.metrics.tracking

Initializes and maintains runtime metric structures used across HelenaBot.

This module ensures that the global metric dictionary (`app_state.metrics["global"]`)
contains all required keys with appropriate default values. It prevents runtime
KeyError issues when metrics are incremented throughout the system.

Exposed:
- ensure_global_metrics: Initializes global metrics if not already present.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from helena_bot import app_state


def ensure_global_metrics() -> None:
    """
    Ensure the global metrics dictionary contains all required fields.

    This function sets default values for the global metrics if not already
    present. It is typically called at the beginning of the embedding pipeline
    or startup routine to ensure consistency.

    Global fields initialized:
    - connected_users: set()
    - messages_sent: int
    - images_sent: int
    - interactions: int
    - embeddings_total: int
    - images_saved: int
    - pdfs_processed: int

    Returns:
        None
    """
    required_fields = [
        "connected_users",
        "messages_sent",
        "images_sent",
        "interactions",
        "embeddings_total",
        "images_saved",
        "pdfs_processed",
    ]
    app_state.metrics.setdefault("global", {})
    for field in required_fields:
        if field == "connected_users":
            app_state.metrics["global"].setdefault(field, set())
        else:
            app_state.metrics["global"].setdefault(field, 0)
