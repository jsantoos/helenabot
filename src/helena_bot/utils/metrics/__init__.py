"""
Package: helena_bot.utils.metrics

Manages runtime metric initialization and validation for HelenaBot.

This package provides utilities to ensure metric dictionaries used across the
pipeline are properly structured and initialized, preventing runtime errors
and supporting consistent tracking.

Exposed:
- ensure_global_metrics: Initializes the required keys in `app_state.metrics['global']`.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .has_metric import has_metrics_to_save
from .safe_ops import safe_increment
from .tracking import ensure_global_metrics

__all__ = ["has_metrics_to_save", "ensure_global_metrics", "safe_increment"]
