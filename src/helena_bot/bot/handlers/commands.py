"""
Module: helena_bot.bot.handlers.commands

Implements Telegram command handlers such as /ajuda and /sobre
for HelenaBot.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import logging

from helena_bot import app_state
from helena_bot.utils.metrics import safe_increment
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def comando_ajuda(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # pylint: disable=unused-argument
) -> None:
    """
    Responds to the /ajuda command with usage instructions.

    Args:
        update (Update): Telegram update with the command.
        context (ContextTypes.DEFAULT_TYPE): Telegram context.
    """
    message = update.message
    if message is None:
        logger.warning("update.message is None – cannot reply.")
        return

    await message.reply_text(
        """*Comandos disponíveis:*\n
        /ajuda - Mostra essa ajuda\n
        /sobre - Sobre a assistente\n
        Você também pode enviar mensagens de texto ou áudio para obter respostas.\n""",
        parse_mode="Markdown",
    )
    safe_increment(app_state.metrics, client_name=None, field="messages_sent")
    logger.info("Comando /ajuda respondido.")


async def comando_sobre(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # pylint: disable=unused-argument
) -> None:
    """
    Responds to the /sobre command with bot information.

    Args:
        update (Update): Telegram update with the command.
        context (ContextTypes.DEFAULT_TYPE): Telegram context.
    """
    message = update.message
    if message is None:
        logger.warning("update.message is None – cannot reply.")
        return

    await message.reply_text(
        """Eu sou a *HelenaBot*, uma assistente de IA especializada
        em instrumentação cirúrgica em ortopedia.\n
        Desenvolvida por *João Santos*, com o apoio de *Luís Serrante* e *Felipe Tinnoco*.""",
        parse_mode="Markdown",
    )
    safe_increment(app_state.metrics, client_name=None, field="messages_sent")
    logger.info("Comando /sobre respondido.")
