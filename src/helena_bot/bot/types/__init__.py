"""
Module: helena_bot.bot.types

Centralizes all TypedDict definitions used in the HelenaBot system to ensure
consistent typing and interoperability across handlers, setup routines,
and embedding workflows.

Exposes:
- ClientContext: Runtime metadata associated with the client session.
- ImageSuggestionContext: Data structure for storing image suggestion state.
- SessionContext: Combined metadata about chat, token, and runtime.
- UserInputContext: Sanitized and raw user input data (text or voice).
- SetupIndexingContext: Configuration dictionary used to index PDFs.
- LLMBundle: Resources returned when initializing embedding + LLM context.
- MongoResources: MongoDB client, collections, and metric collection.
- VectorResources: Vector store and index references for retrieval.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .context import (
    ClientContext,
    ImageSuggestionContext,
    SessionContext,
    UserInputContext,
)
from .setup import LLMBundle, MongoResources, SetupIndexingContext, VectorResources

__all__ = [
    "ClientContext",
    "ImageSuggestionContext",
    "SessionContext",
    "UserInputContext",
    "SetupIndexingContext",
    "LLMBundle",
    "MongoResources",
    "VectorResources",
]
