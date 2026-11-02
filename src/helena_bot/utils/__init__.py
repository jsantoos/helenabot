"""
Package: helena_bot.utils

Utility package for shared functionality across the HelenaBot system.

This package includes specialized utility submodules used throughout the
bot, embedding pipeline, and storage layers.

Subpackages:
- chroma: ChromaDB vector operations and metadata management
- context: Conversation context builders and session utilities
- db: Generic database connectors and abstractions
- embedding: Text embedding strategies and error handling
- groq: Integration utilities for Groq LLMs and Whisper
- hash: Hashing helpers for embeddings and document tracking
- image: Image validation, OCR, and blank image detection
- metrics: Runtime metric counters and safe operations
- path: File and directory path resolution helpers
- storage: MongoDB persistence and I/O operations
- summarization: Text summarization utilities
- text_cleaning: Preprocessing and sanitization for user inputs and PDF content
- tokening: Tokenization, splitting and SentenceSplitter helpers
- types: Shared TypedDicts used across multiple modules

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""
