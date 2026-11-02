"""
Module: helena_bot.core.webhook

Registers the Telegram webhook endpoint and routes incoming updates to the
appropriate handlers for a specific HelenaBot client.

This module dynamically registers a webhook route for each Telegram bot token.
When an incoming HTTP POST request is received at `/<token>`, the system verifies
the token, loads the corresponding bot and embedding context, and dispatches
the update to the appropriate asynchronous handler (`handle_message` or `handle_voice`).

Expected Request Flow:
    Telegram sends update -> Flask app receives it -> Webhook verifies token ->
    Dispatches to `handle_message()` or `handle_voice()` via asyncio loop

Requirements:
- The bot and embedding context must already be initialized in `app_state`.
- This module depends on Flask and the Telegram Python Bot API.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
from asyncio import AbstractEventLoop, run_coroutine_threadsafe
from typing import Any

from flask import request
from helena_bot import app_state
from helena_bot.bot.handlers import handle_message, handle_voice
from helena_bot.utils.groq import transcribe_with_groq
from telegram import Update
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


def register_webhook_route(app: Any) -> None:
    """
    Registers the webhook route on the given Flask app.

    This function defines a dynamic Flask route at `/<token>`, allowing the system
    to receive Telegram webhook updates per bot token. It extracts the `Update` object
    from the request payload, fetches the corresponding application context from memory,
    and schedules asynchronous execution of the proper handler.

    Args:
        app (Any): Flask application instance to attach the route to.

    Side Effects:
        - Updates are dispatched to asyncio event loops per client.
        - Errors are logged if token is invalid or context is missing.

    Raises:
        - None. All exceptions are caught and handled gracefully with logging.
    """

    @app.route("/<token>", methods=["POST"])
    def telegram_webhook(token: str):
        """
        Telegram webhook endpoint for receiving and routing updates.

        Args:
            token (str): Unique bot token used as dynamic URL path for webhook routing.

        Returns:
            str: Plain "OK" message on success.
            tuple[str, int]: Error message and HTTP status code (403 or 500).
        """
        application = app_state.applications.get(token)
        context_data = app_state.client_context.get(token)

        if not application or not context_data:
            logger.warning("Token não reconhecido: %s", token)
            return "Token inválido ou não registrado.", 403

        try:
            update_raw = request.get_json(force=True)
            update: Update | None = Update.de_json(update_raw, application.bot)
            if update is None:
                logger.warning("Update inválido recebido (None).")
                return "Update inválido", 400

            context = CallbackContext(application=application)
            message = getattr(update, "message", None)

            loop = context_data.get("loop")
            if not isinstance(loop, AbstractEventLoop):
                logger.error("Loop de evento ausente ou inválido para token: %s", token)
                return "Loop de evento inválido", 500

            if message:
                if message.text:
                    run_coroutine_threadsafe(
                        handle_message(
                            update,
                            context,
                            context_data["embed_model"],
                            context_data["mongo_collection"],
                        ),
                        loop,
                    )

                elif message.voice:
                    run_coroutine_threadsafe(
                        handle_voice(
                            update,
                            context,
                            context_data["embed_model"],
                            context_data["mongo_collection"],
                            transcribe_with_groq,
                        ),
                        loop,
                    )

            logger.info("Webhook processado com sucesso: %s", token)
            return "OK"

        except (ValueError, TypeError) as e:
            logger.error("Erro ao processar webhook (%s): %s", token, e)
            return "Erro interno", 500
