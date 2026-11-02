"""
Package: helena_bot.utils.groq

Handles integration with Groq's API services, such as audio transcription via Whisper.

This package provides wrappers to interface with Groq's HTTP endpoints, handling
authentication, request formatting, and error resilience. It is primarily used
for converting Telegram voice messages into transcribed text during message handling.

Exposed:
- transcribe_with_groq: Sends an audio file to the Groq Whisper API and returns transcribed text.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .groq import transcribe_with_groq

__all__ = ["transcribe_with_groq"]
