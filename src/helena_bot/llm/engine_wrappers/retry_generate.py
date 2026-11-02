"""
Module: helena_bot.llm.engine_wrappers.retry_generate

Implements a resilient wrapper around LLM chat engines for HelenaBot,
handling transient errors, memory overflows, and API rate limits.

This function is designed to:
- Sanitize and prepare prompts before execution
- Retry on known recoverable failures (e.g., 429 Too Many Requests)
- Reset memory for stateful engines if context overflow occurs
- Provide a user-friendly fallback message in case of total failure

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import asyncio
import logging
from typing import Optional

from helena_bot.utils.text_cleaning import sanitize_prompt, sanitize_text
from telegram.constants import ChatAction

logger = logging.getLogger(__name__)


async def try_generate_response(
    chat_engine,
    prompt: str,
    context=None,
    chat_id: Optional[int] = None,
    max_attempts: int = 3,
) -> str:
    """
    Attempt to generate a response from the LLM engine with built-in retry logic.

    Handles:
    - Prompt sanitization
    - API throttling (HTTP 429)
    - Context overflow and memory resets (e.g., LlamaIndex)
    - Fallback messaging if no valid response is generated

    Args:
        chat_engine: Chat engine object exposing `.chat(prompt)` and optionally `.reset()`.
        prompt (str): Raw user prompt to send to the LLM.
        context: Telegram context object used to send chat actions.
        chat_id (Optional[int]): Chat ID used to send typing indicator during retries.
        max_attempts (int): Number of retries before giving up.

    Returns:
        str: Final response string from the LLM, or a fallback message if all attempts fail.
    """
    prompt = sanitize_prompt(prompt)

    for attempt in range(1, max_attempts + 1):
        try:
            response_obj = chat_engine.chat(prompt)
            logger.debug("LLM response object (attempt %d): %s", attempt, response_obj)

            raw_response = (
                response_obj
                if isinstance(response_obj, str)
                else getattr(response_obj, "response", None)
                or getattr(response_obj, "text", None)
            )

            resposta = sanitize_text(raw_response)
            if resposta:
                return resposta

            logger.warning(
                "Tentativa %d: resposta em branco após sanitização.", attempt
            )

        except Exception as e:  # pylint: disable=broad-exception-caught
            error_message = str(e).lower()
            logger.error("Erro ao tentar gerar resposta (tentativa %d): %s", attempt, e)

            if "429" in error_message or "too many requests" in error_message:
                logger.warning(
                    "Erro 429 - Rate limit. Aguardando antes de tentar novamente."
                )
                if context and chat_id:
                    await context.bot.send_chat_action(
                        chat_id=chat_id, action=ChatAction.TYPING
                    )
                    await asyncio.sleep(5)
                continue

            if "index out of range in self" in error_message:
                logger.warning("Contexto excedido. Tentando resetar memória...")
                if hasattr(chat_engine, "reset"):
                    try:
                        chat_engine.reset()
                        logger.debug("Memória resetada com sucesso.")
                    except (
                        Exception  # pylint: disable=broad-exception-caught
                    ) as reset_err:
                        logger.warning("Falha ao resetar memória: %s", reset_err)

                return (
                    "⚠️ Sua pergunta é muito longa ou o histórico da conversa ficou extenso. "
                    "Tente enviar sua dúvida em partes menores."
                )

    logger.error("Todas as tentativas de resposta falharam.")
    return "⚠️ Não consegui gerar uma resposta. Tente novamente mais tarde."
