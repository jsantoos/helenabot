"""
Module: helena_bot.bot.types.setup

Defines strongly typed dictionaries (TypedDicts) used throughout the setup phase
of HelenaBot clients. These typed structures encapsulate resource bundles for
MongoDB, LLM pipelines, vector indexes, and document indexing context.

Provides strict typing and better readability when initializing:
- MongoDB connections
- LLMs and embeddings
- ChromaDB vector stores
- Indexing routines for PDF ingestion

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import TypedDict

from llama_index.core import ServiceContext, VectorStoreIndex
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.memory import BaseMemory
from llama_index.core.vector_stores.types import VectorStore
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient


class MongoResources(TypedDict):
    """
    Represents MongoDB resources initialized for a specific client.

    Attributes:
        client (MongoClient): The low-level MongoDB client instance.
        db (Database): The selected database object.
        collection (Collection): Collection where indexed images are stored.
        metrics (Collection): Collection used for storing metric snapshots.
    """

    client: MongoClient
    db: Database
    collection: Collection
    metrics: Collection


class LLMBundle(TypedDict):
    """
    Represents initialized LLM and embedding components.

    Attributes:
        embed (BaseEmbedding): HuggingFace embedding instance.
        llm (LLM): Groq or compatible LLM instance.
        context (ServiceContext): Service context for LlamaIndex compatibility.
        memory (BaseMemory): Memory buffer for conversation context.
    """

    embed: BaseEmbedding
    llm: LLM
    context: ServiceContext
    memory: BaseMemory


class VectorResources(TypedDict):
    """
    Encapsulates the vector store and index used for retrieval.

    Attributes:
        store (VectorStore): Low-level vector store backend (Chroma).
        index (VectorStoreIndex): LlamaIndex index built from the vector store.
    """

    store: VectorStore
    index: VectorStoreIndex


class SetupIndexingContext(TypedDict):
    """
    Holds all necessary context to determine whether PDFs should be indexed.

    Attributes:
        client_name (str): The client's folder name (used for scoping).
        embed_model (BaseEmbedding): Embedding model used for vectorization.
        vector_store (VectorStore): Store used to persist vectors.
        mongo_collection (Collection): Collection to track already-indexed files.
        documents_path (str): Path to the PDF files to be indexed.
        metrics_collection (Collection): Collection where indexing stats are stored.
    """

    client_name: str
    embed_model: BaseEmbedding
    vector_store: VectorStore
    mongo_collection: Collection
    documents_path: str
    metrics_collection: Collection
