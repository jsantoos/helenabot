"""
Module: helena_bot.core.startup

Entry point for launching the HelenaBot system.

This module orchestrates the entire startup routine:
- Loads environment variables via `.env`
- Initializes and starts the Flask server in a background thread
- Waits for the Cloudflare tunnel to expose a public URL
- Validates tunnel accessibility via healthcheck endpoint
- Registers the Telegram webhook with the exposed URL
- Initializes the bot for the specified client based on the `CLIENT_NAME` environment variable

The system relies on proper initialization of the client-specific configurations
in the `clients/` folder and requires valid tokens and keys in the environment.

Typical execution:
    python core/startup.py

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import asyncio
import logging
import os
import sys
import threading
import time

from clients import load_all_clients
from dotenv import load_dotenv
from helena_bot.logging_config import setup_logging

from .bot_launcher import start_client_bot
from .cloudflare import read_tunnel_url
from .flask_server import app
from .healthcheck import configure_webhook, test_url
from .webhook import register_webhook_route

logger = logging.getLogger(__name__)


def start_flask_server(port: int) -> None:
    """
    Starts the Flask application on a separate thread.

    Args:
        port (int): Port number to bind the Flask app to (default: 5001)

    Note:
        The Flask app runs in `threading.Thread(daemon=True)` to avoid blocking
        the main coroutine loop for Cloudflare and bot startup.
    """
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


async def main() -> None:
    """
    Main asynchronous startup routine for HelenaBot.

    Responsibilities:
    - Fetches `CLIENT_NAME` from environment.
    - Loads client configuration from `clients/` package.
    - Starts the Telegram bot setup routine.
    - Waits indefinitely after successful setup (via `asyncio.Event()`).

    Raises:
        EnvironmentError: If `CLIENT_NAME` is not defined.
        ValueError: If the specified client is not found.
    """
    client_name = os.environ.get("CLIENT_NAME")
    if not client_name:
        logger.error("Variável de ambiente CLIENT_NAME não está definida.")
        return

    clients = load_all_clients()
    config = clients.get(client_name)

    if not config:
        logger.error("Cliente '%s' não encontrado em clients/.", client_name)
        logger.info("🔍 Clientes disponíveis:")
        for name in clients:
            print(f"  - {name}")
        return

    logger.info("Iniciando bot para cliente: %s", client_name)
    await start_client_bot(client_name, config)
    await asyncio.Event().wait()


if __name__ == "__main__":
    setup_logging()
    # Load .env configuration
    dotenv_path = os.getenv("DOTENV_CONFIG_PATH", ".env")
    load_dotenv(dotenv_path)

    # Extract port and setup Flask routes
    port_number = int(os.getenv("PORT", "5001"))
    register_webhook_route(app)

    # Start Flask server in background
    threading.Thread(
        target=start_flask_server, args=(port_number,), daemon=True
    ).start()
    time.sleep(5)  # Wait for Flask to be up

    try:
        logger.info("Lendo URL do túnel Cloudflare...")
        public_url = read_tunnel_url()
        if not public_url:
            logger.critical("Não foi possível obter a URL do túnel.")
            sys.exit(1)

        if not test_url(f"{public_url}/healthcheck"):
            logger.critical("Healthcheck falhou: %s", public_url)
            sys.exit(1)

        configure_webhook(public_url)
        logger.info("Webhook configurado com sucesso.")

        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Interrompido manualmente.")
