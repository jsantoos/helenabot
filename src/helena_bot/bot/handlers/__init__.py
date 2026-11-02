"""
Package: helena_bot.bot.handlers

Centralizes the Telegram event handling logic for HelenaBot, separating responsibilities
across message types, command routing, and utility functions.

This package includes:
- Handlers for processing both text and voice messages via LLM-based pipelines.
- Command endpoints for `/ajuda` and `/sobre`, providing user assistance and bot metadata.
- Common logic for managing context state, token control, and prompt preparation.

Exports:
- common: Shared constants and utility functions used across handlers.
- utils: Functions for token counting, sanitization, summarization, and prompt construction.
- message: Main logic for processing textual messages received by the bot.
- voice: Workflow for transcribing and responding to voice messages.
- commands: Dispatch functions for Telegram slash commands like /ajuda and /sobre.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from . import common, utils
from .commands import comando_ajuda, comando_sobre
from .message import handle_message
from .voice import handle_voice

__all__ = [
    "common",
    "utils",
    "comando_ajuda",
    "comando_sobre",
    "handle_message",
    "handle_voice",
    "message",
    "voice",
]
