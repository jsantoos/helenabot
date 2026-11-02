"""
Module: app_state

Defines shared global state across all HelenaBot instances.

Responsibilities:
- Holds references to embedding models, chat engine, memory, and vector index.
- Maintains per-client and global interaction metrics.
- Provides shared MongoDB client, database, and collection references.
- Stores Telegram `Application` instances and client-specific contexts.

Applies:
- PEP 8: Style guide for Python code.
- PEP 20: Zen of Python.
- PEP 257: Docstring conventions.
- PEP 484: Type hints.
"""

from collections import defaultdict
from typing import Any, Optional

from llama_index.core import VectorStoreIndex
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.memory import ChatSummaryMemoryBuffer
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from telegram.ext import Application

# Global state shared across bots
llm: Optional[Any] = None
memory: Optional[ChatSummaryMemoryBuffer] = None
chat_engine: Optional[BaseChatEngine] = None
interaction_counter: int = 0
index: Optional[VectorStoreIndex] = None
system_prompt: str = ""

# Mongo and application management
mongo_client: Optional[MongoClient] = None
mongo_db: Optional[Database] = None
metrics_collection: Optional[Collection] = None
applications: dict[str, Application] = {}

# Client-specific contextual storage
client_context: dict[str, dict] = {}

# Metrics storage
metrics = {
    "global": {
        "connected_users": set(),
        "messages_sent": 0,
        "images_sent": 0,
        "interactions": 0,
    },
    "per_client": defaultdict(
        lambda: {
            "connected_users": set(),
            "messages_sent": 0,
            "images_sent": 0,
            "interactions": 0,
            "embeddings_total": 0,
            "images_saved": 0,
            "pdfs_processed": 0,
        }
    ),
}
