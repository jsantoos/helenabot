"""
Module: helena_bot.bot.handlers.voice

Handles incoming voice messages from Telegram users:
- Downloads and transcribes audio
- Builds conversational context
- Invokes LLM response
- Optionally sends or suggests relevant images

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging
import subprocess
import tempfile
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
from helena_bot.bot.types import SessionContext, UserInputContext
from helena_bot.utils.summarization import summarize_text
from helena_bot.utils.text_cleaning import MAX_TOTAL_TOKENS, sanitize_text
from helena_bot.utils.tokening import count_tokens
from pymongo.collection import Collection
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_voice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    embed_model: Any,
    mongo_collection: Collection,
    transcribe_audio_to_text,
) -> None:
    """
    Handles an incoming Telegram voice message by transcribing, interpreting,
    generating a response via LLM, and optionally sending or suggesting relevant images.

    Args:
        update (Update): Telegram update containing the voice message.
        context (ContextTypes.DEFAULT_TYPE): Telegram callback context.
        embed_model (Any): Embedding model for semantic similarity search.
        mongo_collection (Collection): MongoDB collection for interactions.
        transcribe_audio_to_text (Callable): Function to transcribe local audio file to text.

    Returns:
        None
    """
    if not update.message or not update.effective_chat or not update.message.voice:
        await _reply_invalid_voice(update.message)
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

    transcription = await _transcribe_voice(update, transcribe_audio_to_text)
    if not transcription:
        await update.message.reply_text("⚠️ Não consegui transcrever o áudio.")
        _increment_msg_count(client_name)
        return

    sanitized_text = sanitize_text(transcription)
    if count_tokens(sanitized_text) > MAX_TOTAL_TOKENS:
        logger.warning("Transcrição longa. Resumindo...")
        sanitized_text = summarize_text(sanitized_text, max_tokens=300)

    user_input: UserInputContext = {
        "text": transcription,
        "sanitized_text": sanitized_text,
    }

    _update_basic_metrics(session["chat_id"], client_name)

    if _should_send_image_immediately(transcription):
        await _send_relevant_images_if_found(
            update, transcription, embed_model, mongo_collection
        )
        logger.info(
            "⏺ Persistindo métricas após envio direto de imagem (%s)", client_name
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
            "📏 A transcrição está muito longa ou complexa. "
            "Tente resumir ou dividi-la em partes menores."
        )
        logger.info("⏺ Persistindo métricas após erro de LLM (%s)", client_name)
        _persist_metrics_if_available(client_context, client_name)
        return

    await _suggest_image_if_needed(
        update=update,
        user_context={
            "text": transcription,
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


async def _transcribe_voice(update: Update, transcribe_fn) -> str:
    """
    Downloads and transcribes the voice file using the provided transcription function.

    Args:
        update (Update): Telegram update containing the voice.
        transcribe_fn (Callable): Async or sync function to transcribe audio (e.g., Whisper).

    Returns:
        str: The transcribed text, or empty string if transcription fails.
    """
    try:
        if not update.message or not update.message.voice:
            logger.warning("Mensagem ou voz ausente ao tentar transcrever.")
            return ""

        file = update.message.voice
        tg_file = await file.get_file()  # ✅ await obrigatório
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            await tg_file.download_to_drive(tmp.name)  # ✅ await necessário
            ogg_path = tmp.name

        wav_path = ogg_path.replace(".ogg", ".wav")
        subprocess.run(["ffmpeg", "-i", ogg_path, wav_path], check=True)
        return transcribe_fn(wav_path).strip()
    except (
        TelegramError,
        IOError,
        OSError,
        ValueError,
        subprocess.CalledProcessError,
    ) as e:
        logger.warning("Erro ao transcrever áudio: %s", e)
        return ""


async def _reply_invalid_voice(message: Any) -> None:
    """
    Sends a standard message to the user if the voice input is missing or invalid.

    Args:
        message (Any): The Telegram message object (may be None).

    Returns:
        None
    """
    if message:
        await message.reply_text("⚠️ Nenhuma mensagem de voz encontrada.")
    else:
        logger.warning("update.message ou chat vazio.")
