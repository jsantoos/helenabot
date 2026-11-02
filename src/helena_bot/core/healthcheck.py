"""
Module: helena_bot.core.healthcheck

This module verifies the external availability of the Flask server exposed
via Cloudflare (or other tunnel) and registers the Telegram webhook
using the public endpoint.

Responsibilities:
- Ensure the application is accessible via a public healthcheck URL.
- Register the Telegram bot webhook to receive updates at the exposed endpoint.

Used during system startup in `core/startup.py`.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
import os
import time

import requests

logger = logging.getLogger(__name__)
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")


def test_url(url: str, timeout: int = 10, retries: int = 3) -> bool:
    """
    Verifies if the given URL is reachable via HTTP GET.

    This function attempts to reach the specified URL and considers it accessible
    if any attempt returns HTTP status 200. It performs multiple retries to account
    for startup delays or network latency.

    Args:
        url (str): The URL to test (e.g., `https://xyz.tunnel.cloudflare.com/healthcheck`).
        timeout (int): Maximum duration (in seconds) to wait per request. Defaults to 10.
        retries (int): Number of attempts before giving up. Defaults to 3.

    Returns:
        bool: True if the URL is reachable (status 200), False otherwise.

    Logging:
        - INFO: On successful access.
        - WARNING: On each failed attempt.
    """
    for i in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                logger.info("URL acessível: %s", url)
                return True
        except requests.RequestException as err:
            logger.warning("Tentativa %d/%d falhou: %s", i + 1, retries, err)
        time.sleep(3)
    return False


def configure_webhook(public_url: str) -> None:
    """
    Registers the Telegram webhook using the provided public-facing URL.

    This function constructs the Telegram Bot API `setWebhook` URL using
    the current bot token and attempts to register it. The registration
    is critical to receiving updates from Telegram servers via HTTPS POST.

    Args:
        public_url (str): The externally accessible URL (e.g., Cloudflare tunnel).

    Raises:
        requests.RequestException: If the webhook registration fails due to network issues
        or API errors. The caller is expected to handle this failure.

    Logging:
        - INFO: When the webhook is successfully set.
        - CRITICAL: If registration fails and exception is raised.
    """
    webhook_url = f"{public_url}/{TELEGRAM_TOKEN}"
    telegram_api_url = (
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}"
    )

    try:
        response = requests.get(telegram_api_url, timeout=10)
        response.raise_for_status()
        logger.info("Webhook registrado com sucesso: %s", webhook_url)
    except requests.RequestException as err:
        logger.critical("Falha ao registrar webhook: %s", err)
        raise
