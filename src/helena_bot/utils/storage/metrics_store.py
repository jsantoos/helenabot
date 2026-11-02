"""
Module: helena_bot.utils.mongo.metrics_store

Handles the persistence of runtime metrics for HelenaBot into MongoDB.

This module receives in-memory metrics (both global and per-client)
and stores them in a structured format. These metrics enable runtime
monitoring, usage analytics, and long-term performance tracking.

All data is timestamped and converted to serializable formats (e.g., sets → lists).

Responsibilities:
- Transform and persist aggregated metrics into the `helena_metrics` collection
- Ensure metrics are safe for insertion (e.g., no unserializable types like sets)

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import datetime
import logging
from typing import Dict

from pymongo.collection import Collection
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


def save_metrics(metrics: Dict, mongo_collection: Collection) -> None:
    """
    Persist global and per-client runtime metrics to MongoDB.

    The stored document includes:
    - Global metrics (e.g., interactions, messages, embeddings)
    - Per-client breakdown of the same metrics
    - Timestamp for temporal analysis

    Args:
        metrics (Dict): Runtime metrics dictionary with 'global' and 'per_client' keys.
        mongo_collection (Collection): Target MongoDB collection for inserting the metrics.

    Returns:
        None
    """
    try:
        metrics_copy = {
            "global": dict(metrics.get("global", {})),
            "per_client": {},
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
        }
        metrics_copy["global"]["connected_users"] = list(
            metrics_copy["global"].get("connected_users", set())
        )
        for client, data in metrics.get("per_client", {}).items():
            metrics_copy["per_client"][client] = dict(data)
            metrics_copy["per_client"][client]["connected_users"] = list(
                data.get("connected_users", set())
            )

        result = mongo_collection.insert_one(metrics_copy)
        logger.info("✅ Métricas salvas com sucesso. ID: %s", result.inserted_id)
    except (PyMongoError, IOError, TypeError) as e:
        logger.error("Erro ao salvar métricas: %s", e)


def ensure_client_metrics(client_name: str, metrics: Dict) -> None:
    """
    Ensure that all required metric keys exist for a specific client.

    This function initializes the expected metrics dictionary for a client if it doesn't exist yet,
    ensuring consistency across indexing and runtime metric collection.

    Args:
        client_name (str): Logical name of the client.
        metrics (Dict): Top-level runtime metrics dictionary (contains 'per_client').

    Returns:
        None
    """
    default = {
        "connected_users": set(),
        "messages_sent": 0,
        "images_sent": 0,
        "interactions": 0,
        "embeddings_total": 0,
        "images_saved": 0,
        "pdfs_processed": 0,
    }
    metrics.setdefault("per_client", {}).setdefault(client_name, default.copy())
