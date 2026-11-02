"""
Module: helena_bot.bot.setup

Responsible for initializing a Telegram bot instance for a specific client,
including all resources like MongoDB, embedding models, vector index, and chat engine.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import asyncio
import logging
import os
from typing import Any

from dotenv import load_dotenv
from helena_bot import app_state
from helena_bot.bot.handlers import (
    comando_ajuda,
    comando_sobre,
    handle_message,
    handle_voice,
)
from helena_bot.bot.setup_utils import (
    _init_chat_engine,
    _init_embedding_and_llm,
    _init_mongo,
    _init_vector_index,
    _maybe_index_documents,
)
from helena_bot.utils.groq import transcribe_with_groq
from helena_bot.utils.path import get_env_path, get_prompt_path
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logger = logging.getLogger(__name__)


def load_system_prompt(prompt_path: str) -> str:
    """
    Loads the system prompt text from a given file path. This prompt is used to instruct
    the LLM on behavior and personality for the client.

    If the file does not exist, returns a default fallback prompt.

    Args:
        prompt_path (str): Absolute or relative path to the system_prompt.txt file.

    Returns:
        str: Prompt text to be used in LLM chat engine initialization.
    """
    if os.path.exists(prompt_path):
        logger.info("✅ Prompt localizado em: %s", prompt_path)
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    logger.warning(
        "⚠️ system_prompt.txt não encontrado em '%s'. Usando prompt padrão.", prompt_path
    )
    return "Você é a HelenaBot, uma assistente de IA. Seja clara, útil e assertiva."


async def setup_bot(client_name: str, config: dict[str, Any]) -> None:
    """
    Set up the full bot context, database, index, embeddings, and handlers.

    Args:
        client_name (str): Client folder name (used for indexing, MongoDB, and prompt path).
        config (dict[str, Any]): Client-specific configuration. Must include:
            - env: dict with keys TELEGRAM_TOKEN, MONGO_URL, GROQ_API_KEY
            - docs_path (str): Path to PDF documents
            - dpi (int, optional): PDF rendering DPI. Defaults to 200.
            - max_pages (int, optional): Limit of PDF pages to process. If None, processes all.
    """

    logger.info("🔧 Inicializando bot para cliente: %s", client_name)

    required_env_keys = ["TELEGRAM_TOKEN", "MONGO_URL", "GROQ_API_KEY"]
    missing_keys = [k for k in required_env_keys if k not in config.get("env", {})]
    if missing_keys:
        raise KeyError(
            f"Campos ausentes no bloco 'env' da configuração de '{client_name}': {missing_keys}"
        )

    token = config["env"].get("TELEGRAM_TOKEN")
    mongo_url = config["env"].get("MONGO_URL")
    groq_api_key = config["env"].get("GROQ_API_KEY")
    documents_path = config.get("docs_path")
    dpi = 200

    try:
        max_pages = int(config["env"].get("CLIENT_MAX_PAGES") or 0) or float("inf")
    except (ValueError, TypeError):
        max_pages = float("inf")

    load_dotenv(get_env_path(client_name))
    system_prompt = load_system_prompt(get_prompt_path(client_name))

    mongo = _init_mongo(mongo_url, client_name)
    llm_bundle = _init_embedding_and_llm(groq_api_key)
    vector = _init_vector_index(client_name, llm_bundle["context"])

    chat_engine = _init_chat_engine(
        vector["index"], llm_bundle["llm"], llm_bundle["memory"], system_prompt
    )

    _maybe_index_documents(
        {
            "client_name": client_name,
            "embed_model": llm_bundle["embed"],
            "vector_store": vector["store"],
            "mongo_collection": mongo["collection"],
            "documents_path": documents_path,
            "metrics_collection": mongo["metrics"],
            "dpi": dpi,
            "max_pages": max_pages,
        }
    )

    app_state.client_context.setdefault(token, {}).update(
        {
            "client_name": client_name,
            "llm": llm_bundle["llm"],
            "memory": llm_bundle["memory"],
            "chat_engine": chat_engine,
            "index": vector["index"],
            "system_prompt": system_prompt,
            "mongo_client": mongo["client"],
            "mongo_db": mongo["db"],
            "mongo_collection": mongo["collection"],
            "metrics_collection": mongo["metrics"],
            "embed_model": llm_bundle["embed"],
            "loop": asyncio.get_event_loop(),
            "last_questions": {},
        }
    )

    app_state.metrics["per_client"].setdefault(
        client_name,
        {
            "connected_users": set(),
            "messages_sent": 0,
            "images_sent": 0,
            "interactions": 0,
            "embeddings_total": 0,
            "images_saved": 0,
            "pdfs_processed": 0,
        },
    )

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("ajuda", comando_ajuda))
    application.add_handler(CommandHandler("sobre", comando_sobre))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            lambda u, c: handle_message(u, c, llm_bundle["embed"], mongo["collection"]),
        )
    )
    application.add_handler(
        MessageHandler(
            filters.VOICE,
            lambda u, c: handle_voice(
                u, c, llm_bundle["embed"], mongo["collection"], transcribe_with_groq
            ),
        )
    )

    app_state.applications[token] = application

    await application.initialize()
    await application.start()
    logger.info("✅ Bot '%s' iniciado com sucesso.", client_name)
