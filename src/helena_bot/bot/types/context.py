"""
Module: helena_bot.bot.types.context

TypedDict definitions for structured context exchange across Telegram bot handlers.

These types are used to standardize and validate the data passed between functions
that handle Telegram updates, user input, client state, and AI-generated responses.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import Any, TypedDict


class SessionContext(TypedDict):
    """
    Represents contextual metadata for a Telegram chat session.

    Attributes:
        token (str): The Telegram bot token handling the request.
        chat_id (int): Unique Telegram chat ID identifying the conversation.
    """

    token: str
    chat_id: int


class ImageSuggestionContext(TypedDict):
    """
    Represents the input and response pair used to determine if images should be suggested.

    Attributes:
        text (str): User input or transcribed message.
        resposta (str): The LLM-generated response.
    """

    text: str
    resposta: str


class UserInputContext(TypedDict):
    """
    Represents the cleaned and raw form of the user’s input.

    Attributes:
        text (str): The original message sent by the user.
        sanitized_text (str): The cleaned and possibly summarized version of the text.
    """

    text: str
    sanitized_text: str


class ClientContext(TypedDict):
    """
    Contextual information about the current client session.

    Attributes:
        client_data (dict[str, Any]): Full client-specific settings and memory state.
        context_key (str): Unique key for the current session (bot token + chat ID).
        client_name (str): Name of the client associated with this session.
    """

    client_data: dict[str, Any]
    context_key: str
    client_name: str
