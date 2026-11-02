"""
Package: helena_bot.bot

Defines the setup logic and initialization routines for client-specific Telegram bots
within the HelenaBot system. This package acts as the primary entry point for configuring
the embedding pipeline, retrieval engine, prompt system, and runtime context bindings.

Responsibilities:
- Loads client-specific system prompts from `clients/<client>/system_prompt.txt`.
- Initializes the full LLM context, memory, vector store, and embedding models.
- Registers message and voice handlers for the Telegram bot via `setup_bot`.

Exports:
- setup_bot: Initializes and starts the bot for a specified client, preparing all required subsystems.

Context:
This module is invoked during bot startup, typically from `core/bot_launcher.py`
or `main.py`, and ensures each client is configured with isolated resources and state.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .setup import setup_bot

__all__ = ["setup_bot"]
