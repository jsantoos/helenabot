"""
Module: helena_bot.bot.handlers.message

Handles incoming Telegram text messages, including:
- Input validation and sanitization
- Client session context loading
- Response generation using LLM
- Explicit or contextual image suggestion and delivery
- Metric tracking and persistence

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
from typing import Any

from helena_bot import app_state
from helena_bot.bot.handlers.common import (
    _generate_llm_response,
    _increment_msg_count,
    _send_relevant_images_if_found,
    _should_send_image_immediately,
    _suggest_image_if_needed,
)
from helena_bot.bot.handlers.metrics_persistence import _persist_metrics_if_available
from helena_bot.bot.handlers.utils import _resolve_token, _update_basic_metrics
from helena_bot.bot.response import send_relevant_images
from helena_bot.bot.types import SessionContext, UserInputContext
from helena_bot.utils.summarization import summarize_text
from helena_bot.utils.text_cleaning import MAX_TOTAL_TOKENS, sanitize_text
from helena_bot.utils.tokening import count_tokens
from pymongo.collection import Collection
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    embed_model: Any,
    mongo_collection: Collection,
) -> None:
    """
    Handles an incoming Telegram text message by:
    - Validating and sanitizing input
    - Managing context and metrics
    - Generating LLM response
    - Sending or suggesting relevant images

    Args:
        update (Update): Telegram update containing the message.
        context (ContextTypes.DEFAULT_TYPE): Telegram callback context.
        embed_model (Any): Model used for semantic search.
        mongo_collection (Collection): MongoDB collection to persist interactions.

    Returns:
        None
    """
    if (
        update.message is None
        or not update.effective_chat
        or not update.message.text
        or not update.message.text.strip()
    ):
        await _reply_invalid_message(update.message)
        return

    raw_token = _resolve_token(context, update)
    if raw_token is None:
        logger.warning("Token do bot não identificado.")
        return

    session: SessionContext = {
        "chat_id": update.effective_chat.id,
        "token": raw_token,
    }

    context_key = f"{session['token']}:{session['chat_id']}"
    client_context = app_state.client_context.get(session["token"], {})
    client_name = client_context.get("client_name")
    if client_name is None:
        logger.warning("Client name não definido para token %s", session["token"])
        return

    text_message = update.message.text
    sanitized_text = sanitize_text(text_message)

    if count_tokens(sanitized_text) > MAX_TOTAL_TOKENS:
        logger.warning("Mensagem longa demais. Resumindo...")
        sanitized_text = summarize_text(sanitized_text, max_tokens=300)

    user_input: UserInputContext = {
        "text": text_message,
        "sanitized_text": sanitized_text,
    }

    _update_basic_metrics(session["chat_id"], client_name)

    if _should_send_image_immediately(user_input["text"]):
        await _send_relevant_images_if_found(
            update, text_message, embed_model, mongo_collection
        )
        logger.info(
            "⏺ Persistindo métricas após envio direto de imagem (%s)", client_name
        )
        _persist_metrics_if_available(client_context, client_name)
        return

    if _is_confirmation_reply(user_input["text"]):
        await _handle_confirmation_reply(
            update, client_context, context_key, client_name
        )
        logger.info(
            "⏺ Persistindo métricas após resposta de confirmação (%s)", client_name
        )
        _persist_metrics_if_available(client_context, client_name)
        return

    try:
        llm_response = await _generate_llm_response(
            context=context,
            user_input=user_input,
            session=session,
            client_data=client_context,
            mongo_collection=mongo_collection,
        )
    except RuntimeError as err:
        logger.error("Erro ao gerar resposta: %s", err)
        await update.message.reply_text(
            "📏 A mensagem enviada está muito longa ou complexa. "
            "Tente reescrever de forma mais direta ou dividir em partes."
        )
        logger.info("⏺ Persistindo métricas após erro de LLM (%s)", client_name)
        _persist_metrics_if_available(client_context, client_name)
        return

    await _suggest_image_if_needed(
        update=update,
        user_context={
            "text": text_message,
            "resposta": llm_response,
        },
        embed_model=embed_model,
        mongo_collection=mongo_collection,
        client_context={
            "client_data": client_context,
            "context_key": context_key,
            "client_name": client_name,
        },
    )

    logger.info(
        "⏺ Persistindo métricas após resposta do LLM e sugestão de imagem (%s)",
        client_name,
    )
    _persist_metrics_if_available(client_context, client_name)


def _is_confirmation_reply(text: str) -> bool:
    """
    Checks if the user's message confirms a previously suggested image.

    Args:
        text (str): Input text from the user.

    Returns:
        bool: True if confirmation keywords are present, False otherwise.
    """
    return text.lower() in ["sim", "pode enviar", "quero ver", "sim, por favor"]


async def _handle_confirmation_reply(
    update: Update,
    client_data: dict,
    context_key: str,
    client_name: str,
) -> None:
    """
    Handles user confirmation to send previously suggested images.

    Args:
        update (Update): Telegram update from the user.
        client_data (dict): Full client context including image memory.
        context_key (str): Unique session identifier.
        client_name (str): Name of the client for metric tracking.

    Returns:
        None
    """
    last_questions = client_data.get("last_questions", {})
    context_data = last_questions.get(context_key)

    if context_data and context_data.get("images"):
        await send_relevant_images(update, context_data["images"])
        last_questions.pop(context_key, None)
    else:
        if update.message:
            await update.message.reply_text("🤖 Como posso ajudar?")
        else:
            logger.warning(
                "update.message está ausente ao tentar responder confirmação."
            )

    _increment_msg_count(client_name)


async def _reply_invalid_message(message: Any) -> None:
    """
    Replies with a standard warning if the message is invalid.

    Args:
        message (Any): Telegram message object (may be None).

    Returns:
        None
    """
    if message:
        await message.reply_text("⚠️ Por favor, envie uma mensagem de texto ou áudio.")
    else:
        logger.warning("update.message ou chat vazio.")
