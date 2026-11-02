"""
Module: helena_bot.utils.metrics.has_metric

Provides utilities to check the existence of runtime metrics
before persisting them to MongoDB.

This utility ensures that unnecessary database writes are avoided
when no meaningful metrics have been collected yet.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import Dict


def has_metrics_to_save(metrics: Dict) -> bool:
    """
    Determine if there are runtime metrics available to persist.

    This function checks if either the 'global' or 'per_client' sections
    of the runtime metrics structure are non-empty. It helps prevent
    unnecessary database writes when no metrics have been accumulated yet.

    Args:
        metrics (Dict): Dictionary containing runtime metrics, typically from app_state.metrics.
            Expected structure:
                {
                    "global": {...},
                    "per_client": {...}
                }

    Returns:
        bool: True if there are metrics (global or per-client) to persist; False otherwise.
    """
    return bool(metrics.get("global") or metrics.get("per_client"))
