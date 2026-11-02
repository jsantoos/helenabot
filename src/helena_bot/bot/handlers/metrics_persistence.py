"""
Module: helena_bot.bot.handlers.metrics_persistence

Provides shared utilities for persisting runtime metrics into MongoDB
across different Telegram handlers (messages, voice, commands).

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging

from helena_bot import app_state
from helena_bot.utils.metrics import has_metrics_to_save
from helena_bot.utils.storage import save_metrics
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


def _persist_metrics_if_available(client_data: dict, client_name: str) -> None:
    """
    Saves global and per-client runtime metrics to MongoDB if the client
    has a configured metrics collection.

    Args:
        client_data (dict): Dictionary containing client session metadata.
        client_name (str): Name of the client (for fallback logging).

    Returns:
        None
    """

    metrics_collection = client_data.get("metrics_collection")
    logger.warning("Persistindo métricas: %s", metrics_collection)

    if metrics_collection is None:
        logger.warning("Nenhuma metrics_collection encontrada para %s", client_name)
        return

    if not has_metrics_to_save(app_state.metrics):
        logger.info(
            "Nenhuma métrica gerada ainda para %s; não haverá persistência.",
            client_name,
        )
        return

    logger.info("⏺ Persistindo métricas após interação (cliente: %s)", client_name)

    try:
        save_metrics(app_state.metrics, metrics_collection)
    except (PyMongoError, IOError, TypeError) as e:
        logger.error("❌ Erro ao salvar métricas para %s: %s", client_name, e)

    logger.info("✅ Tentativa de salvamento de métricas executada para %s", client_name)
    return
