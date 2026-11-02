"""
Module: helena_bot.utils.mongo.interaction_log

Handles storage and retrieval of user interactions (questions and responses)
in MongoDB for HelenaBot. This enables persistent memory for contextual conversations,
analytics, and debugging.

This module separates user interaction tracking into its own domain, independent
from embeddings or metrics. All interactions are namespaced per client for clarity.

Responsibilities:
- Persist question-answer pairs into `interactions_<client>` collections
- Retrieve the latest N interactions for context reconstruction

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

import datetime
import logging
from typing import List, Optional

from helena_bot.utils.types import InteractionData
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


def save_interaction(
    data: InteractionData,
    mongo_collection: Collection,
    client_name: Optional[str] = None,
) -> None:
    """
    Persist a structured user interaction in the appropriate MongoDB collection.

    Interactions are saved with a timestamp and grouped under collections named
    `interactions_<client>`, which allows for historical context tracking and debugging
    across isolated deployments of HelenaBot.

    Args:
        data (InteractionData): Dictionary containing token, chat ID, question, and response.
        mongo_collection (Collection): MongoDB collection (any) used to resolve the target database.
        client_name (Optional[str]): Optional client name to namespace the collection.

    Returns:
        None
    """
    collection_name = f"interactions_{client_name or 'default'}"
    collection = mongo_collection.database[collection_name]
    interaction = {
        **data,
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    }

    try:
        collection.insert_one(interaction)
        logger.info("[DB] ✅ Interaction saved in %s", collection_name)
    except PyMongoError as e:
        logger.error("[DB] ❌ Failed to save interaction: %s", e)


def get_last_interactions(
    token: str,
    chat_id: int,
    mongo_collection: Collection,
    n: int = 3,
) -> List[dict]:
    """
    Retrieve the last N recorded question/response pairs for a given user.

    This is typically used to reconstruct context in LLM prompts, enabling
    the bot to generate coherent responses based on recent conversation history.

    Args:
        token (str): Telegram bot token identifying the client instance.
        chat_id (int): Unique user chat ID.
        mongo_collection (Collection): MongoDB collection to query from.
        n (int): Number of most recent interactions to return.

    Returns:
        List[dict]: A list of interaction dictionaries, most recent last.
    """
    doc = mongo_collection.find_one({"token": token, "chat_id": chat_id})
    return doc.get("history", [])[-n:] if doc and "history" in doc else []
