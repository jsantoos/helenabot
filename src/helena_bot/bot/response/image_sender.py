"""
Module: helena_bot.bot.response.image_sender

Provides internal logic for sending relevant images to users via Telegram.
Used by the HelenaBot message and voice handlers when visual context is detected.

Responsibilities:
- Decodes images from MongoDB format.
- Sends up to 5 relevant images per user query.
- Tracks message and image delivery metrics (global and per client).

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import base64
import io
import logging
from typing import Any, Optional

from bson import Binary
from helena_bot import app_state
from helena_bot.utils.metrics import safe_increment
from helena_bot.utils.storage import save_metrics
from telegram import Message, Update
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


def _prepare_image_bytes(img: dict) -> Optional[bytes]:
    """
    Extracts and converts the image byte content from a MongoDB document.

    This function handles image storage formats that may come from BSON Binary
    or serialized base64 representations.

    Args:
        img (dict): MongoDB document containing the image data under the 'image_bytes' key.

    Returns:
        Optional[bytes]: The decoded image bytes, or None if the format is unsupported or invalid.
    """
    image_bytes = img.get("image_bytes")

    if isinstance(image_bytes, dict) and "$binary" in image_bytes:
        return base64.b64decode(image_bytes["$binary"]["base64"])
    if isinstance(image_bytes, Binary):
        return bytes(image_bytes)
    if isinstance(image_bytes, bytes):
        return image_bytes

    return None


async def _send_single_image(message: Message, name: str, image_bytes: bytes) -> bool:
    """
    Sends a single image to the user via Telegram.

    Builds a file-like stream from the raw image bytes and attaches a caption with the image name.
    Catches and logs errors such as Telegram API issues or invalid image formatting.

    Args:
        message (Message): Telegram message object to reply to.
        name (str): Caption for the image.
        image_bytes (bytes): Byte content of the image.

    Returns:
        bool: True if the image was successfully sent, False otherwise.
    """
    try:
        image_stream = io.BytesIO(image_bytes)
        image_stream.seek(0)
        await message.reply_photo(photo=image_stream, caption=name)
        return True
    except (ValueError, TypeError, TelegramError) as e:
        logger.error("Falha ao enviar imagem '%s': %s", name, e)
        return False


async def _notify_user_no_images(message: Message, client_name: Optional[str]) -> None:
    """
    Notifies the user that no relevant images were found and updates message metrics.

    Args:
        message (Message): Telegram message object to reply to.
        client_name (Optional[str]): Name of the current client, if available, to update per-client metrics.
    """
    await message.reply_text("⚠️ Nenhuma imagem relevante encontrada.")
    safe_increment(app_state.metrics, client_name, "messages_sent")


async def _notify_user_images_sent(message: Message) -> None:
    """
    Sends a confirmation message to the user after image delivery.

    Args:
        message (Message): Telegram message object to reply to.
    """
    await message.reply_text(
        "✅ Imagens enviadas com sucesso! Tem algo mais que eu possa te ajudar?"
    )


def _increment_message_metric(client_name: Optional[str]) -> None:
    """
    Increments the count of messages sent globally and, if applicable, per client.

    This function should be called whenever a message (text or image) is successfully sent
    to a user to ensure both global and client-specific metrics stay up-to-date.

    Args:
        client_name (Optional[str]): The identifier of the client for scoped metrics.
                                      If None, only the global counter is updated.
    """
    safe_increment(app_state.metrics, client_name, "messages_sent")


def _finalize_metrics(
    token: str,
    client_name: Optional[str],
    context_key: str,
    count_sent: int,
) -> None:
    """
    Updates message and image delivery metrics, clears image suggestion context,
    and persists the current metrics to MongoDB.

    Args:
        token (str): The Telegram bot token used as identifier in the application context.
        client_name (Optional[str]): The current client identifier.
        context_key (str): The unique context key based on token and chat_id.
        count_sent (int): The number of images successfully sent to the user.
    """
    for _ in range(count_sent):
        safe_increment(app_state.metrics, client_name, "images_sent")
    safe_increment(app_state.metrics, client_name, "messages_sent")

    last_q = app_state.client_context.get(token, {}).get("last_questions", {})
    if context_key in last_q:
        logger.debug("Removendo contexto salvo: %s", context_key)
        last_q.pop(context_key)

    metrics_collection = app_state.client_context.get(token, {}).get(
        "metrics_collection"
    )
    if metrics_collection is not None:
        save_metrics(app_state.metrics, metrics_collection)


async def send_relevant_images(
    update: Update, images: list[dict[str, Any]], client_name: Optional[str] = None
) -> None:
    """
    Sends image documents to the user via Telegram and updates system metrics.

    Args:
        update (Update): Telegram update object containing the message.
        images (list[dict]): List of MongoDB image documents. Each must contain:
            - 'name' (str): Image filename or identifier.
            - 'image_bytes' (bytes | Binary | dict with base64 string)
        client_name (Optional[str]): Optional client name for per-client metrics.
    """
    token = update.get_bot().token if hasattr(update, "get_bot") else "unknown"
    client_data = app_state.client_context.get(token, {})

    if not client_name:
        client_name = client_data.get("client_name")

    message = update.message
    if message is None:
        logger.warning("update.message is None - cannot reply.")
        return

    chat = update.effective_chat
    if chat is None:
        logger.warning("effective_chat is None – aborting operation.")
        return
    chat_id = chat.id
    context_key = f"{token}:{chat_id}"

    if not images:
        await _notify_user_no_images(message, client_name)
        return

    await message.reply_text("📎 Enviando imagens relevantes...")
    _increment_message_metric(client_name)

    sent = set()
    count_sent = 0

    for img in images[:5]:
        name = img.get("name")
        if not name or name in sent:
            continue

        image_bytes = _prepare_image_bytes(img)
        if image_bytes is None:
            logger.warning("Bytes inválidos para imagem '%s'", name)
            continue

        if await _send_single_image(message, name, image_bytes):
            sent.add(name)
            count_sent += 1

    await _notify_user_images_sent(message)
    _finalize_metrics(token, client_name, context_key, count_sent)
