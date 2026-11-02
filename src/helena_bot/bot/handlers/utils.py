"""
Module: helena_bot.bot.handlers.utils

Utility functions for token resolution and metrics management.

This module provides low-level helpers for:
- Resolving the bot token from context or update
- Updating global and per-client metrics

These functions are used by message and voice handlers for session tracking.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging

from helena_bot import app_state
from helena_bot.utils.metrics import safe_increment

logger = logging.getLogger(__name__)


def _resolve_token(context, update) -> str | None:
    """
    Resolves the Telegram bot token from either the context or the update.

    This is used to identify which bot instance is handling the current request.
    Works with both `context.bot` and `update.get_bot()` depending on execution scope.

    Args:
        context: Telegram context object provided by the handler.
        update: Telegram update object containing the message or event.

    Returns:
        str | None: The bot token if found, otherwise None.
    """
    if context.bot and getattr(context.bot, "token", None):
        return context.bot.token
    if callable(getattr(update, "get_bot", None)):
        bot = update.get_bot()
        if bot and getattr(bot, "token", None):
            return bot.token
    return None


def _update_basic_metrics(chat_id: int, client_name: str | None) -> None:
    """
    Updates global and per-client metrics for the current interaction.

    This function is called whenever a new user message or voice input is received,
    allowing metrics to track:
    - Number of interactions
    - Unique connected users
    - Activity per client

    Args:
        chat_id (int): Telegram chat ID of the user.
        client_name (Optional[str]): Client identifier for scoped metrics. Can be None.
    """
    app_state.metrics.setdefault("global", {}).setdefault("connected_users", set()).add(
        chat_id
    )
    safe_increment(app_state.metrics, client_name, "interactions")

    if client_name:
        client_metrics = app_state.metrics["per_client"].setdefault(client_name, {})
        client_metrics.setdefault("connected_users", set()).add(chat_id)

    app_state.interaction_counter += 1
