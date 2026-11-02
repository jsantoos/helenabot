"""
Module: helena_bot.core.bot_launcher

Responsible for initializing and starting the Telegram bot for a specific client.

This module delegates the setup process to the `setup_bot` function from
`telegram_handlers.py`, which loads:
- Environment variables for the client
- Embedding models and vector store
- MongoDB collections for embeddings and metrics
- System prompts and memory buffers

This function is intended to be called during the main startup sequence
from the `core.startup` module.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
from typing import Any

from helena_bot.bot import setup_bot

logger = logging.getLogger(__name__)


async def start_client_bot(client_name: str, config: dict[str, Any]) -> None:
    """
    Starts the Telegram bot for a given client using provided configuration.

    This function acts as an orchestrator that prepares the bot's runtime
    environment by calling the `setup_bot()` function with all required
    parameters such as the token, MongoDB URL, document paths, and Groq API key.

    Args:
        client_name (str): Name of the client (used for folder resolution and DB naming).
        config (dict[str, Any]): Client-specific configuration loaded from the clients/ directory.
            Must contain the keys:
                - env: { TELEGRAM_TOKEN, MONGO_URL, GROQ_API_KEY }
                - docs_path: Path to the client document directory.

    Returns:
        None. The bot is started asynchronously and registered in `app_state`.

    Raises:
        KeyError: If required configuration fields are missing.
        RuntimeError: If setup fails at any internal stage.

    Logging:
        - INFO: On successful bot start.
        - ERROR: If startup fails or config is incomplete.
    """
    try:
        logger.info("Iniciando bot para o cliente: %s", client_name)
        await setup_bot(
            client_name=client_name,
            config=config,
        )
    except KeyError as err:
        logger.error(
            "Configuração incompleta para o cliente '%s': %s", client_name, err
        )
        raise
    except Exception as err:
        logger.error("Falha ao iniciar o bot para '%s': %s", client_name, err)
        raise RuntimeError(f"Erro ao inicializar o bot: {err}") from err
