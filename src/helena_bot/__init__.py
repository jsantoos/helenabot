"""
Package: helena_bot

HelenaBot is an AI-powered assistant platform for document-based question answering,
integrated with Telegram, Groq APIs, and advanced multimodal embeddings.

Subpackages and modules:
- bot: Telegram bot initialization, handlers, and chat logic
- core: Flask server, bot launcher, webhook and startup routines
- dashboard: (future) visualization and monitoring tools
- llm: Wrappers for Groq LLM and Whisper transcription
- pipeline: PDF processing and semantic indexing pipeline
- utils: Modular utilities organized by domain (e.g., chroma, hash, embedding, storage)
- app_state: Global runtime state and metrics memory
- context_store: In-memory context handler (tokens, sessions, memory)
- document_reader: PDF text/image extractor (used in pipeline)
- embedding_config: Centralized configuration for embedding model and versioning
- logging_config: Global logger initialization for the application

Applies:
- PEP 8: Style Guide for Python Code
- PEP 20: The Zen of Python
- PEP 257: Docstring Conventions
- PEP 484: Type Hinting
"""

__version__ = "0.1.0"
