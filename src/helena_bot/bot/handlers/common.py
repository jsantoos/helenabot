"""
Module: helena_bot.bot.handlers.common

Common handler logic shared across voice and message processing.

This module provides reusable components for:
- Detecting image request intent
- Executing LLM generation with contextual memory
- Suggesting or sending relevant images
- Tracking user interactions and metrics

Used by both `handle_voice` and `handle_message` in a modular and type-safe manner.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
from typing import Any

from helena_bot import app_state
from helena_bot.bot.response.image_sender import send_relevant_images
from helena_bot.bot.retrievel.image_retriever import find_relevant_images
from helena_bot.bot.types.context import (
    ClientContext,
    ImageSuggestionContext,
    SessionContext,
    UserInputContext,
)
from helena_bot.llm.engine_wrappers import try_generate_response
from helena_bot.utils.context import build_context_safe
from helena_bot.utils.metrics import safe_increment
from helena_bot.utils.storage import get_last_interactions, save_interaction
from helena_bot.utils.text_cleaning import sanitize_prompt, sanitize_text
from helena_bot.utils.tokening import count_tokens
from helena_bot.utils.types import InteractionData
from pymongo.collection import Collection
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)
MAX_CONTEXT_QUESTIONS = 3


def _should_send_image_immediately(text: str) -> bool:
    """
    Determines whether the user's input contains explicit keywords indicating an image request.

    Args:
        text (str): The user's input text.

    Returns:
        bool: True if image-related keywords are detected, False otherwise.
    """
    keywords = ["imagem", "figura", "foto", "ilustração", "diagrama"]
    return any(w in text.lower() for w in keywords)


async def _send_relevant_images_if_found(
    update: Update, query: str, embed_model: Any, mongo: Collection
) -> None:
    """
    Finds and sends images relevant to a user query using semantic similarity.

    Args:
        update (Update): Telegram update to reply to.
        query (str): User's input text or question.
        embed_model (Any): Embedding model used to compute similarity.
        mongo (Collection): MongoDB collection where images are indexed.

    Returns:
        None
    """
    images = find_relevant_images(query, embed_model, mongo)
    if images:
        await send_relevant_images(update, images)


async def _generate_llm_response(
    *,
    context: ContextTypes.DEFAULT_TYPE,
    user_input: UserInputContext,
    session: SessionContext,
    client_data: dict[str, Any],
    mongo_collection: Collection,
) -> str:
    """
    Builds context and generates an LLM response for a user's input message.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Telegram context for message sending.
        user_input (UserInputContext): Contains raw and sanitized user text.
        session (SessionContext): Contains chat/session identifiers.
        client_data (dict): Contains client settings, including the configured chat engine.
        mongo_collection (Collection): MongoDB collection for saving interaction history.

    Returns:
        str: The generated response from the LLM.
    """
    chat_id = session["chat_id"]
    token = session["token"]
    transcription = user_input["text"]
    sanitized_text = user_input["sanitized_text"]
    client_name = client_data["client_name"]
    chat_engine = client_data["chat_engine"]

    past = get_last_interactions(
        token, chat_id, mongo_collection, MAX_CONTEXT_QUESTIONS
    )
    prompt = sanitize_prompt(build_context_safe(past, sanitized_text))
    logger.debug("Prompt final (%d tokens).", count_tokens(prompt))

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    resposta = await try_generate_response(chat_engine, prompt, context, chat_id)
    await context.bot.send_message(chat_id=chat_id, text=sanitize_text(resposta))

    _increment_msg_count(client_name)
    interaction: InteractionData = {
        "token": token,
        "chat_id": chat_id,
        "question": transcription,
        "answer": resposta,
    }
    save_interaction(interaction, mongo_collection, client_name)

    return resposta


async def _suggest_image_if_needed(
    *,
    update: Update,
    user_context: ImageSuggestionContext,
    embed_model: Any,
    mongo_collection: Collection,
    client_context: ClientContext,
) -> None:
    """
    Suggests or sends relevant images based on the user input and the generated response.

    If the response references a visual aid, images are sent directly.
    Otherwise, the bot prompts the user with an offer to view related images.

    Args:
        update (Update): Telegram update containing the user's message.
        user_context (ImageSuggestionContext): User input and LLM response.
        embed_model (Any): Embedding model for finding relevant images.
        mongo_collection (Collection): MongoDB collection with image data.
        client_context (ClientContext): Session metadata used to update state and metrics.

    Returns:
        None
    """
    text = user_context["text"]
    resposta = user_context["resposta"]

    client_data = client_context["client_data"]
    context_key = client_context["context_key"]
    client_name = client_context["client_name"]

    relevant_images = find_relevant_images(text, embed_model, mongo_collection)
    if not relevant_images:
        return

    if any(
        p in resposta.lower()
        for p in ["veja a imagem", "imagem correspondente", "a figura mostra"]
    ):
        await send_relevant_images(update, relevant_images)
    else:
        client_data.setdefault("last_questions", {})[context_key] = {
            "text": text,
            "images": relevant_images,
        }

        if update.message:
            await update.message.reply_text(
                "🔍 Encontrei imagens relacionadas. Deseja que eu envie?"
            )
        else:
            logger.warning(
                "update.message está ausente ao tentar enviar sugestão de imagem."
            )

        _increment_msg_count(client_name)


def _increment_msg_count(client_name: str | None) -> None:
    """
    Increments the message count both globally and for a specific client if applicable.

    Args:
        client_name (Optional[str]): Name of the client for targeted metric tracking.

    Returns:
        None
    """
    safe_increment(app_state.metrics, client_name, "messages_sent")
