"""
Module: helena_bot.bot.retrieval

Contains logic for retrieving semantically relevant documents, images or embeddings
for the HelenaBot system.

Exposes:
- find_relevant_images: Public function for searching relevant images from MongoDB.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from .image_retriever import find_relevant_images

__all__ = ["find_relevant_images"]
